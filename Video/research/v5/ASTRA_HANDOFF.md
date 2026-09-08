# Astra 전달문 (교수님이 Astra에게 그대로 붙여 넣는 글)

---

Astra, PPEL 연구 단편 v5 재제작을 시작한다. 자료는 GitHub 저장소 isac8058/ppel-lab의 브랜치 claude/festive-cray-rmupjl, 폴더 Video/research/v5 에 있다.

폴더 주소: https://github.com/isac8058/ppel-lab/tree/claude/festive-cray-rmupjl/Video/research/v5

로컬 클론이 있으면 다음으로 받는다.

    git fetch origin claude/festive-cray-rmupjl
    git checkout claude/festive-cray-rmupjl

읽는 순서: README.md → STORY_BIBLE.md → ASTRA_REVIEW_REQUEST.md → ASTRA_FLOW_RUNBOOK.md → PROMPT_PACK.md. storyboard.html은 브라우저로 열면 편별 비트, 프롬프트 복사 버튼, 자막 미리보기가 있다. 원본 데이터는 films.json이다.

할 일(동시 진행):

1. ASTRA_REVIEW_REQUEST.md의 질문 11개에 답해 같은 폴더에 ASTRA_REVIEW.md로 저장한다(표 형식은 요청서에 있다).
2. 기다리지 말고 Google Flow에서 재료 이미지 6장(films.json의 ingredients)과 파일럿 클립 2개(5편 클립 1 다이빙, 1편 클립 2 걸음 3종)를 먼저 만든다. 저장 위치와 파일 이름은 ASTRA_FLOW_RUNBOOK.md 4절을 따른다.
3. 결과물(ASTRA_REVIEW.md, ingredients/, pilot/)은 같은 브랜치 claude/festive-cray-rmupjl에 커밋하고 푸시한다. 푸시 권한이 없으면 로컬 클론의 같은 폴더에 저장하고 나에게 알려라.

규칙: 화면 안 글자 0, 한국어 대사는 프롬프트의 큰따옴표 안 문장을 그대로, 재료는 클립에 적힌 것만 최대 3장, 모든 시도는 clips.json에 기록. 프롬프트를 고쳐야 하면 고친 전체 문장을 clips.json의 promptUsed에 남긴다.

파일럿 2개가 나오면 나에게 보여라. 그 승인 뒤 나머지 18개 클립을 생성 순서 5 → 1 → 4 → 2 → 3으로 진행한다.

---

## English version

Astra, we are remaking the five PPEL research shorts (v5). Everything is in the GitHub repo isac8058/ppel-lab, branch claude/festive-cray-rmupjl, folder Video/research/v5 (https://github.com/isac8058/ppel-lab/tree/claude/festive-cray-rmupjl/Video/research/v5). With a local clone: `git fetch origin claude/festive-cray-rmupjl && git checkout claude/festive-cray-rmupjl`.

Read in this order: README.md, STORY_BIBLE.md, ASTRA_REVIEW_REQUEST.md, ASTRA_FLOW_RUNBOOK.md, PROMPT_PACK.md. Open storyboard.html in a browser for per-clip beats, copy buttons and a caption preview; films.json is the source data.

Do these in parallel: (1) answer the 11 questions in ASTRA_REVIEW_REQUEST.md and save them as ASTRA_REVIEW.md in the same folder; (2) without waiting, generate the six ingredient images (films.json → ingredients) and the two pilot clips (film 5 clip 1, film 1 clip 2) in Google Flow, saved exactly as section 4 of ASTRA_FLOW_RUNBOOK.md specifies; (3) commit and push ASTRA_REVIEW.md, ingredients/ and pilot/ to the same branch, or save them into the local clone and tell me if you cannot push.

Rules: zero on-screen text, keep the quoted Korean dialogue verbatim, attach only the listed ingredients (max 3), log every take in clips.json, and record any changed prompt in full under promptUsed. Show me the two pilots; after approval, generate the remaining 18 clips in film order 5, 1, 4, 2, 3.

---

## 교수님 메모

- Astra가 회신과 파일럿을 브랜치에 올리면 이 Claude 세션(또는 새 세션)에 이어서라고만 말씀해 주시면 자막 정렬, 조립, 홈페이지 연결을 진행합니다.
- storyboard.html은 GitHub 화면에서는 소스로만 보이고, 브라우저에서 파일을 직접 열어야 렌더링됩니다. main에 합쳐지면 https://isac8058.github.io/ppel-lab/Video/research/v5/storyboard.html 로도 열립니다.
