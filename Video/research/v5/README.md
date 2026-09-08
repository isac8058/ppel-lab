# 연구 단편 v5: 같은 출연진, 소리 있는 실사, 다섯 편 재제작

상태: **구상안. Astra 교차검증 회신 대기, Flow 파일럿 생성 대기.** 홈페이지는 아직 v4(네 편)와 v3(벚꽃)를 재생한다.

| 카드 | 제목 | 카드 색 | 논문 |
|---|---|---|---|
| AI 기반 인쇄전자 | 레드카펫 | ai-paper | Cellulose 2025, 10.1007/s10570-025-06542-7 |
| 바이오센서 | 교수님의 연필 | biosensor | ACS Nano 2025, 10.1021/acsnano.4c18646 |
| 인쇄형 메모리 | 만지지 마 | memory | Carbon 2024, 10.1016/j.carbon.2024.119320 |
| 인쇄형 에너지 저장 | 숨 참아 | energy-storage | Adv. Compos. Hybrid Mater. 2026, 10.1007/s42114-026-01862-z |
| 압전·마찰전기 | 잠깐만요! | cherry-blossom | Nano Energy 2026, 10.1016/j.nanoen.2025.111687 |

## 파일

| 파일 | 내용 | 대상 |
|---|---|---|
| `STORY_BIBLE.md` | 진단, 고정 사양, 출연진, 다섯 편 요약, 조크 원칙, 과학 락, 제작 흐름 | 교수님, Astra |
| `films.json` | 원본. 20개 클립의 비트, Flow 프롬프트, 재료 배정, 자막 초안, 포스터 프레임 | 스크립트 |
| `storyboard.html` | 단일 HTML 보드. 타임라인, 비트, 프롬프트 복사 버튼, 자막 미리보기. 브라우저에서 바로 연다 | 교수님, Astra |
| `PROMPT_PACK.md` | 스타일 블록이 앞에 붙은 20개 프롬프트와 재료 6장 프롬프트, 생성 순서대로 | Astra |
| `ASTRA_REVIEW_REQUEST.md` | 아이디어 단계 교차검증 질문 11개와 동시 진행 항목 | Astra |
| `ASTRA_FLOW_RUNBOOK.md` | Flow 프로젝트 구성, 재료, 파일럿, 생성 순서, 파일 규격, `clips.json` 형식 | Astra |
| `../../../scripts/build-v5-storyboard.cjs` | `films.json`에서 `storyboard.html`과 `PROMPT_PACK.md`를 생성 | Claude |
| `../../../scripts/assemble-v5.cjs` | 클립 4개 + 논문 카드 2초를 30초 완성본, 포스터, 한영 VTT로 조립 | Claude(워크스테이션) |

`storyboard.html`과 `PROMPT_PACK.md`를 직접 고치지 말고 `films.json`을 고친 뒤 `node scripts/build-v5-storyboard.cjs`를 실행한다.

## 진행 순서

1. Astra: `ASTRA_REVIEW_REQUEST.md` 회신(`ASTRA_REVIEW.md`)과 동시에 재료 6장, 파일럿 2클립 생성.
2. 교수님: 파일럿으로 화풍 승인(승인 1).
3. Astra: 나머지 18클립 생성, 편별 `clips.json` 기록, 상태를 `clips_ready`로.
4. Claude: 발화 시각에 자막 정렬, `node scripts/assemble-v5.cjs`, 완성본 검수(전체 디코드, 2fps 시트, ASR 대조).
5. 교수님: 편별 초안 승인(승인 2).
6. Claude: 홈페이지 연결 PR(경로 교체, 테스트의 v4 참조 교체, 빌드 스탬프 갱신).

## 조립 규격

각 완성본은 H.264/AAC, 1280×720, 24 fps, faststart, 정확히 30초. 클립 4개에서 7초씩 28초를 쓰고 2초 논문 카드로 끝난다. 자막은 영상에 굽지 않고 홈페이지 하단 패널에서 VTT로 표시한다. 조립 스크립트는 FFmpeg와 `@napi-rs/canvas`가 있는 워크스테이션에서 실행한다(`FFMPEG_PATH`, `NODE_PATH`는 기존 v3 스크립트와 같다).

## 표현 범위

다섯 편은 연구 개념의 코미디 연출이며 실험 촬영이나 진단 시연이 아니다. 홈페이지의 AI 연출 안내 문구는 유지한다. 과학 락은 `films.json`의 편별 `scienceLock`에 있고 `STORY_BIBLE.md` 6절에 요약되어 있다.
