#!/usr/bin/env python3
"""kdict-data 저장소의 자료 꾸러미를 묶고 manifest.json을 만든다.

  python3 tools/publish_data.py <kdict-data 폴더> [--init-from-app <kdict 폴더>] [--min-app N]

- <data>/src/<id>.jsonl 또는 <id>.json 이 원본. 꾸러미 id = 파일 이름.
- <data>/packs.json(선택): {"<id>": {"desc": "...", "min_app": 1, "url": "https://...(Release 자산)"}}
- 결과: <data>/packs/<id>.<ext>.gz + <data>/manifest.json
- 내용이 바뀐 꾸러미만 버전이 오른다(YYYY.MM.DD-N). 안 바뀐 건 이전 버전 그대로.
  판은 원본(src) 바이트의 sha256(content_sha256)으로 정한다. 압축 라이브러리(zlib) 판이 달라 다시 압축한 결과가 달라도,
  올려 둔 꾸러미(packs/*.gz)를 풀어 src와 같으면 그 파일·sha256·판을 그대로 쓴다(malgeul-data 0dcddc0과 같은 규칙).
- manifest.json·manifest.sig는 Windows에서도 LF로 쓴다. 꾸러미가 하나도 안 바뀌면 generated 시각도 그대로 둔다.
- 큰 파일(Release에 올릴 것)은 packs.json에 url을 적으면 manifest에 그 주소가 들어간다(gz 파일은 직접 올리기).
- manifest.json을 서명 키(ECDSA P-256)로 서명해 manifest.sig를 만든다. 앱은 서명이 맞는 manifest만 쓴다.
  키: --key 또는 환경 변수 KDICT_SIGN_KEY, 없으면 ~/.kdict-keys/data_sign_ec.pem 또는 /home/claude/.kdict-keys/data_sign_ec.pem. 키는 저장소에 올리지 말 것.
"""
import argparse, base64, datetime, gzip, hashlib, json, os, shutil, sys

APP_ASSETS = {
    'dictation_g1': 'play/dictation_g1.jsonl', 'dictation_g2': 'play/dictation_g2.jsonl', 'dictation_g3': 'play/dictation_g3.jsonl',
    'dictation_g4': 'play/dictation_g4.jsonl', 'dictation_g5': 'play/dictation_g5.jsonl', 'dictation_g6': 'play/dictation_g6.jsonl',
    'confusables': 'play/confusables.jsonl', 'onomatopoeia': 'play/onomatopoeia.jsonl', 'motion': 'play/motion.json',
    'hanja': 'hanja/hanja.json', 'hide_examples': 'hide/hide_examples.json', 'kid_block': 'hide/kid_block.json',
}
APP_ASSETS.update({'vocab_g%d' % g: 'play/vocab_g%d.jsonl' % g for g in range(1, 7)})
DESC = {'dictation_g%d' % g: '받아쓰기 %d학년' % g for g in range(1, 7)}
DESC.update({'vocab_g%d' % g: '학년 낱말 %d학년' % g for g in range(1, 7)})
DESC.update(confusables='헷갈리는 말', onomatopoeia='흉내 내는 말', motion='흉내 말 움직임', hanja='한자 사전',
            hide_examples='가린 예문 목록(감수)', kid_block='아이에게 먼저 내지 않을 말(주제 차단)', features='기능 켜고 끄기')


def check(path, fmt):
    with open(path, encoding='utf-8') as f:
        if fmt == 'jsonl':
            n = 0
            for i, line in enumerate(f, 1):
                line = line.strip()
                if not line:
                    continue
                try:
                    json.loads(line)
                except Exception as e:
                    sys.exit(f'{path}:{i} JSON 오류: {e}')
                n += 1
            if not n:
                sys.exit(f'{path}: 빈 파일')
        else:
            try:
                json.load(f)
            except Exception as e:
                sys.exit(f'{path} JSON 오류: {e}')


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('data')
    ap.add_argument('--init-from-app')
    ap.add_argument('--min-app', type=int, default=None)
    keys = [os.environ.get('KDICT_SIGN_KEY'), os.path.expanduser('~/.kdict-keys/data_sign_ec.pem'), '/home/claude/.kdict-keys/data_sign_ec.pem']
    ap.add_argument('--key', default=next((k for k in keys if k and os.path.exists(k)), keys[1]))
    a = ap.parse_args()
    if not os.path.exists(a.key):
        sys.exit(f'서명 키가 없어요: {a.key}\n  앱은 서명이 맞는 manifest만 받으므로, 키 없이 만들면 휴대폰이 새 자료를 받지 않아요.')
    src = os.path.join(a.data, 'src'); out = os.path.join(a.data, 'packs')
    os.makedirs(src, exist_ok=True); os.makedirs(out, exist_ok=True)
    if a.init_from_app:
        base = os.path.join(a.init_from_app, 'app/src/main/assets')
        for pid, rel in APP_ASSETS.items():
            shutil.copyfile(os.path.join(base, rel), os.path.join(src, pid + os.path.splitext(rel)[1]))
        feat = os.path.join(src, 'features.json')
        if not os.path.exists(feat):
            with open(feat, 'w', encoding='utf-8') as f:
                f.write('{}\n')
    old = {}
    mpath = os.path.join(a.data, 'manifest.json')
    if os.path.exists(mpath):
        m0 = json.load(open(mpath, encoding='utf-8'))
        old = {p['id']: p for p in m0.get('packs', [])}
        min_app = m0.get('min_app', 1)
    else:
        min_app = 1
    if a.min_app is not None:
        min_app = a.min_app
    extra = {}
    ppath = os.path.join(a.data, 'packs.json')
    if os.path.exists(ppath):
        extra = json.load(open(ppath, encoding='utf-8'))
    today = datetime.date.today().strftime('%Y.%m.%d')
    packs = []
    for name in sorted(os.listdir(src)):
        pid, ext = os.path.splitext(name)
        if ext not in ('.jsonl', '.json'):
            continue
        fmt = ext[1:]
        path = os.path.join(src, name)
        check(path, fmt)
        raw = open(path, 'rb').read()
        content = hashlib.sha256(raw).hexdigest()
        gzname = f'{pid}{ext}.gz'
        gzpath = os.path.join(out, gzname)
        prev = old.get(pid)
        # 올려 둔 꾸러미가 src와 같은 내용인지(압축 라이브러리 판과 무관하게 풀어서 비교)
        same_gz = False
        if prev and os.path.exists(gzpath) and not str(prev.get('url', '')).startswith('http'):
            try:
                g0 = open(gzpath, 'rb').read()
                same_gz = hashlib.sha256(g0).hexdigest() == prev.get('sha256') and gzip.decompress(g0) == raw
            except Exception:
                same_gz = False
        if prev and os.path.exists(gzpath) and (same_gz or prev.get('content_sha256') == content):
            ver = prev['version']  # 같은 내용: 올려 둔 파일·판 그대로(다시 압축하지 않음)
        elif not prev and a.init_from_app and (pid == 'features' or pid in APP_ASSETS):
            ver = '0'  # 앱에 이미 든 것과 같음: 휴대폰이 다시 받지 않게
            with open(gzpath, 'wb') as f:
                with gzip.GzipFile(filename='', mode='wb', fileobj=f, mtime=0, compresslevel=9) as g:
                    g.write(raw)
        else:
            n = 1
            if prev and prev['version'].startswith(today + '-'):
                n = int(prev['version'].split('-')[-1]) + 1
            ver = f'{today}-{n}'
            with open(gzpath, 'wb') as f:  # mtime=0: 같은 내용이면 같은 gz
                with gzip.GzipFile(filename='', mode='wb', fileobj=f, mtime=0, compresslevel=9) as g:
                    g.write(raw)
        gz = open(gzpath, 'rb').read()
        e = extra.get(pid, {})
        packs.append({'id': pid, 'version': ver, 'url': e.get('url', f'packs/{gzname}'),
                      'sha256': hashlib.sha256(gz).hexdigest(), 'size': len(gz), 'format': fmt, 'gzip': True,
                      'min_app': e.get('min_app', 1), 'desc': e.get('desc', DESC.get(pid, pid)), 'content_sha256': content})
        print(f'{pid:14} {ver:14} {len(gz):>9}B  {"(바뀜)" if not prev or prev["version"] != ver else ""}')
    man = {'schema': 1, 'generated': datetime.datetime.now().astimezone().isoformat(timespec='seconds'), 'min_app': min_app, 'packs': packs}
    if old and packs == list(old.values()) and min_app == m0.get('min_app', 1):
        man['generated'] = m0.get('generated', man['generated'])  # 바뀐 꾸러미가 없으면 manifest도 그대로
    with open(mpath, 'w', encoding='utf-8', newline='\n') as f:  # Windows에서도 LF
        json.dump(man, f, ensure_ascii=False, indent=1)
        f.write('\n')
    sign(mpath, a.key)
    print('manifest.json 저장:', len(packs), '개 · manifest.sig 서명함')


def sign(mpath, key_path):
    """manifest.json 바이트 그대로를 SHA256withECDSA로 서명 → manifest.sig(base64 DER)"""
    from cryptography.hazmat.primitives import hashes, serialization
    from cryptography.hazmat.primitives.asymmetric import ec
    key = serialization.load_pem_private_key(open(key_path, 'rb').read(), password=None)
    raw = open(mpath, 'rb').read()
    sig = key.sign(raw, ec.ECDSA(hashes.SHA256()))
    key.public_key().verify(sig, raw, ec.ECDSA(hashes.SHA256()))
    with open(os.path.join(os.path.dirname(mpath), 'manifest.sig'), 'w', encoding='ascii', newline='\n') as f:
        f.write(base64.b64encode(sig).decode() + '\n')


if __name__ == '__main__':
    main()
