import os, sys, time, subprocess, json, urllib.request, urllib.error

TOKEN = os.environ.get('GH_TOKEN', '')
OWNER, REPO = 'djmssb', 'eddie-format-fix'
RELEASE_ID = 416425364
SRC = 'dist/Eddie-format-0.6.4-win-x64.zip'
PART_DIR = 'dist'
PART_MB = int(os.environ.get('PART_MB', '190'))

CHUNK = PART_MB * 1024 * 1024


def split():
    size = os.path.getsize(SRC)
    n = (size + CHUNK - 1) // CHUNK
    paths = []
    with open(SRC, 'rb') as f:
        for i in range(1, n + 1):
            p = f'{SRC}.{i:03d}'
            with open(p, 'wb') as out:
                remain = min(CHUNK, size - f.tell())
                while remain > 0:
                    buf = f.read(min(4 * 1024 * 1024, remain))
                    if not buf:
                        break
                    out.write(buf)
                    remain -= len(buf)
            paths.append(p)
            print(f'part {i}/{n}: {p} {os.path.getsize(p)/1024**2:.1f} MB', flush=True)
    return paths


def upload_one(path):
    name = os.path.basename(path)
    url = f'https://uploads.github.com/repos/{OWNER}/{REPO}/releases/{RELEASE_ID}/assets?name={name}'
    cmd = [
        'curl', '-sS', '-X', 'POST',
        '-H', f'Authorization: Bearer {TOKEN}',
        '-H', 'Content-Type: application/octet-stream',
        '-H', 'Accept: application/vnd.github+json',
        '-H', 'User-Agent: eddie-format-publisher',
        '-H', 'Expect:',
        '--keepalive-time', '30',
        '--max-time', '1200',
        '--data-binary', '@' + path,
        '-w', '\nHTTP=%{http_code} time=%{time_total} size=%{size_upload} speed=%{speed_upload}',
        url,
    ]
    r = subprocess.run(cmd, capture_output=True, text=True)
    out = (r.stdout or '') + (r.stderr or '')
    code = ''
    for line in out.splitlines():
        if line.startswith('HTTP='):
            code = line
    return out.strip()[-400:], code


def list_assets():
    url = f'https://api.github.com/repos/{OWNER}/{REPO}/releases/{RELEASE_ID}/assets'
    req = urllib.request.Request(url, headers={
        'Authorization': 'Bearer ' + TOKEN,
        'Accept': 'application/vnd.github+json',
        'User-Agent': 'eddie-format-publisher',
    })
    with urllib.request.urlopen(req, timeout=60) as resp:
        return json.loads(resp.read())


def delete_asset(aid):
    url = f'https://api.github.com/repos/{OWNER}/{REPO}/releases/assets/{aid}'
    req = urllib.request.Request(url, headers={
        'Authorization': 'Bearer ' + TOKEN,
        'Accept': 'application/vnd.github+json',
        'User-Agent': 'eddie-format-publisher',
    }, method='DELETE')
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            return resp.status
    except urllib.error.HTTPError as e:
        return e.code


def main():
    action = sys.argv[1] if len(sys.argv) > 1 else 'all'

    if action == 'split':
        split()

    elif action == 'upload':
        parts = sorted(p for p in os.listdir(PART_DIR) if '.zip.' in p)
        existing = {a['name'] for a in list_assets()}
        for p in parts:
            name = p
            if name in existing:
                print(f'skip (already on release): {name}', flush=True)
                continue
            full = os.path.join(PART_DIR, p)
            size_mb = os.path.getsize(full) / 1024**2
            for attempt in range(1, 5):
                t0 = time.time()
                print(f'[{name}] {size_mb:.0f} MB attempt {attempt} ...', flush=True)
                out, code = upload_one(full)
                dt = time.time() - t0
                print(f'  -> {dt:.0f}s {code}', flush=True)
                if 'HTTP=201' in code or 'HTTP=200' in code:
                    print(f'  OK {name}', flush=True)
                    break
                print('  ' + out.replace('\n', ' | ')[:300], flush=True)
                time.sleep(5)
            else:
                print(f'  FAILED {name} after 4 attempts', flush=True)

    elif action == 'list':
        for a in list_assets():
            print(a['name'], round(a['size'] / 1024**2, 1), 'MB', a['state'])


if __name__ == '__main__':
    main()
