import os, json, urllib.request, urllib.error, sys

TOKEN = os.environ.get('GH_TOKEN', '')
if not TOKEN:
    print('NO_TOKEN'); sys.exit(1)

API = 'https://api.github.com'
OWNER = 'djmssb'
REPO = 'eddie-format-fix'


def req(method, path, data=None, extra_headers=None):
    url = path if path.startswith('http') else API + path
    body = None
    headers = {
        'Authorization': 'Bearer ' + TOKEN,
        'Accept': 'application/vnd.github+json',
        'User-Agent': 'eddie-format-publisher',
        'X-GitHub-Api-Version': '2022-11-28',
    }
    if data is not None:
        body = json.dumps(data).encode()
        headers['Content-Type'] = 'application/json'
    if extra_headers:
        headers.update(extra_headers)
    r = urllib.request.Request(url, data=body, headers=headers, method=method)
    try:
        with urllib.request.urlopen(r, timeout=60) as resp:
            raw = resp.read()
            return resp.status, json.loads(raw) if raw else {}
    except urllib.error.HTTPError as e:
        raw = e.read()
        try:
            return e.code, json.loads(raw)
        except Exception:
            return e.code, {'raw': raw[:800].decode('utf-8', 'ignore')}


def main():
    action = sys.argv[1] if len(sys.argv) > 1 else 'create'

    if action == 'create':
        status, d = req('POST', '/user/repos', {
            'name': REPO,
            'description': '飞鼠格式 FlyingMouse Format 第三方修复版（非官方）：Markdown 图片文件夹隔离、扫描版 PDF 走 OCR 兜底、qpdf 缺失时禁用加密解密、赞助弹窗清理',
            'homepage': f'https://github.com/{OWNER}/{REPO}',
            'private': False,
            'has_issues': True,
            'has_wiki': False,
            'has_projects': False,
            'auto_init': False,
        })
        print('status', status)
        if status in (200, 201):
            print('created:', d.get('full_name'), d.get('html_url'))
            print('clone:', d.get('clone_url'))
        else:
            print('error:', json.dumps(d, ensure_ascii=False)[:600])

    elif action == 'info':
        status, d = req('GET', f'/repos/{OWNER}/{REPO}')
        print('status', status, d.get('full_name'), d.get('default_branch'))


if __name__ == '__main__':
    main()
