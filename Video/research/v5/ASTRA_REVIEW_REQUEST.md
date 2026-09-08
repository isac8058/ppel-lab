# Astra 교차검증 요청: 연구 단편 v5 (5편 재제작)

요청자: Claude Code (2026-09-08). 수신: Astra. 상태: **회신 대기**.
교수님 지시: 현재 영상은 재미가 없고 연출이 어색하다. 스토리를 다시 짜서 Google Flow로 다시 만든다. 빠른 진행을 위해 Astra가 돕는다.

교수님 규칙에 따라 아이디어 단계에서 교차검증한다. 다만 이번에는 속도가 우선이므로 **검토와 파일럿 생성을 동시에** 진행한다(아래 3절).

## 읽어야 할 파일

1. `STORY_BIBLE.md`: 진단, 고정 사양, 출연진, 다섯 편 요약, 조크 원칙, 과학 락
2. `films.json`: 20개 클립의 비트(한국어)와 Flow 프롬프트(영어), 자막 초안, 재료 배정
3. `storyboard.html`: 위 내용을 브라우저에서 보는 보드(프롬프트 복사 버튼 포함)
4. `ASTRA_FLOW_RUNBOOK.md`: 생성 순서와 파일 규격
5. 배경: `../v4/README.md`(현재 게시본), `../v3/README.md`와 `../v3/edit-plan.json`(Astra가 검수했던 벚꽃편)

## 질문

### A. 이야기(시청자 관점, 자유롭게 반대해도 된다)

1. 다섯 편 중 가장 약한 편은 무엇이고 어떻게 고치겠는가. 특히 3편(만지지 마)은 메모리 은유가 30초 안에 읽히는가.
2. 각 편의 정점(레드카펫 질주, 연필통 헌납, 모든 것을 만짐, 스노클 취침, 미화원의 직접 탭)이 자막 없이도 웃긴가. 자막을 꺼도 이해되지 않는 컷을 지목해 달라.
3. 다섯 편이 같은 출연진의 미니 시리즈라는 설정이 홈페이지 방문자에게 이득인가, 아니면 편마다 독립이 낫나.
4. 실사 시네마틱 코미디로 통일한 판단에 동의하는가. 벚꽃편만 v3 애니메이션 화풍을 유지하는 편이 나은가.

### B. Flow 실행 가능성

5. 클립당 한국어 대사 2문장(각 10자 내외)을 Veo가 입에 맞춰 안정적으로 발화하는가. 최근 경험상 실패율과 대응(대사 줄이기, 발음 표기 병기)을 알려 달라.
6. 재료 3장(인물 2 + 세트 1)으로 20개 클립의 인물 일관성이 유지되는가. 재료 이미지를 Flow 안에서 만들지, 다른 이미지 생성기에서 만들지 권고해 달라.
7. 2편 클립 3, 5편 클립 3처럼 한 클립 안에 컷이 하나 있는 프롬프트(SHOT A, SHOT B)는 위험한가. 위험하다면 별도 클립 2개로 나누고 각 4초만 쓰는 방안에 동의하는가(크레딧 증가).
8. 특수 소품(풀페이스 스노클 마스크, 유리 종 덮개, 벨벳 쿠션, 악어클립 비커 셀, 빗살 패턴 유연 필름)이 Veo에서 안정적으로 나오는가. 대체 소품 제안.
9. 크레딧 추정: 20클립 × (초안 2회 Fast + 최종 1회 최고 등급). 현재 Flow 요금과 남은 크레딧 기준으로 총량과 부족분을 적어 달라.
10. Astra 기준 일정 추정과 승인 지점 위치. 제안: 승인 1 = 파일럿 2클립 후, 승인 2 = 편별 4클립 초안 후.

### C. 과학 락

11. `films.json`의 각 편 `scienceLock`을 어길 소지가 있는 컷이 있는가. 특히 2편(환자·진단 노출), 4편(잉크 부활, 맨손 분말), 5편(계측 전원)을 봐 달라.

## 회신 형식

같은 폴더에 `ASTRA_REVIEW.md`로 저장해 달라. 항목별로 다음 표를 채우고, 마지막에 가장 큰 위험 3개를 적어 달라.

| 번호 | 판단 (동의 / 수정 / 반대) | 근거 | 대안 또는 수정안 |
|---|---|---|---|

## 3. 동시 진행(속도 우선)

회신을 기다리는 동안 다음은 바로 시작해도 된다. 스토리가 바뀌어도 출연진과 화풍은 유지되므로 낭비가 없다.

- 재료 이미지 6장 생성(`films.json`의 `ingredients`), `v5/ingredients/I1.png`~`I6.png`
- 파일럿 클립 2개: 5편 클립 1(다이빙), 1편 클립 2(걸음 3종). `v5/pilot/`에 저장
- 파일럿 2fps 컨택트 시트와 발화 시각 메모

회신을 받으면 Claude가 `films.json`, `storyboard.html`, 생성 순서를 수정하고 `README.md`의 상태를 교차검증 완료로 바꾼다. 의견이 갈리는 항목은 교수님이 결정한다.

## English summary for Astra

Please cross-check the v5 concept (files above) and save your answers as `ASTRA_REVIEW.md` in this folder, one table row per item (verdict agree / revise / disagree, reasoning, alternative), ending with the top three risks. A1 weakest film and fix, especially whether film 3's memory metaphor reads in 30 s; A2 which payoffs fail without captions; A3 shared-cast mini-series vs independent films; A4 live-action for all five vs anime for the cherry film only. B5 reliability of two short Korean lines per 8 s clip in Veo, and mitigations; B6 whether three ingredients (two characters + one set) hold identity across 20 clips, and where to make the ingredient images; B7 risk of one internal cut per clip (film 2 clip 3, film 5 clip 3) vs splitting into two clips; B8 prop reliability (full-face snorkel mask, bell jar, velvet cushion, alligator-clip beaker cell, interdigitated flexible film); B9 credit estimate for 20 clips × (2 Fast drafts + 1 top-tier final) against the current plan; B10 your schedule and approval points. C11 any cut that risks the per-film `scienceLock` in `films.json`. In parallel, please start the six ingredient images and the two pilot clips (film 5 clip 1, film 1 clip 2) as described in `ASTRA_FLOW_RUNBOOK.md`.
