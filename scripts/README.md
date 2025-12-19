脚本: count_quoted_chars.py

用途:
- 统计指定目录下（递归）所有 `.yml` / `.yaml` 文件中，被单引号或双引号包裹的字符串的字符数（支持中英文混合）。

快速开始:
```bash
python scripts/count_quoted_chars.py --path localisation/simp_chinese
```

选项:
- `--path` / `-p`: 要扫描的目录，默认为当前目录。
- `--json`: 输出 JSON 格式的机器可读结果。
 - `--only-chinese`: 只统计被引号包裹字符串中的中文字符数（仅中文计数）。

说明:
- 脚本通过正则在文件文本中查找单引号或双引号包裹的片段，简单处理转义引号和反斜杠。
- 对非常复杂的 YAML 引用场景（例如多行引用、特殊转义）可能不是 100% 精确，但对常见本地化 yml 文件效果良好。
