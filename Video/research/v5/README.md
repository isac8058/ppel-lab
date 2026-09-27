# PPEL research films v5 — current homepage edition

Ten 36-second films, two per research card. Each film has separate Korean and English video files with baked-in text on the same frame-aligned timeline. Exports: 1920×1080, 30 fps, H.264 + AAC, faststart.

## Production

Claude가 코드로 만든 절차적 애니메이션과 직접 합성한 음악·효과음으로 제작했다. AI 영상 생성 서비스는 사용하지 않았다. 과학 문구는 논문 원문·초록을 기준으로 Astra가 교차 검토했다. 이 제작 이력은 제공 미디어의 제작 기록이며, 홈페이지 연동 검증과 구분한다.

Animated dramatization · figures from the paper, not experimental footage.
애니메이션 연출 · 수치는 논문 기준, 실제 실험 영상 아님

## Films

| Card | Order | Stem | English title | 한국어 제목 | Paper DOI |
|---|---|---|---|---|---|
| ai-paper | 1 | ai-paper | MISSION: HANJI-POSSIBLE | 미션 한지파서블 | [10.1007/s10570-025-06542-7](https://doi.org/10.1007/s10570-025-06542-7) |
| ai-paper | 2 | ai-paper-2 | FILM OF ROCK | 필름 오브 록 | [10.1002/adfm.202424271](https://doi.org/10.1002/adfm.202424271) |
| biosensor | 1 | biosensor | PENCIL NOIR | 연필 형사 | [10.1021/acsnano.4c18646](https://doi.org/10.1021/acsnano.4c18646) |
| biosensor | 2 | biosensor-2 | HANJI HERO | 한지 히어로 | [10.1016/j.cej.2026.178008](https://doi.org/10.1016/j.cej.2026.178008) |
| memory | 1 | memory | FAST & RESISTIVE | 저항의 질주 | [10.1016/j.carbon.2024.119320](https://doi.org/10.1016/j.carbon.2024.119320) |
| memory | 2 | memory-2 | A SPOONFUL OF DOPAMINE | 도파민 한 스푼 | [10.1016/j.orgel.2025.107305](https://doi.org/10.1016/j.orgel.2025.107305) |
| energy-storage | 1 | energy-storage | OPERATION OXIDATION | 작전명: 산화 | [10.1007/s42114-026-01862-z](https://doi.org/10.1007/s42114-026-01862-z) |
| energy-storage | 2 | energy-storage-2 | MXene VOYAGE | MXene 결사대 | [10.1021/acsami.6c05337](https://doi.org/10.1021/acsami.6c05337) |
| cherry-blossom | 1 | cherry-blossom | PETAL FIGHTER | 벚꽃 파이터 | [10.1016/j.nanoen.2025.111687](https://doi.org/10.1016/j.nanoen.2025.111687) |
| cherry-blossom | 2 | cherry-blossom-2 | CLEAN & CHARGE | 번쩍 셀룰로스 | [10.1007/s42114-026-01819-2](https://doi.org/10.1007/s42114-026-01819-2) |

## File list

`films.json` records card, stem, order, bilingual titles, DOI, and duration (36 seconds). This directory also contains `README.md` and the following 60 media files:

- `ai-paper-ko.mp4`, `ai-paper-en.mp4`, `ai-paper-ko.jpg`, `ai-paper-en.jpg`, `ai-paper.ko.vtt`, `ai-paper.en.vtt`
- `ai-paper-2-ko.mp4`, `ai-paper-2-en.mp4`, `ai-paper-2-ko.jpg`, `ai-paper-2-en.jpg`, `ai-paper-2.ko.vtt`, `ai-paper-2.en.vtt`
- `biosensor-ko.mp4`, `biosensor-en.mp4`, `biosensor-ko.jpg`, `biosensor-en.jpg`, `biosensor.ko.vtt`, `biosensor.en.vtt`
- `biosensor-2-ko.mp4`, `biosensor-2-en.mp4`, `biosensor-2-ko.jpg`, `biosensor-2-en.jpg`, `biosensor-2.ko.vtt`, `biosensor-2.en.vtt`
- `memory-ko.mp4`, `memory-en.mp4`, `memory-ko.jpg`, `memory-en.jpg`, `memory.ko.vtt`, `memory.en.vtt`
- `memory-2-ko.mp4`, `memory-2-en.mp4`, `memory-2-ko.jpg`, `memory-2-en.jpg`, `memory-2.ko.vtt`, `memory-2.en.vtt`
- `energy-storage-ko.mp4`, `energy-storage-en.mp4`, `energy-storage-ko.jpg`, `energy-storage-en.jpg`, `energy-storage.ko.vtt`, `energy-storage.en.vtt`
- `energy-storage-2-ko.mp4`, `energy-storage-2-en.mp4`, `energy-storage-2-ko.jpg`, `energy-storage-2-en.jpg`, `energy-storage-2.ko.vtt`, `energy-storage-2.en.vtt`
- `cherry-blossom-ko.mp4`, `cherry-blossom-en.mp4`, `cherry-blossom-ko.jpg`, `cherry-blossom-en.jpg`, `cherry-blossom.ko.vtt`, `cherry-blossom.en.vtt`
- `cherry-blossom-2-ko.mp4`, `cherry-blossom-2-en.mp4`, `cherry-blossom-2-ko.jpg`, `cherry-blossom-2-en.jpg`, `cherry-blossom-2.ko.vtt`, `cherry-blossom-2.en.vtt`

## Homepage integration and checks

Both start posters are visible in a vertical stack inside each card, including mobile. Video MP4 sources stay unset until a start button is pressed. Language switching updates the video itself, posters, fallback links and the separate subtitle panel. Loaded players restore their playback time and paused/playing state; only one film can play at a time. Fullscreen includes the subtitle panel.

Run `node tests/research-films-static.cjs` from the repository root for dependency-free static validation. Run `node tests/research-film-state.cjs` for source-switch state-machine checks. With Playwright and Chromium installed, serve this repository over HTTP with byte-range support and run `node tests/research-captions.cjs` (`TEST_URL`, optional `CHROME_PATH`). The browser test covers all ten films, both languages, time preservation within 0.5 seconds, exclusive playback, fullscreen, errors and mobile/reduced-motion behavior.

The v1–v4 directories and legacy rendering scripts are historical assets; they do not rebuild v5.
