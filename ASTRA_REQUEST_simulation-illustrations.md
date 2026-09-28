# Astra 요청: 시뮬레이션 협업 섹션 카드 일러스트 3장

요청 2026-09-28 · 요청자 임수만 교수님 (정리 Claude) · 대상 브랜치 `claude/dft-comsol-collaboration-message-i5z4cd`

## 1. 배경

- PPEL+ 홈페이지(`index.html`) 연구 섹션 뒤에 DFT·COMSOL 시뮬레이션 협업 섹션을 넣는 중입니다. 시안 파일은 이 브랜치의 `simulation-preview.html` 입니다.
- 섹션에는 DFT, MD(준비 중), COMSOL 카드 3장이 나란히 있고, 각 카드 위쪽에 가로로 긴 그림이 들어갑니다.
- Claude가 만든 벡터 그림은 엉성해서 쓰지 않기로 했습니다(교수님 결정). 그림은 Astra가 만듭니다.

## 2. 산출물

| 파일 | 카드 | 주조색 |
|---|---|---|
| `image/simulation/illust-dft.webp` | DFT (원자·전자) | 파랑 `#1E3AFF` 계열 |
| `image/simulation/illust-md.webp` | MD (분자·계면, 준비 중) | 청록 `#00B79C` 계열 |
| `image/simulation/illust-comsol.webp` | COMSOL (소자·장) | 호박색 `#FF8A00` 계열 |

- 크기 1600×700 px (16:7), WebP 품질 85 안팎, 파일당 300 KB 이하
- 흰 바탕(#FFFFFF), 가장자리 여백 넉넉히 (카드 모서리가 둥글게 잘리고, 휴대폰에서는 좌우가 조금 잘릴 수 있음)
- 그림 안에 글자, 숫자, 기호, 로고, 워터마크를 넣지 않습니다.

## 3. 스타일

- 기존 연구 카드 그림과 같은 계열로 맞춥니다. 먼저 `image/research/*.jpg` 5장을 열어 보십시오. 흰 바탕에 수채화 번짐과 가는 기술 선화를 섞고, 카드마다 한 색 계열을 강조하는 필치입니다.
- 세 장이 한 세트로 보이도록 구도, 선 굵기, 번짐 정도를 통일합니다.
- 과학적으로 틀린 묘사는 피합니다. 아래 장면 설명을 벗어나는 장식(로봇, 사람 얼굴 등)은 넣지 않습니다.

## 4. 장면

1. **DFT**: 육각 격자로 배열된 결정 표면(광택 있는 구슬 원자층) 위에 작은 분자가 흡착해 있고, 분자와 표면 사이에 전하 밀도 차 등고면(반투명한 파랑 로브와 옅은 주황 로브)이 떠 있는 장면. 결합은 가는 선.
2. **MD**: 옅은 점선으로 그린 주기 경계 상자(육면체) 안에서 고분자 사슬(청록 구슬 목걸이)이 얽혀 있고, 이온 몇 개가 점선 궤적을 남기며 움직이는 장면.
3. **COMSOL**: 손끝이나 누름판이 얇은 유연 인쇄 필름을 누르고 있고, 필름 표면에 유한요소 삼각 메시와 전위 분포 색 지도(파랑에서 청록, 주황으로 부드럽게 이어짐)가 입혀진 장면.

이미지 생성 모델용 영문 프롬프트 (그대로 쓰거나 다듬어서 사용):

- DFT: `Watercolor scientific illustration on a pure white background, matching a lab website's research artwork: loose blue watercolor washes (#1E3AFF family) combined with fine technical ink linework. A crystal surface made of a hexagonal layer of glossy spherical atoms, a small molecule adsorbed on top, and translucent charge-density-difference lobes in blue and soft orange floating between the molecule and the surface. Wide 16:7 composition, generous white margins, no text, no numbers, no labels, no logos.`
- MD: `Watercolor scientific illustration on a pure white background, same style: loose teal watercolor washes (#00B79C family) with fine technical ink linework. Inside a faint dotted periodic simulation box, tangled polymer chains drawn as bead necklaces, and a few ions leaving dotted trajectories as they diffuse. Wide 16:7 composition, generous white margins, no text, no numbers, no labels, no logos.`
- COMSOL: `Watercolor scientific illustration on a pure white background, same style: loose amber watercolor washes (#FF8A00 family) with fine technical ink linework. A fingertip pressing a thin flexible printed film; the film surface carries a finite-element triangular mesh and a smooth potential color map flowing from blue through teal to orange under the pressed point. Wide 16:7 composition, generous white margins, no text, no numbers, no labels, no logos.`

## 5. 작업 방법

1. 사용 가능한 이미지 생성 도구로 만들고, 결과를 직접 열어 2절과 3절 기준(글자 없음, 색, 여백, 세 장의 통일감, 과학적 묘사)에 맞는지 확인합니다. 맞지 않으면 다시 생성합니다.
2. 1600×700 WebP로 저장해 2절의 경로에 둡니다.
3. `index.html`, `simulation-preview.html` 등 다른 파일은 수정하지 않습니다. 그림 반영은 Claude가 합니다.
4. 이 파일 맨 아래 6절에 결과(파일별 크기, 사용한 도구·모델, 확인 결과)를 적습니다.
5. 브랜치 `claude/dft-comsol-collaboration-message-i5z4cd`에 커밋합니다. 메시지: `Astra: 시뮬레이션 카드 일러스트 3장`. 푸시가 막히면 교수님께 `git push` 를 부탁합니다.

## 6. 결과 (Astra 작성)

제작 완료. 아래 판정은 Astra 자가점검 결과이고, 맨 아래에 Claude 검토 결과를 붙였습니다.

| 파일 | 크기(px) | 용량(KB, 1KB=1,000바이트) | 생성 횟수 |
|---|---|---:|---:|
| `image/simulation/illust-dft.webp` | 1600×700 | 76.3 (76,252바이트) | 1회 |
| `image/simulation/illust-md.webp` | 1600×700 | 72.2 (72,196바이트) | 1회 |
| `image/simulation/illust-comsol.webp` | 1600×700 | 82.6 (82,608바이트) | 1회 |

도구·모델: 내장 `image_gen`으로 생성(세부 모델 ID는 도구에서 공개하지 않음). 기존 연구 카드 5장을 직접 열고, `piezo.jpg`와 `energy.jpg`를 모든 생성 호출의 스타일 참조로 사용했습니다. System.Drawing으로 흰 여백 크롭·비율 유지 축소·흰 캔버스 중앙 배치 후 FFmpeg 7.1 `libwebp`, 품질 85로 저장했습니다. 프롬프트와 점검용 중간 파일은 저장소에 올리지 않았습니다.

| 자가점검 기준 | DFT | MD | COMSOL |
|---|---|---|---|
| 1. 글자·숫자·기호·로고·워터마크·서명 없음 | 통과 | 통과 | 통과 |
| 2. 흰 바탕·순백 모서리와 가장자리 | 통과 | 통과 | 통과 |
| 3. 핵심 피사체가 가운데 가로 75%·세로 80% 안에 있음 | 통과 | 통과 | 통과 |
| 4. 파랑·청록·호박색 주조색 구분 | 통과 | 통과 | 통과 |
| 5. 기존 카드와 같은 수채화 번짐·가는 기술 선화 | 통과 | 통과 | 통과 |
| 6. 세 장의 피사체 크기·위치·선·번짐 통일 | 통과 | 통과 | 통과 |
| 7. 요청한 과학 장면 묘사 | 통과 | 통과 | 통과 |
| 8. 장면 설명에 없는 장식 없음 | 통과 | 통과 | 통과 |

과학 장면 확인: DFT는 육각 원자층·표면 위 작은 분자·그 사이 파랑/옅은 주황 로브, MD는 점선 육면체 안의 구슬 사슬·이온·점선 궤적, COMSOL은 누름판과 얇은 필름의 접촉·삼각 메시·접촉점 아래를 중심으로 한 전위 색 변화를 확인했습니다. 과학 장면의 개념 일러스트이며 실제 계산 결과나 정량 검증을 뜻하지 않습니다.

최종 WebP를 다시 디코딩하여 각 장을 800×350px 타일 4개로 나누고 총 12개를 원본 배율로 직접 열어 전체와 네 모서리를 검사했습니다. 세 장 모두 20px 가장자리 띠 90,400개 화소와 네 모서리의 70×70px 영역은 각 채널 최솟값이 255이며, RGB 250 미만 화소는 0개입니다. 그림의 배치 영역도 안전 영역 x=200~1400, y=70~630 안에 있습니다.

비교 이미지 4개(각 그림을 기존 카드 2장과 나란히 붙인 것 3개, 세 장을 한 줄로 붙인 것 1개)를 만들어 직접 열어 확인했습니다.

남은 문제: 자가점검상 시각적 불통과 항목은 없습니다. HTML과 요청서 1~5절은 수정하지 않았습니다.

**Claude 검토 (2026-09-29, 교수님 PC)**: 통과. 세 장을 열어 2절·3절 기준으로 확인했습니다. 글자·숫자·로고 없음, 흰 바탕과 넉넉한 여백, 주조색(파랑·청록·호박색) 구분, `image/research/*.jpg` 와 같은 수채화 번짐과 가는 선화, 세 장의 구도 통일, 장면 묘사(육각 원자층 위 흡착 분자와 전하 밀도 차 로브, 점선 주기 상자 안의 구슬 사슬과 이온 궤적, 누름판 아래 삼각 메시와 전위 색 지도) 모두 요청과 맞습니다. 커밋·푸시는 Claude가 명령서 3절대로 했습니다.
