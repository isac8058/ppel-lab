# Daily Paper Digest

매일 최상위 저널에서 신규 논문을 자동 수집하고, Google Gemini API로 분석한 뒤, 트렌드 리포트를 이메일로 발송하는 시스템입니다.

## 대상 저널

- Nature
- Science
- Advanced Materials
- ACS Nano
- Nano Energy
- Biosensors and Bioelectronics
- Advanced Functional Materials
- Energy & Environmental Science

## 주요 기능

- RSS 피드 기반 논문 자동 수집 (최근 48시간)
- TF-IDF 기반 키워드 관련성 필터링
- Gemini AI 논문 분석 (한글 요약, PPEL 연관성 점수)
- 반응형 HTML 이메일 리포트 자동 발송
- SQLite 기반 중복 방지 및 주간 트렌드 추적
- GitHub Actions 기반 매일 자동 실행 (KST 오전 7시)

## 설치

```bash
git clone https://github.com/ppel-lab/daily-paper-digest.git
cd daily-paper-digest
pip install -r requirements.txt
```

## 환경변수 설정

`.env.example`을 `.env`로 복사한 뒤 값을 입력합니다:

```bash
cp .env.example .env
```

필요한 환경변수:

| 변수 | 설명 |
|------|------|
| `GEMINI_API_KEY` | Google Gemini API 키 |
| `GMAIL_USER` | Gmail 이메일 주소 |
| `GMAIL_APP_PASSWORD` | Gmail 앱 비밀번호 |

### Gemini API 키 발급

1. [Google AI Studio](https://aistudio.google.com/apikey)에 접속
2. Google 계정으로 로그인
3. "Create API Key" 클릭
4. 생성된 API 키를 `.env` 파일의 `GEMINI_API_KEY`에 입력

무료 tier 한도: 분당 15회, 일 1,500회 (본 시스템에 충분)

### Gmail 앱 비밀번호 생성

1. [Google 계정 관리](https://myaccount.google.com/) 접속
2. 보안 > 2단계 인증 활성화 (필수)
3. 보안 > 2단계 인증 > 앱 비밀번호
4. 앱 선택: "메일", 기기 선택: "기타"
5. 생성된 16자리 비밀번호를 `.env` 파일의 `GMAIL_APP_PASSWORD`에 입력

## 로컬 실행

```bash
python main.py
```

## GitHub Actions 자동 실행

### Secrets 설정

1. GitHub 리포지토리 > Settings > Secrets and variables > Actions
2. 다음 시크릿 추가:
   - `GEMINI_API_KEY`: Gemini API 키
   - `GMAIL_USER`: Gmail 주소
   - `GMAIL_APP_PASSWORD`: Gmail 앱 비밀번호

### 실행 스케줄

- 매일 UTC 22:00 (KST 오전 7:00) 자동 실행
- 수동 실행: Actions 탭 > "Daily Paper Digest" > "Run workflow"

## config.yaml 커스터마이징

### 저널 추가/변경

```yaml
journals:
  - name: "저널 이름"
    url: "RSS 피드 URL"
```

### 키워드 변경

```yaml
keywords:
  - energy harvesting
  - biosensor
  - 원하는 키워드 추가
```

### 분석 설정

```yaml
analysis:
  max_papers: 20          # 분석할 최대 논문 수
  relevance_threshold: 3  # 관련성 점수 임계값 (0-10)
  time_window_hours: 48   # 수집 시간 범위 (시간)
```

### 수신자 변경

```yaml
email:
  recipient: "your-email@example.com"
```

## 프로젝트 구조

```
daily-paper-digest/
├── config.yaml              # 저널 RSS URL, 키워드, 이메일 설정
├── src/
│   ├── collector.py         # RSS/API로 논문 수집
│   ├── filter.py            # 키워드 기반 필터링 (TF-IDF)
│   ├── analyzer.py          # Gemini API로 논문 분석
│   ├── reporter.py          # HTML 이메일 리포트 생성
│   ├── mailer.py            # SMTP 이메일 발송
│   └── database.py          # SQLite 중복 방지 & 트렌드 추적
├── templates/
│   └── email_template.html  # 이메일 HTML 템플릿
├── main.py                  # 전체 파이프라인 실행
├── requirements.txt
├── .env.example
└── .github/
    └── workflows/
        └── daily-digest.yml # GitHub Actions 워크플로우
```
