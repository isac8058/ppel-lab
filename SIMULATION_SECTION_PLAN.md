# 시뮬레이션 협업 홍보 섹션 계획 (DFT · COMSOL · MD)

작성 2026-09-28 · 대상 `index.html` · 상태: 내용 확정, 시안 완료 (`simulation-preview.html`), 교수님 시안 확인 대기

## 1. 목적

- **누구에게**: 실험 결과의 기전 설명이 필요한 국내외 실험 연구실과 기업 연구소. 리뷰어가 계산 근거를 요구해 막힌 연구자가 핵심 대상입니다.
- **무엇을**: PPEL이 DFT와 COMSOL 계산을 직접 수행하고, 그 계산이 이미 게재 논문에 쓰였다는 근거를 보여 준 뒤, 공동연구와 분석 의뢰 문의로 연결합니다. MD는 준비 중으로 예고합니다.
- **성공 기준**: 방문자가 30초 안에 세 가지를 파악합니다. 무엇을 계산해 주는지, 믿을 근거가 있는지, 어떻게 연락하는지.

## 2. 교수님 결정 (2026-09-28)

| 항목 | 결정 |
|---|---|
| 논문 목록 | Claude가 조사해 확정 (아래 3절) |
| 수행 항목 범위 | 논문 실적 항목 + 수행 가능 항목 모두 표기 |
| 협업 조건 | 공동연구 + 분석 의뢰 모두 받음, 세부 조건은 메일 협의 |
| 배치 | 연구 섹션 바로 뒤, 상단 메뉴와 바닥글에 시뮬레이션 탭 추가 |
| MD | 시기 없이 준비 중으로 표기 |

## 3. 근거 논문 (확정 7편)

**포함 기준**: 임수만 교수님이 교신저자(또는 공동 교신)이고, 초록이나 본문에 DFT, COMSOL 계산이 명시된 논문. 조사는 연구 영상 자료와 웹 검색 결과로 했습니다(작업 환경에서 출판사 사이트 접속이 막혀 원문과 SI는 직접 열지 못함).

| 연도 | 논문 | 저널 · IF | 계산 | 계산으로 밝힌 것 | 근거 |
|---|---|---|---|---|---|
| 2026 | Sulfated Cellulose Nanocrystals into Piezoelectricity | Adv. Compos. Hybrid Mater. · 21.8 | DFT + COMSOL | 쌍극자 모멘트 3.2 D에서 11.0 D (3.4배), 하중 시 더 큰 압전 전위 | 연구 영상 번쩍 셀룰로스 |
| 2026 | Oxygen-scavenging MnO₂ nanoparticles ... MXene inks | Adv. Compos. Hybrid Mater. · 21.8 | DFT | MnO₂가 산소와 먼저 상호작용해 MXene 산화 억제 | 초록, 연구 영상 작전명: 산화 |
| 2026 | Cherry Blossom TENG, gesture recognition | Nano Energy · 16.8 | DFT | 접촉 계면의 전하 이동 기전 | 연구 영상 벚꽃 파이터 |
| 2026 | Ti₃C₂Tₓ MXene Nanosheets: Bridging High-Performance Energy Storage and ... Biocompatibility | ACS Appl. Mater. Interfaces | DFT | 금속성 Ti–C 골격과 O/F 말단기의 빠른 전자 수송 | 초록 (공동 교신) |
| 2026 | First-Principles Investigation of Glucose Adsorption ... on Ti₃C₂O₂ MXene | Micromachines | DFT | 포도당 흡착 에너지 −0.82 eV, 전자 구조 변화 | 초록 |
| 2025 | Structural transformation of g-C₃N₄ from 2D to 1D | Chem. Eng. J. · 13.4 | COMSOL | 속이 빈 나노튜브가 압전 출력을 높이는 이유 | 초록 |
| 2022 | A Screen-Printed Metal Hybrid Composite for Wireless Wind Sensing | Nanomaterials | COMSOL | 인장 시 균열 해석(J-적분)으로 저항 변화 원리 규명 | 본문 (COMSOL 5.6) |

- 합계: 7편, DFT 5편, COMSOL 3편. MD를 쓴 논문은 없음.
- 제외: 초록에 계산이 없거나 확인 불가(AFM 2025 PVDF TENG, CEJ 2026 한지 패치, JAC 2025 리보플라빈, EPJ 2025 마이크로니들 등), 리뷰 논문(IJER 2026 아연 음극), 우리 연구실 논문이 아님(J. Mater. Sci.: Mater. Electron. 2023 PENG, Nano Energy 2023 삼원 복합체 PENG).
- 교수님이 원문이나 SI에만 계산이 있는 논문을 알려 주시면 추가합니다.

**기존 논문 목록의 DOI 오류 2건 (반영 단계에서 함께 수정)**

| 논문 | 현재 사이트 DOI (오류) | 올바른 DOI | 사이트 내 위치 |
|---|---|---|---|
| g-C₃N₄ 2D에서 1D, 압전 (CEJ 2025) | `10.1016/j.cej.2024.157858` (디젤 탈황 연구, Salonikidou 외) | `10.1016/j.cej.2025.165069` | 연구 카드 1곳, 논문 목록 2곳 |
| 금속 황화물-MXene 슈퍼커패시터 (JMCA 2024) | `10.1039/D4TA01234H` (리튬 금속 전지 분리막 논문) | `10.1039/D4TA01551G` | 연구 카드 1곳, 논문 목록 2곳 |

## 4. 섹션 구성 (시안 반영)

1. **머리말**: 시뮬레이션 협업 / 실험은 현상을 보여 주고, 계산은 그 이유를 밝힙니다. / 소개 한 문단 / 협업 문의 버튼, 게재 논문 보기 버튼
2. **원자에서 소자까지**: 길이 축(Å, nm, µm~mm) 아래 DFT, MD(준비 중, 점선 카드), COMSOL 카드 3개. 카드마다 자체 SVG 삽화, 답하는 질문, 산출물 목록(채운 점 = 게재 논문 실적, 빈 점 = 요청 시 수행 가능), 사용 코드
3. **계산이 쓰인 게재 논문**: 7편 행 목록(연도, 제목, 계산으로 밝힌 것, 저널, DFT/COMSOL 배지, IF, 연구 영상 링크 또는 DOI)
4. **협업 진행 방식**: 공유 → 설계 → 계산·전달 → 투고 지원, 그리고 공동연구 / 분석 의뢰 두 방식
5. **문의**: 어두운 띠 카드. 보내 주실 정보 4가지, 메일 버튼(제목과 본문 양식이 언어에 맞게 자동 입력), 주소, 세부 조건은 메일 협의

## 5. 디자인·기술 원칙

- 기존 색 토큰 재사용: DFT = 전도성 파랑, MD = 전류 청록, COMSOL = 호박색(글자는 에너지 저장 카드와 같은 대비 검증 색). 라이트·다크 모두 적용.
- 삽화는 자체 SVG(전하 밀도 차 로브, 분자 사슬과 이온 궤적, 유한요소 메시와 전위 분포). 논문 그림은 쓰지 않습니다.
- 움직임은 기존 등장 효과(`.reveal`)와 카드 hover만 씁니다. 모션 감소 설정에 따라 멈추는 새 애니메이션은 넣지 않습니다(CLAUDE.md 참고).
- 한·영 전환은 기존 `data-en` / `data-ko` 방식, 메일 링크는 `ppel:language` 이벤트로 언어 전환.
- 메타 설명·키워드와 구조화 데이터(knowsAbout)에 DFT, COMSOL 추가.
- 메뉴 10개 수용: 영어 981~1180px에서 넘치므로 메뉴 간격을 줄이고 필요하면 햄버거 전환 폭 조정.
- 바닥글 빌드 번호 갱신, CHANGELOG 기록.

## 6. 진행 순서

1. ~~내용 확정~~ 완료
2. ~~시안~~ 완료: `simulation-preview.html` (한·영, 라이트·다크 전환 버튼 포함)
3. **반영**: 교수님 시안 확인 후 `index.html`에 섹션, 메뉴·바닥글 탭, 메타 정보, DOI 2건 수정
4. **검증**: headless Chromium으로 일반 + 모션 감소 두 환경, 한·영, 라이트·다크, 360~1920px 폭에서 가로 넘침·메뉴 넘침·대비 확인. `tests/design-polish.cjs`의 메뉴 목록에 `#simulation` 추가
5. **배포**: PR 생성 → main 병합(스쿼시) → 약 1분 뒤 사이트 반영, 바닥글 빌드 번호로 최신본 확인
