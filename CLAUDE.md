# kdict-data — 아이용 국어사전(kdict) 데이터 꾸러미 (공개 저장소)

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
