# Astra용 Google Flow 실행 순서 (v5)

목적: 20개 클립을 같은 출연진, 같은 화풍으로 빠르게 뽑아 저장소에 넣는다. 프롬프트 원본은 `films.json`, 복사용은 `PROMPT_PACK.md`와 `storyboard.html`이다. 프롬프트를 고쳐야 하면 고친 문장을 `clips.json`에 기록해서 Claude가 `films.json`에 반영할 수 있게 한다.

## 0. 준비

- Flow 프로젝트 하나를 만든다: `PPEL v5 research shorts`. 편마다 프로젝트를 나누지 않는다(재료를 공유해야 한다).
- 화면비 16:9, 출력은 가능한 최고 해상도로 다운로드한다. 최종본은 1280×720으로 정규화한다.
- 모델 등급: 초안은 Fast 등급, 채택 컷만 최고 등급으로 다시 생성한다. 크레딧 수치는 Flow 화면의 현재 값을 그대로 `clips.json`에 적는다(요금은 바뀐다).

## 1. 재료(Ingredients) 6장

`films.json`의 `ingredients` 프롬프트로 이미지를 만든다. 인물은 전신, 정면, 무표정, 회색 단색 배경. 얼굴이 뚜렷하게 보이는 장을 고른다. 배경이 지저분하거나 소품이 프롬프트와 충돌하면 일관성이 떨어진다.

저장: `Video/research/v5/ingredients/I1.png` ~ `I6.png`, 그리고 `ingredients/README.md`에 각 장의 생성 도구, 프롬프트, 재시도 횟수를 적는다.

## 2. 파일럿 2개(스토리 확정과 무관, 바로 시작)

| 파일럿 | 클립 | 검증 목적 |
|---|---|---|
| P1 | 5편 클립 1 (다이빙 캐치) | 동작 강도, 화면 밖 절규의 발화, 성만 재료의 일관성 |
| P2 | 1편 클립 2 (걸음 3종, 고정 카메라) | 한 클립 안 반복 동작의 안정성, 지안의 무반응 연기, 모니터 파형 표현 |

저장: `Video/research/v5/pilot/P1-<try>.mp4`, `P2-<try>.mp4`. 2fps 컨택트 시트(`P1-<try>-sheet.png`)와 발화 시각 메모를 함께 둔다. 교수님 승인 1은 여기서 받는다.

## 3. 본 생성 순서

편 순서: 5 → 1 → 4 → 2 → 3. 5편은 교수님이 가장 낫다고 본 편이라 화풍 기준이 되고, 3편은 은유가 가장 위험해 마지막에 남긴다.

각 클립 규칙:

1. 프롬프트 맨 앞에 `films.json`의 `style.block`을 붙인다. `PROMPT_PACK.md`에는 이미 붙어 있다.
2. 그 클립의 `ingredients`에 적힌 재료만 넣는다(최대 3장). 인물이 등장하지 않는 재료는 넣지 않는다.
3. 대사는 프롬프트의 큰따옴표 안 한국어를 그대로 둔다. 발화가 두 번 실패하면 문장을 하나로 줄이고 그 사실을 `clips.json`에 적는다.
4. 화면에 글자, 자막, 로고가 생기면 채택하지 않는다. 모니터의 파형만 허용된다.
5. 인물 복제, 손가락 이상, 소품 변형이 있으면 그 시도는 버리고 프롬프트를 바꾸지 말고 한 번 더 생성한다. 두 번 실패하면 프롬프트를 손보고 변경 내용을 기록한다.
6. 채택 컷은 최고 등급으로 한 번 더 생성해 그 파일을 최종으로 쓴다. 초안이 더 좋으면 초안을 쓰고 그 사실을 기록한다.

## 4. 파일 규격

```
Video/research/v5/
  ingredients/I1.png … I6.png, README.md
  pilot/P1-1.mp4, P2-1.mp4, *-sheet.png
  ai-paper/clip-1.mp4 … clip-4.mp4, clips.json
  biosensor/clip-1.mp4 … clip-4.mp4, clips.json
  memory/clip-1.mp4 … clip-4.mp4, clips.json
  energy-storage/clip-1.mp4 … clip-4.mp4, clips.json
  cherry-blossom/clip-1.mp4 … clip-4.mp4, clips.json
```

`clips.json` 형식(편 폴더마다 하나):

```json
{
  "clips": [
    { "n": 1, "file": "clip-1.mp4", "model": "<Flow에 표시된 모델명>", "credits": 20,
      "tries": 2, "promptChanged": false, "promptUsed": "<바꾼 경우에만 전체 문장>",
      "sourceStart": 0.5, "useDuration": 7,
      "speech": [ { "text": "잠깐만요!", "at": 0.4 } ],
      "issues": "" }
  ]
}
```

- `sourceStart`, `useDuration`: 최종본에 넣을 구간. 기본 0.5초부터 7초. 앞머리 흔들림이나 끝 복제가 있으면 여기서 피한다.
- `speech.at`: 클립 안에서 대사가 시작되는 초. Claude가 자막 시각을 여기에 맞춘다.
- 컨택트 시트: 채택 클립마다 2fps 시트 한 장(`clip-1-sheet.png`).

## 5. 완료 보고

편 폴더 5개가 채워지면 `v5/README.md`의 상태를 `clips_ready`로 바꾸고 커밋한다. 이후 Claude가 자막 정렬과 `node scripts/assemble-v5.cjs` 실행, 홈페이지 연결을 맡는다.

## English summary for Astra

One Flow project for all five films so the six ingredient images (`films.json` → `ingredients`) are shared. Make the ingredients first (full body, front, neutral, plain gray background), then two pilots (film 5 clip 1, film 1 clip 2) for the owner's first approval. Then generate in film order 5, 1, 4, 2, 3, four clips each, Fast tier for drafts and the top tier for the adopted take. Prefix every prompt with `style.block` (already done in `PROMPT_PACK.md`), attach only that clip's listed ingredients (max 3), keep the Korean dialogue verbatim, reject any take with on-screen text, duplicated people, or deformed props, and record every take in the per-film `clips.json` (model, credits, tries, prompt changes, source range, speech start times). Save files exactly as the tree above and flip `v5/README.md` status to `clips_ready` when done.
