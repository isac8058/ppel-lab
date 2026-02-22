"""
식당봉사 주간 알림 스크립트
- 매주 토요일에 다음 주 일요일 봉사팀을 이메일로 알림
- 기준: 2026-03-01(일) 1팀 시작, 이후 매주 순환
"""

import os
import sys
import smtplib
from datetime import date, timedelta
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# ─────────────────────────────────────────────
# 봉사팀 명단
# ─────────────────────────────────────────────
TEAMS = [
    {
        "name": "1팀",
        "leader": "임수만",
        "members": ["김경은E", "정재성A", "장쾌남"],
    },
    {
        "name": "2팀",
        "leader": "정정진",
        "members": ["김호기", "김병수C", "오선록"],
    },
    {
        "name": "3팀",
        "leader": "최성계",
        "members": ["최종문A", "김대연A", "홍성일A"],
    },
    {
        "name": "4팀",
        "leader": "김종민C",
        "members": ["김도윤B", "김재근B", "박광진"],
    },
]

# 기준 토요일: 2026-02-28 → 다음 날(일) 1팀 봉사 시작
REFERENCE_SATURDAY = date(2026, 2, 28)

RECIPIENT = "smlim@jbnu.ac.kr"


def get_duty_team(saturday: date) -> dict:
    """해당 토요일 기준 다음 날(일) 봉사팀 반환"""
    days_since_ref = (saturday - REFERENCE_SATURDAY).days
    week_index = days_since_ref // 7
    team_index = week_index % len(TEAMS)
    return TEAMS[team_index]


def build_message(team: dict, sunday: date) -> tuple[str, str]:
    """(제목, 본문) 반환"""
    members_str = ", ".join(team["members"])
    subject = f"[식당봉사 알림] {sunday.strftime('%m/%d')}"
    body = (
        f"이번주 식당봉사는 {team['name']} ({team['leader']} 조장, {members_str}) 입니다."
    )
    return subject, body


def send_email(gmail_user: str, gmail_password: str, subject: str, body: str) -> None:
    """Gmail SMTP로 이메일 전송"""
    msg = MIMEMultipart()
    msg["From"] = gmail_user
    msg["To"] = RECIPIENT
    msg["Subject"] = subject
    msg.attach(MIMEText(body, "plain", "utf-8"))

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(gmail_user, gmail_password)
        server.sendmail(gmail_user, RECIPIENT, msg.as_string())


def main():
    gmail_user = os.environ.get("GMAIL_USER")
    gmail_password = os.environ.get("GMAIL_APP_PASSWORD")

    if not gmail_user or not gmail_password:
        print("오류: 환경변수 GMAIL_USER, GMAIL_APP_PASSWORD 를 설정하세요.")
        sys.exit(1)

    today = date.today()

    if today.weekday() != 5:
        print(f"경고: 오늘({today})은 토요일이 아닙니다. 계속 실행합니다.")

    saturday = today
    sunday = saturday + timedelta(days=1)

    team = get_duty_team(saturday)
    subject, body = build_message(team, sunday)

    print(f"수신: {RECIPIENT}")
    print(f"제목: {subject}")
    print(f"본문:\n{body}")

    send_email(gmail_user, gmail_password, subject, body)
    print("이메일 전송 완료!")


if __name__ == "__main__":
    main()
