#!/usr/bin/env python3
import os
import sys
import json
import time
from collections import defaultdict
try:
    from urllib.request import Request, urlopen
    from urllib.error import HTTPError, URLError
except Exception:
    print('Erro importando urllib.'); raise

USERNAME = os.environ.get('GITHUB_USER', 'NayaraLF')
TOKEN = os.environ.get('GITHUB_TOKEN')
PER_PAGE = 100

HEADERS = {'User-Agent': 'lang-stats-script'}
if TOKEN:
    HEADERS['Authorization'] = f'token {TOKEN}'


def fetch_url(url):
    req = Request(url, headers=HEADERS)
    try:
        with urlopen(req, timeout=30) as resp:
            data = resp.read()
            headers = resp.getheaders()
            return data, dict((k.lower(), v) for k, v in headers)
    except HTTPError as e:
        print(f'HTTPError {e.code} for {url}', file=sys.stderr)
        return None, e.headers if hasattr(e, 'headers') else {}
    except URLError as e:
        print(f'URLError for {url}: {e}', file=sys.stderr)
        return None, {}


def get_all_repos(user):
    repos = []
    page = 1
    while True:
        url = f'https://api.github.com/users/{user}/repos?per_page={PER_PAGE}&page={page}'
        data, headers = fetch_url(url)
        if data is None:
            break
        try:
            page_repos = json.loads(data.decode())
        except Exception as e:
            print('Erro ao decodificar JSON de repos:', e, file=sys.stderr)
            break
        if not page_repos:
            break
        repos.extend(page_repos)
        # check if fewer than per_page -> last page
        if len(page_repos) < PER_PAGE:
            break
        page += 1
        time.sleep(0.1)
    return repos


def get_repo_languages(languages_url):
    data, headers = fetch_url(languages_url)
    if data is None:
        return {}
    try:
        return json.loads(data.decode())
    except Exception as e:
        print('Erro ao decodificar JSON de languages:', e, file=sys.stderr)
        return {}


def main():
    user = USERNAME
    print(f'Agregando linguagens para usuário: {user}', file=sys.stderr)
    repos = get_all_repos(user)
    if not repos:
        print('Nenhum repositório encontrado ou erro na API.', file=sys.stderr)
        sys.exit(1)

    totals = defaultdict(int)
    repo_count = 0
    for r in repos:
        # pular forks vazios possiveis
        if r.get('archived'):
            continue
        lang_url = r.get('languages_url')
        if not lang_url:
            continue
        langs = get_repo_languages(lang_url)
        if not langs:
            # pode ser vazio (0 bytes) — ainda conta como repo
            repo_count += 1
            continue
        for lang, b in langs.items():
            totals[lang] += int(b)
        repo_count += 1
        time.sleep(0.05)

    total_bytes = sum(totals.values())
    if total_bytes == 0:
        print('Nenhuma linguagem com bytes encontrados nos repositórios públicos do usuário.')
        sys.exit(0)

    sorted_langs = sorted(totals.items(), key=lambda x: x[1], reverse=True)
    top = sorted_langs[:3]

    md = []
    md.append('<!--languages-start-->')
    md.append(f'### 📊 Linguagens (todos os repositórios do usuário {user})')
    md.append('')
    md.append('| Linguagem | Bytes | Percentual |')
    md.append('|---:|---:|---:|')
    for lang, size in top:
        pct = size / total_bytes * 100
        bar_len = int(pct / 5)
        bar_len = max(0, min(20, bar_len))
        bar = '█' * bar_len + '░' * (20 - bar_len)
        md.append(f'| {lang} | {size:,} | {pct:.1f}% {bar} |')

    # include 'Other' if there are more langs
    others = sorted_langs[3:]
    if others:
        others_sum = sum(x[1] for x in others)
        pct = others_sum / total_bytes * 100
        bar_len = int(pct / 5)
        bar_len = max(0, min(20, bar_len))
        bar = '█' * bar_len + '░' * (20 - bar_len)
        md.append(f'| Other | {others_sum:,} | {pct:.1f}% {bar} |')

    md.append('<!--languages-end-->')

    print('\n'.join(md))

if __name__ == '__main__':
    main()
