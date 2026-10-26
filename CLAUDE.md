# kdict-data — 아이용 국어사전(kdict) 데이터 꾸러미 (공개 저장소)

- **공개 저장소가 원칙**(대표님 결정 2026-10-26 15:53): 앱이 로그인 없이 raw.githubusercontent.com에서 꾸러미를 받기 때문. 비공개로 바꾸지 않고, 공개·비공개를 대표님께 다시 묻지 않는다. 서명 키·비밀번호·개인 자료는 절대 올리지 않는다(서명 파일 manifest.sig만).

앱이 시작할 때 `manifest.json`(+`manifest.sig` 서명)을 받아, 내장본보다 새 꾸러미만 내려받는다. 서명이 맞지 않으면 받지 않는다.
공통 규칙은 `~/.claude/CLAUDE.md`, 앱 설명은 `../kdict/CLAUDE.md`.

## 구조
- `src/` 원본(JSON) → `tools/publish_data.py`가 `packs/*.gz`·`packs.json`·`manifest.json`·`manifest.sig`를 만든다.
- 주요 꾸러미: hanja(한자 훈음·필순), kid_block(아이 차단: words, defs, prefix, keep, allow, easy_skip, easy_first, easy_kid, chain_ban), vocab(학년 낱말), dictation_g1~g6(받아쓰기), confusables(헷갈리는 말), 흉내말, hide_examples, features.
- 버전 형식 "YYYY.MM.DD-N".

## 게시
```
python tools/publish_data.py . --key ~/.kdict-keys/data_sign_ec.pem
```
- 키 없이 만들면 폰이 새 자료를 받지 않는다. 키는 절대 커밋하지 않는다.
- 게시 후 commit·push(main) → 폰 앱 「자료 받기」로 반영 확인.
- 앱 코드 변경과 짝이 맞아야 하는 데이터는 앱 빌드와 함께 게시한다.

## 말글사전과 공유
- hanja의 h, u, p, ps, od, pv만 공유한다. 바꾸면 `../malgeul-data/src`의 같은 글자 필드만 패치(통째 복사 금지).
- 아이앱 전용: 급수 lv, 아이용 훈(女 '여자 녀' 등), kid_block 등 나머지 전부. 말글사전에 넣지 않는다.

## 사전 앱 예외(공통 규칙 원본 kiouvici/dev-setup에 더해, 2026-10-24 대표님 결정)
- **inbox**: `~/dev/kdict-docs/inbox/` + kdict-docs PR #1(댓글로 알림). 목업은 노트북이 만들어 대화창에 보고한다.
- **Git**: kdict-data·malgeul-data는 main push = 게시이므로 main에 직접(게시 스크립트·공유 필드 검사 통과 뒤). kdict-docs는 문서·inbox라 main 직접. kdict·malgeul은 Actions 결제가 풀릴 때까지 자동 검사가 돌지 않으므로 노트북 검사(node --check·단위 시험·끝말잇기 162항목) 통과를 녹색으로 대신하고, main 푸시는 `[skip ci]`, 정식 배포는 노트북 빌드(kdict-docs `setup/DECISIONS.md`).
- **승인된 인터넷 사용**: kdict — 자료 꾸러미 받기(raw.githubusercontent.com/kiouvici/kdict-data), 국립국어원 로그인·사전 받기(stdict·krdict.korean.go.kr), 손글씨 한자 인식 모델 1회 받기(ML Kit, 와이파이). 말글사전 — 자료 꾸러미 받기(raw.githubusercontent.com/kiouvici/malgeul-data), 국립국어원 로그인·사전 받기(stdict·opendict.korean.go.kr).
- **감수팀**: 국어국문학 교수·초등학교 교사·사전 편찬 편집장·국립국어원 직원·학부모·아동 심리 전문가(kdict는 아이 보호 기준, 말글사전은 어른앱 기준으로 정확성·오류 중심).
- **프로젝트 금지**: 필순.dat 복호화 금지, 네이버 자동 수집 금지, 두 앱 공유 데이터는 hanja의 h·u·p·ps·od·pv만.