# Astra 교차검증 요청: 벚꽃 단편 v4 구상안

요청자: Claude Code (2026-09-07). 수신: Astra. 상태: **회신 대기**. 회신 전까지 v4 구상안은 확정안이 아니다.

교수님 지시: 아이디어 단계에서도 항상 교차검증한다. 이 문서는 그 절차의 첫 적용이다.

## 읽어야 할 파일

1. `CLAUDE_BLENDER_CONCEPT.md`: 훅 7개, 14컷 샷 리스트, 자막, 사운드, Blender 설계도, 과학 락, 대안, 결정 항목
2. `shotlist.json`: 같은 내용의 기계 판독용 사본
3. `storyboard.html`: 14컷 스케치와 30초 타임라인, 자막 패널 플레이어
4. `blender/petal_ground_poc.py`와 `poc/petal-ground-poc.png`: 개념 검증 스크립트와 렌더
5. 배경: `../v3/README.md`, `../v3/edit-plan.json`, `../v2/CLAUDE_PRODUCTION_LOCK.md`

## 질문

### A. 아이디어 단계 (시청자 관점, 자유롭게 반대해도 된다)

1. 훅 7개 중 시청자 입장에서 약하거나 상투적인 것은 무엇이고, 무엇으로 바꾸겠는가.
2. 얼굴 없이 파란 니트릴 장갑과 빨간 점박이 코팅장갑으로만 두 인물을 연기하는 방식이 v3의 웃음을 유지하는가. 전신 캐릭터가 꼭 필요한 컷이 있다면 어느 컷인가.
3. 30초에 14컷(평균 2.1초)은 적절한가. 병합하거나 늘려야 할 컷을 지정해 달라.
4. 컷 6(지퍼 슬라이더 와이프)과 컷 11(파형이 점 무리 둘로 갈라지는 분류 시각화)이 설명 없이 이해되는가.
5. 포스터 프레임을 3.4초(슬로모 낚아채기)로 잡은 것에 동의하는가. 다른 후보가 있는가.

### B. Blender 실행 가능성

6. 장갑 손 2종: MakeHuman 또는 Blender Studio Human Base Meshes(CC0) 팔 + Rigify 방식이 실제로 다룰 수 있는 범위인가. 더 나은 방법이 있는가.
7. 컷 2~3의 리지드 바디 낚아채기(꽃잎 200장 + 패시브 빗자루)와 소매 클로스 시뮬을 bpy 스크립트로 통제할 수 있는가, GUI 작업이 필요한 부분은 어디인가.
8. 사용 가능한 렌더 장비(GPU 유무, VRAM)와 Blender 버전. 이에 따라 Cycles 컷(1, 5)과 EEVEE 컷 배분을 조정해야 하는가.
9. `blender/petal_ground_poc.py`가 Astra의 환경에서 그대로 실행되는가. 실행 시간과 문제점을 적어 달라.
10. 제작 기간 추정치. 문서의 3~5일은 숙련자 기준 가정치이므로 Astra 기준으로 다시 잡아 달라. 승인 지점 2개의 위치도 조정 가능하다.

### C. 과학 표현 락

11. 14컷 중 과학 락(꽃잎은 소자의 한 층, 신호는 접촉·분리, ML은 한 번·두 번 탭 구별, 계측기는 별도 전원, 화면 안 글자 0)을 어길 소지가 있는 컷이 있는가.

## 회신 형식

같은 폴더에 `ASTRA_REVIEW.md`로 저장해 달라. 항목별로 다음 표를 채우고, 마지막에 가장 큰 위험 3개를 적어 달라.

| 번호 | 판단 (동의 / 수정 / 반대) | 근거 | 대안 또는 수정안 |
|---|---|---|---|

회신을 받으면 Claude가 샷 리스트, `shotlist.json`, 제작 순서를 수정하고 `README.md`의 상태를 교차검증 완료로 바꾼다. 의견이 갈리는 항목은 교수님이 결정한다.

## English summary for Astra

Please cross-check the v4 concept (files above) and save your answers as `ASTRA_REVIEW.md` in this folder using the table format: item number, verdict (agree / revise / disagree), reasoning, alternative. Questions: A1 weak hooks and replacements; A2 does the faceless glove-only staging keep the v3 comedy, and which cuts would need a full-body character; A3 is 14 cuts in 30 s right, which to merge or extend; A4 are the zipper wipe (cut 6) and the two-cluster classification visual (cut 11) understandable without narration; A5 is 3.4 s the right poster frame. B6 feasibility of the glove hand rigs (MakeHuman or Blender Studio base meshes + Rigify); B7 can the rigid-body petal snatch and cloth sleeve be driven from bpy scripts, where is GUI work unavoidable; B8 your render hardware and Blender version, and whether the Cycles/EEVEE split should change; B9 does `blender/petal_ground_poc.py` run as is in your environment, with timing; B10 your own schedule estimate and approval-point placement. C11 any cut that risks the science lock (petal is one layer of the device, signal from contact and separation, ML distinguishes single vs double taps, readout on separate mains power, zero on-screen text). End with the top three risks.
