# PPEL+ 연구 단편 5편 — 전면 재작업 시나리오 (v2)

> Claude 작성 초안입니다. 제작에는 [프로덕션 락 부록](CLAUDE_PRODUCTION_LOCK.md)을 우선 적용합니다. 특히 전기화학 박리 공정, 자막 시간, 산화 완화, 메모리의 상태 유지 묘사가 수정되었습니다.

## A) 공통 비주얼 트리트먼트 & 실패 원인

기존 5편은 "귀여운 사물 의인화 + 말장난"이라는 유아용 문법에 갇혀 있었고, 시청자가 감정이입할 인간도, 1초 안에 시선을 붙잡는 사건도, 진짜 웃음 포인트(비주얼 개그의 반전)도 없었습니다. 이번 버전은 **90년대 극장판 일본 애니메이션 룩(셀 셰이딩, 필름 그레인, 진지한 성인 작화)으로 그린 연구실 직장 코미디**로 통일하고, 진지한 연출 문법(사무라이 대치, 순정만화 벚꽃, 호러 조명)을 연구실 일상에 정색하고 갖다 붙여서 웃기는 "데드팬 세인넨 개그"를 핵심 톤으로 삼습니다.

### 고정 출연진 (5편 공통 — 캐릭터 시트 1회 제작 후 재사용, 제작비 절감의 핵심)

| 캐릭터 | 설정 | 프롬프트용 영문 고정 서술 |
|---|---|---|
| **백도윤** (29, 대학원생) | 헝클어진 검은 머리, 둥근 철테 안경, 랩코트 안에 낡은 갈색 가디건. 진심 100%의 열정형 사고뭉치 | DOYUN: Korean man in his late 20s, messy black hair, round wire-frame glasses, worn brown cardigan under an open white lab coat, earnest, highly expressive face |
| **서지안** (34, 선임연구원) | 칼 단발, 반쯤 감긴 무표정 눈, 청록 터틀넥 위 빳빳한 랩코트. 데드팬 츳코미 담당 | JIAN: Korean woman in her mid 30s, sharp black bob haircut, deadpan half-lidded eyes, crisp white lab coat over a teal turtleneck |
| **한 교수** (58, PI) | 백발 섞인 올백, 각진 턱, 항상 팔짱, 랩코트 안 다크 베스트. 화강암 같은 표정 | PROF. HAN: Korean man in his late 50s, swept-back graying hair, square jaw, arms crossed, dark vest under a white lab coat, granite-still face |

### 공통 제작 설계 (저비용)

- 편당 **4~6컷**, 그중 **생성 클립 3~4개(각 6~10초, image-to-video)**. 나머지는 편집 기술로 확장: 프리즈 프레임+펀치인, 스피드 램프, 역재생 루프, 생성 클립의 스틸 팬.
- 모든 프롬프트 끝에 공통 스타일 블록을 붙입니다:
  > `STYLE: 1990s Japanese theatrical anime, hand-drawn cel shading, subtle film grain, painterly background, cinematic lighting. Absolutely no text, no captions, no subtitles, no logos, no UI anywhere in frame.`
- **자막·제목·과학 문장은 전부 화면 하단 레터박스(영상 밖)** 에 편집 단계에서 얹습니다. 화면 안 텍스트 생성 금지.
- 각 편 마지막 2초는 디자인 툴로 만든 정적 **DOI 엔드카드** (생성 아님).
- 사운드: 로열티프리 애니메이션풍 오케스트라/재즈 + 폴리(발소리, 종이, 유리병).

---

## B) 5편 시나리오

---

### 01 · ai-paper — 「자연스럽게 걸어보세요」
*(EN: "JUST WALK NORMALLY")* · Cellulose 2025 · DOI 10.1007/s10570-025-06542-7

- **훅(0~1초):** 맨발 하나가 종이 매트 위 공중에서 폭탄 해체하듯 부들부들 떨고 있다. 땀 한 방울.
- **갈등:** 한 교수 앞 시연에서 도윤은 "자연스럽게" 걸어야 하는데, 의식하는 순간 걸음이 전부 부자연스러워진다 — 누구나 아는 그 저주.
- **코믹 반전:** 런웨이 워킹까지 시도하다 제 발에 걸려 매트 위로 전신 슬로모 낙하. 그런데 오실로스코프가 폭발적으로 반응하고, 한 교수는 처음으로 흡족하게 끄덕인다. **망신이 곧 최고의 데이터였다.**

| 시간 | 컷 | 화면(액션/프레이밍) | 사운드 | 대사(KO) / 하단 자막(EN) |
|---|---|---|---|---|
| 0–6 | S1 · 생성 8초 | ECU: 종이 매트 위 떨리는 맨발 → 틸트업, 사색이 된 도윤 얼굴. 뒤로 팔짱 낀 한 교수의 흐릿한 실루엣 | 심장박동, 긴장 현악 | 한 교수: "자연스럽게." / *"Just walk normally."* |
| 6–12 | S2 · 생성 8초 | 와이드: 도윤이 로봇처럼 같은 쪽 팔다리로 걷는다. 지안, 반쯤 감긴 눈으로 관전 | 삐걱대는 코믹 튜바 | 도윤: "이게… 자연이었나?" / *"Wait. How do humans walk?"* |
| 12–17 | S3 · 편집(S2 스틸 펀치인 + 생성 6초) | 점프컷 몽타주: 군대 행진 → 패션쇼 캣워크 → 까치발. 컷마다 지안의 눈이 1mm씩 더 감김 | 컷마다 셔터음 | (무대사) / *"Attempt 2. Attempt 3. Attempt 7."* |
| 17–23 | S4 · 생성 8초 | 슬로모: 제 발에 걸려 활공, 종이 매트 위로 전신 착지. 서류가 벚꽃처럼 흩날림 | 무음 → 육중한 "쿵" | (무대사) / *"Full-body contact. And separation."* |
| 23–28 | S5 · 생성 6초 + 프리즈 | 스코프 화면의 파형이 요동(문자 없음, 초록 파형만). 한 교수, 인생 첫 끄덕임. 바닥의 도윤 엄지척 | 승리의 팡파르 한 소절 | 한 교수: "데이터가 아주 풍부하군." / 하단 과학자막 ↓ |
| 28–30 | S6 · 엔드카드 | 정적 카드: 논문 제목 + DOI + PPEL+ | 로고음 | *Read the paper · PPEL+* |

- **과학 한 문장(23–28 하단 자막):** "실제 연구에서는 한지의 접촉·분리로 생기는 마찰전기 신호를 머신러닝으로 분석해 발 건강 상태를 분류했습니다." / *"In the study, contact-separation signals from mulberry paper are classified by machine learning for foot-health monitoring."*
- **과학 이탈 경고:** 매트가 "누가 걸었는지" 알아내거나 즉석에서 질병을 진단하는 것처럼 보이면 안 됨 — 신원 추적·즉석 의료진단 아님, 연구 단계의 신호 패턴 분류임.
- **생성 프롬프트:**
  - **S1:** `Extreme close-up of a bare male foot trembling in midair above a large sheet of traditional Korean paper on a lab floor, one sweat drop falling, then slow tilt up to the terrified face of DOYUN: [고정 서술]. Blurred silhouette of a stern older professor in the background. Static camera, shallow depth of field, tense atmosphere played for comedy. [STYLE 블록]`
  - **S2:** `Wide shot of a modern research lab. DOYUN: [고정 서술] walks stiffly across a paper mat, same-side arm and leg swinging together like a malfunctioning robot, face frozen in panic. JIAN: [고정 서술] watches with deadpan half-lidded eyes. Slow lateral tracking shot. Comedic body acting. [STYLE 블록]`
  - **S3:** `Medium shot, same lab: DOYUN attempts an exaggerated fashion-runway strut across a paper mat, hand on hip, chin high, utterly serious. Camera slowly pushes in. Deadpan workplace comedy. [STYLE 블록]`
  - **S4:** `Dramatic slow-motion: DOYUN trips over his own feet and glides horizontally through the air, glasses flying off, landing flat on a large paper mat as loose documents scatter like flower petals. Low-angle hero framing, cinematic lighting, epic treatment of a silly fall. [STYLE 블록]`
  - **S5:** `Close-up of an oscilloscope screen showing only a wild glowing green waveform (no numbers, no letters), then rack focus to PROF. HAN: [고정 서술] giving one slow approving nod. Warm lighting shift. [STYLE 블록]`

---

### 02 · biosensor — 「행운의 연필 강탈 사건」
*(EN: "THE LUCKY PENCIL HEIST")* · ACS Nano 2025 · DOI 10.1021/acsnano.4c18646

- **훅(0~1초):** 어두운 실험실, 스포트라이트 아래 벨벳 쿠션 위에 모셔진 낡은 몽당연필. 장갑 낀 손이 유리 덮개로 스윽 들어온다 — 명백한 강탈 구도.
- **갈등:** 그 연필은 도윤이 10년째 모셔온 수능 부적. 지안에게는 그저 **최적의 흑연 전구체**다. 애착 대 과학.
- **코믹 반전:** 도윤이 액션영화처럼 슬라이딩 다이브까지 했지만 연필은 이미 공정 속으로. 절망 — 그런데 완성된 나뭇가지형 그래핀 전극이 눈부시게 작동하고, 지안이 타다 남은 몽당연필을 **전사자 유해 반환하듯 정중히 두 손으로** 돌려준다. 도윤, 그걸 액자에 건다.

| 시간 | 컷 | 화면 | 사운드 | 대사/자막 |
|---|---|---|---|---|
| 0–7 | S1 · 생성 8초 | 하이스트 무비 조명: 쿠션 위 몽당연필, 장갑 낀 지안의 손이 유리 덮개를 들어올려 집어간다. 붉은 경보등 회전 | 미션임파서블풍 긴장음 | (무대사) / *"Security level: one grad student."* |
| 7–13 | S2 · 생성 8초 | 도윤, 빈 쿠션 발견 → 무성 슬로모 절규 → 복도 전력질주, 랩코트 펄럭 | 절규 대신 오케스트라 타격음 | 도윤: "제 수능 연필!!" / *"MY LUCKY PENCIL!"* |
| 13–19 | S3 · 생성 8초 | 슬로모 슬라이딩 다이브 — 손끝이 닿기 직전, 반응로 도어가 쿵 닫힘. 도윤, 바닥을 미끄러져 벽까지 | 슬로모 심장음 → 금속 도어음 | (무대사) / *"Ten years of luck. One furnace."* |
| 19–25 | S4 · 생성 8초 | 반전: 나뭇가지처럼 뻗은 검은 그래핀 전극 클로즈업 → 휴대형 무선 리더가 은은히 빛나고 폰 화면엔 파형만(문자 없음). 지안, 몽당연필 잔해를 두 손 헌정 자세로 반환 | 장엄한 진혼곡 → 코믹 정적 | 지안: "훌륭한 희생이었어." / *"He served well."* |
| 25–28 | S5 · 편집(프리즈+줌) | 도윤, 액자에 든 몽당연필을 벽에 건다. 경건한 표정 | 액자 못질음 | 하단 과학자막 ↓ |
| 28–30 | S6 · 엔드카드 | DOI 카드 | 로고음 | *Read the paper · PPEL+* |

- **과학 한 문장:** "실제 연구에서는 연필 흑연을 전구체로 나뭇가지형 그래핀 전극을 만들어, DNA의 5hmC 표지를 휴대형 무선 포텐시오스탯으로 검출했습니다." / *"The study grows tree-like graphene from pencil graphite to detect the DNA marker 5hmC with a portable wireless potentiostat."*
- **과학 이탈 경고:** 연필로 사람을 즉석 진단하거나 단일 분자를 잡아내는 장면·자막 금지 — 게놈 DNA 시료의 표지(5hmC) 검출 연구임.
- **생성 프롬프트:**
  - **S1:** `Heist-movie lighting in a dark lab: a worn-down pencil stub resting on a small velvet cushion under a single spotlight inside a glass display dome. A white-gloved hand of JIAN: [고정 서술] slowly lifts the dome and takes the pencil while a red alarm light sweeps the room. Slow push-in, suspense parody. [STYLE 블록]`
  - **S2:** `DOYUN: [고정 서술] discovers the empty velvet cushion, face collapsing into a silent slow-motion scream, then sprints down a long lab corridor, lab coat flapping heroically. Tracking shot alongside him. Overdramatic anime action acting. [STYLE 블록]`
  - **S3:** `Epic slow-motion: DOYUN dives horizontally across the lab floor, arm outstretched toward a closing metal furnace door, fingertips inches away as it shuts. He slides across the floor into a wall of cardboard boxes. Low wide-angle action framing. [STYLE 블록]`
  - **S4:** `Macro close-up of a black electrode with intricate branching tree-like graphene structures, softly glowing; cut within the same shot to JIAN: [고정 서술] solemnly returning a charred pencil stub to DOYUN with both hands and a formal bow, like presenting a war medal. Reverent lighting, deadpan comedy. [STYLE 블록]`

---

### 03 · memory — 「부장님의 저항 상태」
*(EN: "THE PROFESSOR HAS TWO STATES")* · Carbon 2024 (리뷰) · DOI 10.1016/j.carbon.2024.119320

- **훅(0~1초):** 사무라이 결투 구도. 화면 절반은 화강암 표정의 한 교수 얼굴, 절반은 부들부들 커피잔을 든 도윤. 커피 한 방울이 슬로모로 낙하 중.
- **갈등:** 한 교수에겐 두 가지 상태뿐이다. **고저항 상태**(팔짱, 냉기, 결재 전면 차단)와, 커피 투입 시의 **저저항 상태**(만사 통과). 대학원생들은 커피로 교수를 '쓰기(write)'하며 결재를 흘려보낸다.
- **코믹 반전:** 원두가 떨어져 디카페인을 올린 순간 — 한 모금에 교수는 고저항 상태로 폭풍 복귀, 공중의 결재 서류가 얼어붙는다. 그리고 진짜 펀치라인: **그 상태는 지워지지 않는다.** 교수는 그날의 디카페인을 영원히 기억한다. (비휘발성.)

| 시간 | 컷 | 화면 | 사운드 | 대사/자막 |
|---|---|---|---|---|
| 0–7 | S1 · 생성 8초 | 사무라이 대치 프레이밍: 냉기 서린 교수(푸른 조명, 먼지만 굴러감) ↔ 커피잔 든 도윤. 커피 방울 슬로모 낙하 | 서부극 휘파람 + 바람 | (무대사) / *"State one: nothing gets through."* |
| 7–14 | S2 · 생성 8초 | 커피가 책상에 놓이는 순간 — 조명이 한 번에 따뜻해지고 교수의 자세가 스르륵 풀림. 결재 서류가 컨베이어처럼 술술 통과(도장은 흐릿한 붉은 원, 글자 없음) | 조명 전환 "웅—" + 경쾌한 재즈 | 도윤: "통한다…!" / *"State two: everything flows."* |
| 14–20 | S3 · 편집 몽타주(S2 변형 + 생성 6초) | 점프컷: 커피→통과, 커피→통과… 원두통이 점점 비어감 → 바닥 드러난 통을 든 도윤의 동공지진 | 몽타주 리듬 → 레코드 긁힘 | (무대사) / *"Write pulse. Write pulse. Write—"* |
| 20–26 | S4 · 생성 8초 | 도윤, 식은땀 흘리며 디카페인을 올림. 교수 한 모금 → 정지 → 번개 인서트 → 실내가 극지방 블루로 급변, 공중에 던져지던 서류가 그대로 얼어붙음 | 정적 → 뇌우 일격 | 한 교수: "…이건 아니지." / *"Wrong voltage."* |
| 26–28 | S5 · 프리즈+줌(편집) | 도윤의 영혼이 입에서 반투명하게 빠져나가는 프리즈 프레임 | 성가대 한 음 | 하단: "그리고 교수님은 그 디카페인을, 지금도 기억하신다." / *"And that state? It never resets."* + 과학자막 ↓ |
| 28–30 | S6 · 엔드카드 | DOI 카드 | 로고음 | *Read the review · PPEL+* |

- **과학 한 문장:** "실제 논문은 탄소 소재의 높은 저항과 낮은 저항, 서로 다른 두 상태에 정보를 저장하는 저항변화 메모리 연구들을 정리한 리뷰입니다." / *"The real paper is a review of carbon-based resistive switching, where high- and low-resistance states store information."*
- **과학 이탈 경고:** 이 편의 교수 개그는 100% 은유임을 자막 톤으로 분명히 할 것 — 리뷰 논문을 신소자 개발로 오인시키거나, '사람의 마음을 읽고 쓴다'는 인상을 주면 안 됨.
- **생성 프롬프트:**
  - **S1:** `Samurai-standoff split framing in a lab office: left side, PROF. HAN: [고정 서술] radiating cold blue aura, motionless; right side, DOYUN: [고정 서술] holding a trembling coffee cup, one drop of coffee falling in extreme slow motion between them. Dust drifts past. Static wide shot, western-duel parody. [STYLE 블록]`
  - **S2:** `The coffee cup lands on the professor's desk; in one continuous shot the lighting warms from cold blue to golden, PROF. HAN's crossed arms melt open, posture relaxing, and he stamps a flowing stream of blank documents with a blurred red stamp. Slow dolly-in, comedic transformation acting. No readable text on any paper. [STYLE 블록]`
  - **S3:** `Close-up: DOYUN holds an empty glass coffee-bean jar upside down; a single bean drops out and bounces on the floor. His pupils shrink to dots, sweat drop, slow zoom into his horrified face. [STYLE 블록]`
  - **S4:** `PROF. HAN sips from a mug, freezes mid-sip; a lightning flash; the room lighting snaps to arctic blue and papers thrown in the air freeze mid-fall around him as his arms re-cross into granite stillness. DOYUN cowers in the foreground. Dramatic push-in on the professor's icy stare. [STYLE 블록]`

---

### 04 · energy-storage — 「밤을 새운 건 잉크가 아니었다」
*(EN: "THE INK SLEPT FINE")* · Adv. Comp. Hybrid Mater. 2026 · DOI 10.1007/s42114-026-01862-z

- **훅(0~1초):** 호러 조명. 유리병에 비친 충혈된 눈 클로즈업 — 번개 섬광 — 병 속 잉크가 죽은 듯 탁하게 변해 있다.
- **갈등:** 지안의 MXene 잉크가 밤마다 산화되어 죽는다(연구자라면 다 아는 악몽). 새 배치를 지키려 랩 야전침대 밤샘 경계에 돌입 — 랩 필름, 테이프, 결국 병을 끌어안고 잔다.
- **코믹 반전:** 도윤이 휴가 가방을 멘 채 지나가다 검은 분말(MnO₂)을 휘휘 저어 넣고 휘파람 불며 퇴근. 아침 햇살 — 잉크는 광택 찬란, **대신 지안이 산화되어 있다**(다크서클, 좀비 자세). 잉크가 인간보다 오래 버텼다.

| 시간 | 컷 | 화면 | 사운드 | 대사/자막 |
|---|---|---|---|---|
| 0–7 | S1 · 생성 8초 | 심야 랩 호러: 보관장을 여는 지안 — 번개 — 한때 반짝이던 잉크가 탁한 잿빛. 더치앵글, 무성 절규 | 뇌우, 호러 현악 | 지안: "…또." / *"Third batch this week."* |
| 7–14 | S2 · 생성 8초 | 밤샘 경계 몽타주(원컷): 새 잉크병에 랩 필름 칭칭 → 테이프 → 결국 끌어안고 의자에서 꾸벅. 벽시계 바늘 고속 회전 | 째깍음 가속 + 코골이 | (무대사) / *"Night watch: hour six."* |
| 14–20 | S3 · 생성 7초 | 도윤, 휴가용 하와이안 셔츠+캐리어 차림으로 지나가다 멈춤 → 검은 분말 한 스푼을 잉크에 휘휘 → 병을 톡톡 → 휘파람 퇴장 | 경쾌한 휘파람 | 도윤: "산소는 얘가 먼저 먹을 거예요." / *"The powder eats the oxygen first."* |
| 20–26 | S4 · 생성 8초 | 아침 햇살: 잉크는 거울처럼 광택 → 팬 하면 좀비화된 지안(폭탄머리, 다크서클, 병을 여전히 사수) → 도윤 손의 인쇄된 유연 슈퍼커패시터가 낭창하게 휘어짐 | 상쾌한 아침 새소리(잔인하게 밝게) | 지안: "산화된 건 나였어…" / *"The ink is fine. I am not."* |
| 26–28 | S5 · 프리즈(편집) | 광택 잉크 vs 좀비 지안 2분할 프리즈 | 정적 | 하단 과학자막 ↓ |
| 28–30 | S6 · 엔드카드 | DOI 카드 | 로고음 | *Read the paper · PPEL+* |

- **과학 한 문장:** "실제 연구에서는 MnO₂ 나노입자가 산소를 먼저 포집해 MXene 잉크의 산화를 막았고, 이 잉크로 인쇄한 유연 슈퍼커패시터는 충·방전 10,000회 후에도 용량의 98.52%를 유지했습니다." / *"MnO₂ nanoparticles scavenge oxygen to keep MXene ink stable; the printed flexible supercapacitor retained 98.52% capacity after 10,000 charge–discharge cycles."*
- **과학 이탈 경고:** 10,000회·98.52%는 **충·방전** 사이클 수치 — 굽힘 횟수로 오인되게 편집 금지. '영구 배터리'·'절대 안 죽는 잉크' 뉘앙스 금지(산화를 '완화'하는 것).
- **생성 프롬프트:**
  - **S1:** `Horror-movie night scene in a lab: JIAN: [고정 서술] opens a storage cabinet; lightning flashes through the window revealing a glass jar of ink that has turned dull, cloudy gray. Dutch angle, her face lit from below, mouth opening in a silent horror scream. Parody of J-horror framing. [STYLE 블록]`
  - **S2:** `Single continuous shot, night lab: JIAN wraps a fresh jar of dark glossy ink in layers of plastic wrap, then tape, then finally hugs the jar in a chair as her head nods off; wall clock hands spin rapidly behind her. Time-lapse comedy, static camera. [STYLE 블록]`
  - **S3:** `DOYUN: [고정 서술] but wearing a loud Hawaiian shirt over his cardigan and pulling a small travel suitcase, casually stops, stirs a spoon of fine dark powder into the ink jar next to the sleeping JIAN, pats the jar twice, and strolls out whistling. Breezy tracking shot, relaxed comedic body language. [STYLE 블록]`
  - **S4:** `Warm morning sunlight floods the lab: close-up of the ink jar now glossy and mirror-bright; camera pans to JIAN looking completely wrecked — wild hair, deep dark circles, zombie posture, still clutching the jar — while a hand holds a thin printed flexible device bending springily in the foreground. Cruelly cheerful lighting. [STYLE 블록]`

---

### 05 · cherry-blossom — 「벚꽃 아래, 핀셋」
*(EN: "UNDER THE CHERRY TREE, WITH TWEEZERS")* · Nano Energy 2026 · DOI 10.1016/j.nanoen.2025.111687

- **훅(0~1초):** 순정 애니의 그 장면 — 황금빛 역광, 흩날리는 벚꽃, 남자가 천천히 손을 뻗는다… 손에 들린 것은 **핀셋과 지퍼백**.
- **갈등:** 벚꽃 데이트에서 도윤은 낭만 대신 시료 채집을 한다. 상대는 폭발해 꽃보라 속으로 퇴장. 도윤은 눈치도 못 채고 행복하게 지퍼백을 채운다.
- **코믹 반전:** 계절이 지나 — 꽃잎을 층으로 넣어 만든 탭 센서가 완성된다. 떠났던 그녀가 궁금해서 돌아와 패드를 톡, 톡 두 번 두드리자 파형이 두 봉우리를 그리고, 도윤의 눈에 감동의 눈물이 차오른다. 카메라가 빠지면 — **그가 감격하며 바라보는 건 그녀가 아니라 분류 파형이다.** 지안의 데드팬이 화면을 닫는다.

| 시간 | 컷 | 화면 | 사운드 | 대사/자막 |
|---|---|---|---|---|
| 0–7 | S1 · 생성 8초 | 순정만화 문법 풀가동: 황금 역광, 꽃보라, 도윤이 손을 뻗는다 → 핀셋 등장, 꽃잎 한 장 집어 지퍼백 밀봉. 옆의 상대(단역, 얼굴만 필요) 표정 붕괴 | 서정 피아노 → 레코드 긁힘 | (무대사) / *"The most romantic scene in anime. Almost."* |
| 7–13 | S2 · 생성 7초 | 상대가 꽃보라 속으로 성큼성큼 퇴장. 도윤, 전혀 모른 채 무릎 꿇고 채집 삼매경, 지퍼백 가득 | 바람, 멀어지는 구두굽 소리 | 도윤: "오늘 수율 좋다!" / *"Great harvest today!"* |
| 13–20 | S3 · 생성 8초 | 랩: 꽃잎을 얇은 층으로 눌러 넣은 소자를 정성껏 조립 → 손가락 탭 → 스코프에 초록 파형이 한 번 솟음(문자 없음) | 조립 폴리 → 파형 "삑" | (무대사) / *"Petals inside. A tap outside."* |
| 20–26 | S4 · 생성 8초 | 랩 문가에 그때 그녀. 다가와 패드를 톡·톡 — 파형 두 봉우리. 도윤의 눈에 그렁그렁 눈물 → 카메라 빠지면 시선의 끝은 그녀가 아니라 스코프. 뒤에서 지안, 반쯤 감긴 눈 | 로맨틱 현악 고조 → 뚝 끊김 | 도윤: "구분했어… 두 번인 걸…" / *"It knows. It's a double tap."* |
| 26–28 | S5 · 프리즈(편집) | 감동의 도윤 / 어이없는 그녀 / 데드팬 지안 3인 프리즈 | 정적 | 하단 과학자막 ↓ |
| 28–30 | S6 · 엔드카드 | DOI 카드 | 로고음 | *Read the paper · PPEL+* |

- **과학 한 문장:** "실제 연구에서는 벚꽃잎을 층으로 넣어 제작한 소자의 접촉·분리 신호를 머신러닝으로 분석해 단일 탭과 이중 탭을 구별했습니다." / *"The fabricated device uses cherry-petal layers; machine learning distinguishes single from double taps in its contact-separation signals."*
- **과학 이탈 경고:** 생꽃잎이 그대로 전기를 만든다거나 랩 전체에 전원을 공급하는 묘사 금지, 제스처는 단일/이중 탭뿐(스와이프·원 그리기 금지), 판독 전자장치는 여전히 외부 전원이 필요함.
- **생성 프롬프트:**
  - **S1:** 아래 C)의 파일럿 프롬프트와 동일(8초 그대로 본편 재사용 — 제작비 절감).
  - **S2:** `A young Korean woman in a spring dress storms away through a blizzard of falling cherry petals, heels clicking, while in the foreground DOYUN: [고정 서술] kneels happily on the grass picking petals with tweezers into a transparent zip bag, completely oblivious. Golden-hour backlight, wide romantic framing used ironically. [STYLE 블록]`
  - **S3:** `Macro lab scene: careful hands assemble a thin layered device with pressed pink cherry petals visible inside, close the top layer, then one finger taps the pad; an oscilloscope in the background shows a single glowing green spike (no numbers, no letters). Warm desk-lamp lighting, precise loving craftsmanship acting. [STYLE 블록]`
  - **S4:** `The same young Korean woman appears at the lab doorway, curious; she walks over and taps a small petal-layered pad twice with one finger; a scope glows with two clean spikes. DOYUN: [고정 서술] tears up with trembling awe — camera slowly pulls back to reveal his adoring gaze is fixed on the waveform, not on her. JIAN: [고정 서술] watches deadpan in the background. Romantic lighting undercut by comedy. [STYLE 블록]`

---

## C) 파일럿 선정 — 05 「벚꽃 아래, 핀셋」

**선정 이유:** 다섯 편 중 유일하게 **개그가 단 하나의 그림으로 성립**합니다. "벚꽃 역광에서 뻗는 손"은 일본 애니메이션에서 가장 즉각적으로 읽히는 낭만 기호이고, 그 손에 핀셋이 들려 있는 순간 배신이 완성됩니다. 대사·자막·소리가 전혀 없어도 0.5초 만에 장르를 약속하고 3초 만에 약속을 깨므로, 사이트 오너가 요구한 "애니메이션급 표정 연기"(설렘→진지한 채집 집중→상대의 표정 붕괴)를 8초 안에 전부 증명할 수 있습니다. 다른 네 편의 훅은 좋지만 맥락(랩, 캐릭터 관계)이 1컷 더 필요합니다.

**8초 단독 파일럿 프롬프트 (훅으로 시작, 코믹 페이오프로 종료, 무음 성립):**

```
Single continuous 8-second shot, 1990s Japanese theatrical anime style, hand-drawn
cel shading, subtle film grain, painterly background, golden-hour backlight.

A gentle storm of pink cherry blossom petals drifts across frame under a blooming
cherry tree in a park. DOYUN — Korean man in his late 20s, messy black hair, round
wire-frame glasses, worn brown cardigan — gazes up with a soft, moved expression
and slowly, romantically extends his hand toward a falling petal, coat and hair
stirring in the wind, classic shoujo-anime framing. At the midpoint his other hand
rises into frame holding metal tweezers and a small transparent zip bag; his dreamy
expression sharpens into intense scientific concentration as he precisely plucks
one petal from the air with the tweezers, drops it into the bag, and seals it with
deep satisfaction, giving the bag one proud little shake. Beside him, a young
Korean woman in a spring dress turns from swooning anticipation to open-mouthed
disbelief, shoulders dropping. End on his blissful proud face next to her frozen
deadpan stare, petals still falling.

Slow dolly-in, shallow depth of field. Expressive anime facial acting throughout.
Absolutely no text, no captions, no subtitles, no logos anywhere in frame.
```

---

## D) 자체 평가 (5점 만점, 냉정하게)

| 편 | 1초 훅 | 성인 코미디 반전 | 과학 충실도 | 제작 용이성 | 비고 |
|---|---|---|---|---|---|
| 01 걸음 | 4 | 4 | 5 | 4 | "의식하면 못 걷는다"는 전 인류 공감 개그. 낙하 슬로모(S4)의 생성 품질이 성패 좌우 — 실패 시 프리즈 3연타 편집으로 대체 가능 |
| 02 연필 | 4 | 4 | 5 | 4 | 하이스트 패러디는 문법이 견고해 연출 실패 확률 낮음. '유해 반환 목례'가 확실한 두 번째 웃음 |
| 03 교수 | 5 | 4 | 4 | 5 | 훅이 가장 강함(사무라이 대치+커피). 리뷰 논문이라 은유임을 자막 톤으로 반드시 고정할 것 — 충실도 4점은 그 리스크 반영 |
| 04 잉크 | 4 | 5 | 5 | 4 | "잉크 대신 인간이 산화됐다"가 연구자 타깃에 가장 뼈아프게 웃김. 좀비 지안(S4)의 표정 연기가 관건 |
| 05 벚꽃 | 5 | 5 | 5 | 5 | **파일럿.** 무음 성립, 1컷 개그, S1을 본편에 재사용해 비용까지 최적 |

**개발 중 폐기·재작업한 안 (투명성 차원):**
- 01 초안 "매트가 밤손님의 정체를 밝힌다" → **신원 추적은 논문에 없음**, 과학 이탈로 폐기하고 '자연스럽게 걷기의 저주'로 교체.
- 03 초안 "전자들이 지름길을 찾는 교통 코미디" → 인간 주인공 부재 + 기존작과 동일 발상이라 폐기, '교수 저항 상태'로 전면 재작성. 디카페인 = 비휘발성 펀치라인이 리뷰의 핵심 개념(상태 유지)과 정확히 맞물리는 것을 확인 후 확정.
- 05 초안 "고백 성공 로맨스 엔딩" → 개그가 아니라 감동으로 끝나 밋밋함. "눈물의 대상이 그녀가 아니라 파형"으로 뒤집어 성인 코미디 반전을 확보.

**공통 준수사항 재확인:** 모든 자막·과학 문장·엔드카드는 하단 레터박스(화면 밖) 전용, 생성 화면 안 텍스트 0, 각 편 과학 문장은 1개로 제한하고 허구의 사건(교수의 결재, 데이트, 밤샘)은 어떤 자막에서도 "연구 결과"로 서술하지 않습니다.
