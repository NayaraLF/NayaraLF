#!/usr/bin/env python3
import os
from collections import defaultdict

# mapping common extensions to language names
EXT_LANG = {
    '.py': 'Python',
    '.js': 'JavaScript',
    '.ts': 'TypeScript',
    '.jsx': 'JavaScript',
    '.tsx': 'TypeScript',
    '.html': 'HTML',
    '.css': 'CSS',
    '.scss': 'CSS',
    '.json': 'JSON',
    '.md': 'Markdown',
    '.java': 'Java',
    '.rb': 'Ruby',
    '.go': 'Go',
    '.rs': 'Rust',
    '.php': 'PHP',
    '.c': 'C',
    '.cpp': 'C++',
    '.h': 'C/C++ Header',
    '.cs': 'C#',
    '.swift': 'Swift',
    '.kt': 'Kotlin',
    '.sh': 'Shell',
    '.ps1': 'PowerShell',
    '.yml': 'YAML',
    '.yaml': 'YAML',
    '.xml': 'XML',
    '.lock': 'Lockfile'
}

IGNORE_DIRS = {'.git', 'node_modules', '__pycache__', '.venv', 'venv', 'dist', 'build'}

root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
lang_bytes = defaultdict(int)
other_bytes = 0

for dirpath, dirnames, filenames in os.walk(root):
    # filter out ignored dirs
    parts = set(dirpath.split(os.sep))
    if parts & IGNORE_DIRS:
        continue
    for fn in filenames:
        # skip the script itself
        if fn == os.path.basename(__file__):
            continue
        fp = os.path.join(dirpath, fn)
        try:
            size = os.path.getsize(fp)
        except OSError:
            continue
        _, ext = os.path.splitext(fn.lower())
        if ext in EXT_LANG:
            lang_bytes[EXT_LANG[ext]] += size
        else:
            other_bytes += size

# combine other into 'Other' if present
if other_bytes:
    lang_bytes['Other'] += other_bytes

# sort and compute percentages
total = sum(lang_bytes.values())
if total == 0:
    print('No files found to analyze.')
    raise SystemExit(0)

sorted_langs = sorted(lang_bytes.items(), key=lambda x: x[1], reverse=True)
# take top 8
top = sorted_langs[:8]

# build markdown table
md = []
md.append('### 📊 Linguagens neste repositório')
md.append('')
md.append('| Linguagem | Bytes | Percentual |')
md.append('|---:|---:|---:|')
for lang, size in top:
    pct = size / total * 100
    bar_len = int(pct / 5)  # 20 chars max
    bar = '█' * bar_len + '░' * (20 - bar_len)
    md.append(f'| {lang} | {size:,} | {pct:.1f}% {bar} |')

# include markers for easy replacement
print('\n'.join(['<!--languages-start-->'] + md + ['<!--languages-end-->']))
