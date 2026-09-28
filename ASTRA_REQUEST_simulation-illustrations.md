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

(작성 전)
