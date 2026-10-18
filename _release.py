import os, json, sys, urllib.request, urllib.error

TOKEN = os.environ.get('GH_TOKEN', '')
OWNER, REPO = 'djmssb', 'eddie-format-fix'
TAG = 'v0.6.4-fix.1'

BODY = """**第三方修复版，非官方发布。** 原始软件版权归 [牢蜂 LaoFeng](https://github.com/LaoFeng-mouse/flyingmouse-format) 所有，本版仅修复若干转换流程问题，免费、不商用，遵循原项目「禁止商业售卖/转卖/套壳」的条款。

## 修复内容

1. **Markdown 图片文件夹不再互相覆盖** —— 每次转换生成独立的 `.assets` 文件夹，桌面端与 CLI 都能正确取回，文件重命名后依然有效。
2. **CLI 转换 Markdown 时下载网络图片** —— 补齐命令行路径的图片抓取，不再只留失效链接。
3. **qpdf 缺失时禁用 PDF 加密/解密** —— 发行包不含 qpdf，界面直接把相关选项置灰，不再点了报错。
4. **扫描版 PDF 转 Word 走 OCR 兜底** —— 没有结构化 PDF 引擎时改用 OCR；纯文字 PDF 转换后明确提示「图片与版式不保留」。
5. **赞助弹窗去掉强迫性提示语** —— 中英文同步删除最后一句，保留免费、自愿支持的表述。

原始压缩包保留为 `resources/app.asar.before-fix`，可随时回退。

## 下载

`Eddie-format-0.6.4-win-x64.zip` — 解压后双击 `Eddie format.exe` 直接使用。
内置 LibreOffice / FFmpeg / Poppler / Tesseract 四套离线引擎，无需另装 Office 或 Python。必须保留整个文件夹，`resources` 是引擎本体。

首次运行 SmartScreen 可能提示未知发布者，选择「更多信息 → 仍要运行」。

## 需要的系统

Windows 10 / 11 x64。程序完全离线运行，不联网、不上传文件。
"""


def req(method, path, data=None):
    url = path if path.startswith('http') else 'https://api.github.com' + path
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
    r = urllib.request.Request(url, data=body, headers=headers, method=method)
    try:
        with urllib.request.urlopen(r, timeout=90) as resp:
            raw = resp.read()
            return resp.status, json.loads(raw) if raw else {}
    except urllib.error.HTTPError as e:
        raw = e.read()
        try:
            return e.code, json.loads(raw)
        except Exception:
            return e.code, {'raw': raw[:500].decode('utf-8', 'ignore')}


def main():
    action = sys.argv[1] if len(sys.argv) > 1 else 'create'

    if action == 'create':
        status, d = req('POST', f'/repos/{OWNER}/{REPO}/releases', {
            'tag_name': TAG,
            'name': f'{TAG} · Eddie format 第三方修复版',
            'body': BODY,
            'draft': False,
            'prerelease': False,
        })
        print('status', status)
        if status == 201:
            print('id:', d['id'])
            print('url:', d['html_url'])
            print('upload:', d['upload_url'])
            with open('_release_id.txt', 'w') as f:
                f.write(str(d['id']))
        else:
            print(json.dumps(d, ensure_ascii=False)[:800])

    elif action == 'list':
        status, d = req('GET', f'/repos/{OWNER}/{REPO}/releases')
        print('status', status)
        for r in d if isinstance(d, list) else []:
            print(r['tag_name'], r['id'], r['html_url'])
            for a in r.get('assets', []):
                print('  asset:', a['name'], round(a['size'] / 1024**2, 1), 'MB', a['state'])


if __name__ == '__main__':
    main()
