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
    pattern = re.compile(r"(?s)\"((?:\\.|[^\"\\])*)\"|'((?:\\.|[^\\'\\])*)'")
    results = []
    for m in pattern.finditer(text):
        s = m.group(1) if m.group(1) is not None else m.group(2)
        # 简单还原常见的转义序列，便于更准确计数
        s = s.replace('\\"', '"').replace("\\'", "'").replace('\\\\', '\\')
        results.append(s)
    return results


def is_chinese_char(ch: str) -> bool:
    # 检查字符是否为中文（覆盖常用的 CJK 范围）
    cp = ord(ch)
    return (
        0x4E00 <= cp <= 0x9FFF or
        0x3400 <= cp <= 0x4DBF or
        0x20000 <= cp <= 0x2A6DF or
        0x2A700 <= cp <= 0x2B73F or
        0x2B740 <= cp <= 0x2B81F or
        0x2B820 <= cp <= 0x2CEAF or
        0xF900 <= cp <= 0xFAFF or
        0x2F800 <= cp <= 0x2FA1F
    )


def scan_directory(path, only_chinese=False):
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
                if only_chinese:
                    count_chars = sum(sum(1 for ch in s if is_chinese_char(ch)) for s in strs)
                else:
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
    p.add_argument('--only-chinese', action='store_true', help='只统计被引号包裹字符串中的中文字符数')
    args = p.parse_args()

    if not os.path.isdir(args.path):
        print('指定路径不是目录: ' + args.path, file=sys.stderr)
        sys.exit(2)

    res = scan_directory(args.path, only_chinese=args.only_chinese)

    if args.json:
        print(json.dumps(res, ensure_ascii=False, indent=2))
        return

    print('扫描目录:', args.path)
    print('找到 YAML 文件数:', len(res['files']))
    print('找到字符串段数:', res['total_strings'])
    if args.only_chinese:
        print('总中文字符数:', res['total_chars'])
    else:
        print('总字符数:', res['total_chars'])
    print('\n每个文件统计:')
    for f in sorted(res['files'], key=lambda x: (-x['chars'], x['file'])):
        if args.only_chinese:
            print(f"{f['file']}: 中文字符数={f['chars']}, 字符串段数={f['strings']}")
        else:
            print(f"{f['file']}: 字符数={f['chars']}, 字符串段数={f['strings']}")


if __name__ == '__main__':
    main()
