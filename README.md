# kdict-data — 어린이 국어사전 앱 자료 꾸러미

어린이 국어사전 앱(kdict)이 **하루 한 번 알아서** 이 저장소의 `manifest.json`을 읽고,
버전이 올라간 자료만 내려받아 바꿉니다. 앱을 새로 만들(빌드할) 필요가 없습니다.

> 이 저장소는 **공개(public)** 저장소여야 합니다. 앱은 로그인 없이
> `https://raw.githubusercontent.com/kiouvici/kdict-data/main/` 에서 받습니다.
> 아이 이름·기록 같은 개인 정보는 절대 올리지 마세요.

## 폴더

| 위치 | 내용 |
|---|---|
| `src/` | **원본 자료** — 여기만 고치면 됩니다 |
| `packs/` | 앱이 받는 압축 파일(.gz) — 스크립트가 만듦, 손대지 않기 |
| `manifest.json` | 꾸러미 목록·버전·검사값 — 스크립트가 만듦 |
| `packs.json` | (선택) 설명·최소 앱 버전·외부 주소 지정 |
| `tools/publish_data.py` | 묶기 스크립트 |

## 꾸러미 목록

| id | 파일 | 내용 |
|---|---|---|
| `dictation_g1` ~ `dictation_g6` | `src/dictation_gN.jsonl` | 받아쓰기 1~6학년 문장 |
| `confusables` | `src/confusables.jsonl` | 헷갈리는 말 |
| `onomatopoeia` | `src/onomatopoeia.jsonl` | 흉내 내는 말 |
| `motion` | `src/motion.json` | 흉내 내는 말 움직임 |
| `hanja` | `src/hanja.json` | 한자 사전 (큼, 약 2.3MB 압축) |
| `hide_examples` | `src/hide_examples.json` | 감수로 가린 예문 목록 |
| `kid_block` | `src/kid_block.json` | 아이에게 앱이 먼저 내지 않을 말(술·담배·도박·연애·직장 생활어). 보호 모드에서 오늘의 낱말·퀴즈 보충 낱말·끝말잇기 앱 낱말·힌트에만 적용, 검색은 막지 않음. `words`=표제어 정확히 일치, `defs`=뜻풀이 정규식, `allow`=뜻풀이 규칙·동형어 사전 표시(flags)에서 빼 줄 흔한 낱말(주전자·시장), `easy_skip`=보호 모드 오늘의 낱말·퀴즈에서만 뺄 말(깨다). 보호 모드 상세 화면은 `defs`·Protect에 걸리는 뜻·예문을 가림 |
| `vocab_g1` ~ `vocab_g6` | `src/vocab_gN.jsonl` | 학년 필수 낱말(학년당 309~375개). 한 줄 = `{"w","pos","code"(표준사전 낱말 번호, 교과 용어는 없음),"t"(주제),"src"(근거),"d"(아이용 쉬운 뜻),"ex"(쉬운 예문),"f"(예문 속 모양)}`. 오늘의 공부·문맥으로 뜻 짐작·낱말 친구들에 씀. 보호 모드에서 kid_block에 걸리는 줄은 앱이 뺌 |
| `features` | `src/features.json` | 기능 켜고 끄기 (예: `{"새기능": true}`) |

### 한자 사전의 인명용 표시(`im`·`imr`·`ima`·`imv`)

- 출처: 가족관계의 등록 등에 관한 규칙, 대법원규칙 제3220호(2025. 7. 19. 시행) 별표1 인명용 추가 한자표·별표2 인명용 한자 허용 자체표(2024. 5. 30. 개정), 교육용 기초한자 1,800자
- `imr` 이름에 쓰는 소리. 주 1(첫소리가 ㄴ·ㄹ인 한자는 소리 나는 대로 ㅇ·ㄴ으로도 쓸 수 있음)에 따라 두음 소리를 함께 적음(예: `내,래`)
- `ima` 이 글자 대신 쓸 수 있는 허용 자체(별표2), `imv` 이 글자가 허용 자체인 본 글자
- 주 2(示변↔礻변, "++"변↔"十十"변은 서로 바꾸어 쓸 수 있음, 예: 福=福, 蘭=蘭)는 같은 부호 안의 글꼴 차이라 글자별 자료로 따로 적지 않음

### 한자 필순 출처(`p`·`ps`·`od`)

필순은 **일본식(KanjiVG) 순서**를 기준으로 하며, 말글사전(malgeul) `src/hanja.json`과 `p`·`ps`·`od` 값이 모든 글자에서 같은 공통 자료입니다(2026-10 통일).
한 글자에 자료가 여럿이면 `jp` > `kr` > `aj` > `cmp` 순서로 하나만 씁니다. 한국 순서(animCJK Ko)·중국 순서(animCJK ZhHant, Make Me a Hanzi)는 쓰지 않습니다.

- `jp` KanjiVG(https://kanjivg.tagaini.net, © Ulrich Apel, CC BY-SA 3.0 https://creativecommons.org/licenses/by-sa/3.0/)
  획 경로(`<path d>`)를 소수 첫째 자리로 줄여 그대로 씀.
- `kr` KanjiVG를 감수팀이 우리 자형으로 고친 것(순서는 일본식). CC BY-SA 3.0.
- `aj` animCJK(https://github.com/parsimonhi/animCJK) graphicsJa.txt(일본 순서)의 중심선(medians)을 109×109 좌표로 바꾼 것.
  Arphic Public License(Arphic PL KaitiM 글꼴 파생)를 따릅니다. 고쳐 쓰거나 다시 나눌 때도 이 라이선스를 지켜 주세요(사본: `licenses/arphic/ARPHICPL.TXT`).
- `cmp` KanjiVG에 없는 글자를 KanjiVG 부품(구성 요소별 획 경로)으로 이어 그린 것. 부품 분해는 KanjiVG 자체 구성 정보와 IDS(cjkvi-ids, CHISE 기반)를 쓰고,
  일본식 필순 규칙(왼쪽→오른쪽, 위→아래, 바깥→안, 囗는 마지막 획을 안 다음에, 辶·廴는 안 먼저 등)으로 순서를 정함. CC BY-SA 3.0.
  - 다음 22자는 예전 보충 때 부품 일부를 Make Me a Hanzi 중심선(Arphic Public License)으로 채운 것이 남아 있음: 亹俁刁奭巿彘彧橐毌爟瓘秭稶笫纍芾褰襫鈺鼉𥸴𦂈
  - KanjiVG 부품으로 만들 수 없어 필순이 없는 글자(15자): 沔玈疈舃舝褎覶豋𩑠燛橆縃𦁗枾𰜩
- `od: 1` 나라마다 순서가 다를 수 있는 글자(`aj`·`cmp` 전부, `jp` 중 일부). 앱이 "나라마다 순서가 달라요" 안내를 보여 줌.
- `pv: 1` 감수 확인 표시. 아이앱은 `cmp`를 `pv: 1`일 때만 보여 줌(감수 전이라 지금은 없음).
- 총획(`s`)과 획 수가 다르면(일본 자형: 艹 3획, 飠 8획 등) 앱이 "획수 다름" 안내를 함께 보여 줌.
- KanjiVG에서 온 필순 자료(`jp`·`kr`·`cmp`)를 고쳐 다시 나눌 때도 CC BY-SA 3.0(출처 표시·같은 조건)으로 나눠야 합니다.
- `_meta.imsrc` 인명용 한자 출처 문구(앱이 이 값을 읽어 보여 줌, 없으면 앱에 든 기본 문구)

새 이름의 파일(예: `src/proverbs.jsonl`)을 넣어도 앱이 받아 둡니다. 화면에 쓰려면 앱 쪽 기능이 있어야 합니다.

## 받아쓰기 문제 추가 방법

1. `src/dictation_g2.jsonl`(2학년 예)을 열고 **맨 아래에 한 줄씩** 넣습니다. 한 줄 = 한 문제.
   ```
   {"g": 2, "s": "동생과 같이 놀았어요.", "t": ["같이"], "cat": "소리표기"}
   ```
   - `g` 학년, `s` 읽어 줄 문장, `t` 채점할 낱말(문장 안에 그대로 있어야 함), `cat` 갈래
   - 파일은 **UTF-8**로 저장. 줄 끝에 쉼표 넣지 않기.
2. 묶기:
   ```
   python3 tools/publish_data.py .
   ```
   바뀐 꾸러미만 버전이 `2026.10.20-1`처럼 오르고, 문법이 틀린 줄이 있으면 몇째 줄인지 알려 주고 멈춥니다.
3. 올리기:
   ```
   git add -A && git commit -m "받아쓰기 2학년 문장 추가" && git push
   ```
4. 끝. 아이 휴대폰은 하루 안에 받습니다. 바로 확인하려면 앱 **어른 메뉴 → 자료 업데이트 → 지금 확인**.
   (GitHub 쪽 캐시 때문에 올린 뒤 5분쯤 걸릴 수 있어요.)

헷갈리는 말·흉내 내는 말도 같은 방법입니다(기존 줄 모양을 그대로 따라 쓰기).
아이들이 볼 자료이므로 **감수팀 확인을 거친 뒤** 올려 주세요.

## 고치기·되돌리기

- 잘못 올렸으면 `src/` 파일을 고치고 다시 2~3단계. 버전이 또 올라 휴대폰이 새로 받습니다.
- 앱은 받은 파일의 **크기·SHA-256 검사값**과 **JSON 문법**을 확인한 뒤에만 바꿉니다. 실패하면 지금 자료를 그대로 씁니다.
- 앱은 바로 앞 버전 하나를 남겨 둡니다.

## 큰 파일 (GitHub Release)

20MB가 넘는 자료는 휴대폰이 **와이파이에서만** 받습니다. 아주 큰 파일은 저장소 대신 Release 자산으로 올리고
`packs.json`에 주소를 적습니다:
```json
{"hanja": {"url": "https://github.com/kiouvici/kdict-data/releases/download/hanja-2026.10/hanja.json.gz"}}
```
스크립트가 만든 `packs/hanja.json.gz`를 그 Release에 올리면 됩니다(검사값은 manifest에 들어감).

## 앱 버전 제한

새 자료가 새 앱에서만 돌아가면 `packs.json`에 `"min_app": <앱 versionCode>`를 적습니다.
그보다 낮은 앱은 그 꾸러미를 받지 않고 "앱 업데이트 필요"로 표시합니다.
전체를 막으려면 `python3 tools/publish_data.py . --min-app N`.

## 처음 만든 방법 (참고)

```
python3 tools/publish_data.py . --init-from-app ../kdict
```
앱에 든 자료와 같은 첫 꾸러미는 버전 `0`(=앱 기본)이라 휴대폰이 다시 받지 않습니다.
