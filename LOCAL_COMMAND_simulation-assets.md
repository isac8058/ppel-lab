# 명령서: 시뮬레이션 섹션 그림 준비 (교수님 PC, 바탕화면 폴더에서 실행)

작성 2026-09-28 · 실행 주체: 교수님 PC의 Claude Code 세션(바탕화면 폴더) · 그림 생성: Astra(Codex CLI)

## 목표

PPEL+ 홈페이지 시뮬레이션 협업 섹션에 넣을 두 가지를 만들어 GitHub 브랜치에 올린다.

1. 바탕화면의 최근 논문에서 DFT 내용과 DFT 그림 발췌
2. 카드 일러스트 3장 (Astra에게 맡김)

## 0. 저장소 준비

```
cd <바탕화면>
git clone https://github.com/isac8058/ppel-lab.git   # 이미 있으면 생략
cd ppel-lab
git fetch origin
git checkout claude/dft-comsol-collaboration-message-i5z4cd
git pull
```

## 1. DFT 발췌 (바탕화면의 논문 PDF, DOCX)

대상: 바탕화면(하위 폴더 포함)에 있는 아래 게재 논문. 파일명이 달라도 제목으로 찾는다.

| 약칭 | 논문 | DOI |
|---|---|---|
| cherry | Self-Powered Gesture Recognition Using a Sustainable and Thermally Stable Cherry Blossom TENG (Nano Energy 2026) | 10.1016/j.nanoen.2025.111687 |
| scnc | Sulfated Cellulose Nanocrystals into Piezoelectricity (Adv. Compos. Hybrid Mater. 2026) | 10.1007/s42114-026-01819-2 |
| mno2 | Oxygen-scavenging MnO₂ nanoparticles ... MXene inks (Adv. Compos. Hybrid Mater. 2026) | 10.1007/s42114-026-01862-z |
| mxene | Ti₃C₂Tₓ MXene Nanosheets: Bridging High-Performance Energy Storage ... (ACS Appl. Mater. Interfaces 2026) | 10.1021/acsami.6c05337 |
| glucose | First-Principles Investigation of Glucose Adsorption ... on Ti₃C₂O₂ MXene (Micromachines 2026) | 10.3390/mi17040489 |

바탕화면에 DFT가 들어간 다른 최근 논문이 있으면 함께 본다. 투고 중이거나 수정 중인 미게재 원고는 그림을 쓰지 않고 결과표에 미게재로만 적는다.

논문마다 할 일:

1. **계산 조건**: 코드(Quantum ESPRESSO, VASP 등), 범함수(PBE 등), 분산 보정, 컷오프 에너지, k-점, 계산 모델(슬래브, 분자, 단위 셀).
2. **계산한 것과 핵심 수치**: 흡착 에너지, 전하 이동량(Bader), 쌍극자 모멘트, DOS 변화 등. 원본 그림 번호를 함께 적는다.
3. **DFT 그림 1장**: 해당 Figure에서 DFT 패널(전하 밀도 차, 흡착 구조, DOS 등)을 잘라 JPG로 저장한다.
   - 경로: `image/simulation/dft-<약칭>.jpg` (예: `dft-cherry.jpg`)
   - 가로 최대 1100 px, 품질 85, 250 KB 이하
   - 패널 기호와 축 글자는 둬도 되고, 저널 로고나 워터마크는 잘라낸다.
4. 결과를 `docs/simulation/dft-extract.md` 에 표로 정리한다.
   열: 약칭, 논문, DOI, 계산 조건, 계산한 것, 핵심 수치, 그림 파일, 원본 그림 번호, 게재 여부.
   원문에서 확인하지 못한 칸은 확인 못 함으로 적고, 추정해서 채우지 않는다.

## 2. 카드 일러스트 3장 (Astra)

저장소 루트의 `ASTRA_REQUEST_simulation-illustrations.md` 를 Astra에게 맡긴다.

```
codex exec -s workspace-write "Read ASTRA_REQUEST_simulation-illustrations.md in the repository root and follow it exactly."
```

결과 파일: `image/simulation/illust-dft.webp`, `illust-md.webp`, `illust-comsol.webp` (각 1600×700). 세 장을 열어 보고 글자가 없는지, 기존 연구 카드 그림(`image/research/*.jpg`)과 필치가 맞는지 확인한다. 맞지 않으면 Astra에게 다시 시킨다.

## 3. 올리기

```
git add image/simulation docs/simulation ASTRA_REQUEST_simulation-illustrations.md
git commit -m "시뮬레이션 섹션 그림: DFT 논문 발췌와 카드 일러스트"
git push origin claude/dft-comsol-collaboration-message-i5z4cd
```

`index.html` 과 `simulation-preview.html` 은 고치지 않는다. 반영은 클라우드 세션의 Claude가 한다.

## 4. 보고

교수님께 짧게 보고한다: 올린 파일 목록, 찾지 못한 논문, 미게재로 뺀 논문, Astra 그림 확인 결과.
