# 이메일 알림 설정 가이드

PPEL Lab 일일 보고서를 smlim@jbnu.ac.kr로 받기 위한 설정 가이드입니다.

## 1단계: Gmail 앱 비밀번호 생성

### 1.1 Google 계정 2단계 인증 활성화
1. https://myaccount.google.com/security 접속
2. "Google에 로그인" 섹션에서 **2단계 인증** 클릭
3. 안내에 따라 2단계 인증 활성화

### 1.2 앱 비밀번호 생성
1. https://myaccount.google.com/apppasswords 접속
2. "앱 선택" → **메일** 선택
3. "기기 선택" → **기타(맞춤 이름)** → "PPEL Lab Bot" 입력
4. **생성** 클릭
5. 표시되는 16자리 비밀번호 복사 (예: `abcd efgh ijkl mnop`)

> ⚠️ 이 비밀번호는 한 번만 표시됩니다. 안전한 곳에 저장하세요.

---

## 2단계: GitHub Secrets 설정

### 2.1 저장소 Settings 접속
1. GitHub 저장소 페이지 접속
2. 상단 메뉴에서 **Settings** 클릭
3. 좌측 사이드바에서 **Secrets and variables** → **Actions** 클릭

### 2.2 Secrets 추가
**New repository secret** 버튼을 클릭하여 다음 4개의 Secret을 추가:

| Name | Value |
|------|-------|
| `SMTP_SERVER` | `smtp.gmail.com` |
| `SMTP_PORT` | `587` |
| `SMTP_USERNAME` | 발신용 Gmail 주소 (예: `ppellab.bot@gmail.com`) |
| `SMTP_PASSWORD` | 1단계에서 생성한 앱 비밀번호 (공백 제거: `abcdefghijklmnop`) |

---

## 3단계: 테스트

### 워크플로우 수동 실행
1. GitHub 저장소 → **Actions** 탭
2. 좌측에서 **Daily Task Recommendations** 선택
3. 우측 **Run workflow** 버튼 클릭
4. **Run workflow** 확인

### 결과 확인
- 이메일 수신 확인: smlim@jbnu.ac.kr
- GitHub Actions 로그에서 성공/실패 확인

---

## 대체 옵션: 대학 SMTP 서버 사용

전북대학교 SMTP 서버를 사용할 경우:

| Name | Value |
|------|-------|
| `SMTP_SERVER` | `smtp.jbnu.ac.kr` (확인 필요) |
| `SMTP_PORT` | `587` 또는 `465` |
| `SMTP_USERNAME` | `smlim@jbnu.ac.kr` |
| `SMTP_PASSWORD` | 대학 이메일 비밀번호 |

> 대학 SMTP 설정은 전산원에 문의하시기 바랍니다.

---

## 문제 해결

### 이메일이 오지 않는 경우
1. GitHub Actions 로그 확인
2. 스팸 폴더 확인
3. Gmail "보안 수준이 낮은 앱" 설정 확인

### "Authentication failed" 오류
- 앱 비밀번호 재생성
- 비밀번호에서 공백 제거 확인

---

## 일정

설정 완료 후, 매일 **오전 9시 (KST)**에 다음 내용이 포함된 이메일이 발송됩니다:

- 📚 최신 연구동향 (arXiv 논문)
- 🔬 연구 프로그램 추천
- 🛠️ 웹사이트 개선 작업

---

*이 가이드에 대한 문의: GitHub Issues를 통해 문의해 주세요.*
