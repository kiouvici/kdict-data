#!/usr/bin/env python3
"""kdict-data 저장소의 자료 꾸러미를 묶고 manifest.json을 만든다.

  python3 tools/publish_data.py <kdict-data 폴더> [--init-from-app <kdict 폴더>] [--min-app N]

- <data>/src/<id>.jsonl 또는 <id>.json 이 원본. 꾸러미 id = 파일 이름.
- <data>/packs.json(선택): {"<id>": {"desc": "...", "min_app": 1, "url": "https://...(Release 자산)"}}
- 결과: <data>/packs/<id>.<ext>.gz + <data>/manifest.json
- 내용이 바뀐 꾸러미만 버전이 오른다(YYYY.MM.DD-N). 안 바뀐 건 이전 버전 그대로.
- 큰 파일(Release에 올릴 것)은 packs.json에 url을 적으면 manifest에 그 주소가 들어간다(gz 파일은 직접 올리기).
"""
import argparse, datetime, gzip, hashlib, json, os, shutil, sys

APP_ASSETS = {
    'dictation_g1': 'play/dictation_g1.jsonl', 'dictation_g2': 'play/dictation_g2.jsonl', 'dictation_g3': 'play/dictation_g3.jsonl',
    'dictation_g4': 'play/dictation_g4.jsonl', 'dictation_g5': 'play/dictation_g5.jsonl', 'dictation_g6': 'play/dictation_g6.jsonl',
    'confusables': 'play/confusables.jsonl', 'onomatopoeia': 'play/onomatopoeia.jsonl', 'motion': 'play/motion.json',
    'hanja': 'hanja/hanja.json', 'hide_examples': 'hide/hide_examples.json',
}
DESC = {'dictation_g%d' % g: '받아쓰기 %d학년' % g for g in range(1, 7)}
DESC.update(confusables='헷갈리는 말', onomatopoeia='흉내 내는 말', motion='흉내 말 움직임', hanja='한자 사전',
            hide_examples='가린 예문 목록(감수)', features='기능 켜고 끄기')


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
    a = ap.parse_args()
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
        if prev and prev.get('content_sha256') == content and os.path.exists(gzpath):
            ver = prev['version']
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
    with open(mpath, 'w', encoding='utf-8') as f:
        json.dump(man, f, ensure_ascii=False, indent=1)
        f.write('\n')
    print('manifest.json 저장:', len(packs), '개')


if __name__ == '__main__':
    main()
