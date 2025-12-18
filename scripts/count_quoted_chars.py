#!/usr/bin/env python3
"""
统计指定目录下（递归）所有 .yml/.yaml 文件中，被单引号或双引号包裹的字符串的字符数（支持中英文混合）。

用法示例:
  python scripts/count_quoted_chars.py --path localisation/simp_chinese

输出包含每个文件的字符串数量与字符总数，以及总体汇总。
"""
import argparse
import os
import re
import json
import sys


def find_quoted_strings(text):
    # 匹配双引号或单引号内的字符串，支持转义引号和跨行（DOTALL）
    pattern = re.compile(r'(?s)"((?:\\.|[^"\\])*)"|\'((?:\\.|[^\\'\\])*)\'')
    results = []
    for m in pattern.finditer(text):
        s = m.group(1) if m.group(1) is not None else m.group(2)
        # 简单还原常见的转义序列，便于更准确计数
        s = s.replace('\\"', '"').replace("\\'", "'").replace('\\\\', '\\')
        results.append(s)
    return results


def scan_directory(path):
    per_file = []
    total_strings = 0
    total_chars = 0
    for root, dirs, files in os.walk(path):
        for fn in files:
            if fn.lower().endswith(('.yml', '.yaml')):
                fp = os.path.join(root, fn)
                try:
                    with open(fp, 'r', encoding='utf-8', errors='replace') as f:
                        text = f.read()
                except Exception as e:
                    print(f"无法读取文件 {fp}: {e}", file=sys.stderr)
                    continue
                strs = find_quoted_strings(text)
                count_strings = len(strs)
                count_chars = sum(len(s) for s in strs)
                per_file.append({
                    'file': os.path.relpath(fp),
                    'strings': count_strings,
                    'chars': count_chars
                })
                total_strings += count_strings
                total_chars += count_chars
    return {
        'files': per_file,
        'total_strings': total_strings,
        'total_chars': total_chars
    }


def main():
    p = argparse.ArgumentParser(description='Count characters inside quoted strings in YAML files')
    p.add_argument('--path', '-p', default='.', help='Directory path to scan (recursive)')
    p.add_argument('--json', action='store_true', help='Output machine-readable JSON')
    args = p.parse_args()

    if not os.path.isdir(args.path):
        print('指定路径不是目录: ' + args.path, file=sys.stderr)
        sys.exit(2)

    res = scan_directory(args.path)

    if args.json:
        print(json.dumps(res, ensure_ascii=False, indent=2))
        return

    print('扫描目录:', args.path)
    print('找到 YAML 文件数:', len(res['files']))
    print('找到字符串段数:', res['total_strings'])
    print('总字符数:', res['total_chars'])
    print('\n每个文件统计:')
    for f in sorted(res['files'], key=lambda x: (-x['chars'], x['file'])):
        print(f"{f['file']}: 字符数={f['chars']}, 字符串段数={f['strings']}")


if __name__ == '__main__':
    main()
