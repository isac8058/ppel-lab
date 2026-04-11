"""
식당봉사 주간 알림 스크립트
- 매주 금요일에 이번 주 일요일 봉사조를 이메일로 알림
- 기준: 2026-04-19(일) A조 시작, 이후 격주(2조) 순환
"""

import os
import sys
import smtplib
from datetime import date, timedelta
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# ─────────────────────────────────────────────
# 봉사조 명단 (2조 격주 체제)
# ─────────────────────────────────────────────
TEAMS = [
    {
        "name": "A조",
        "leader": "임수만",
        "vice_leader": "최성계",
        "members": [
            "김호기", "김준영H", "김재근B", "김병수C", "박광진",
            "홍성일A", "장쾌남", "김성철E", "정재성A",
        ],
    },
    {
        "name": "B조",
        "leader": "정정진",
        "vice_leader": "김대연A",
        "members": [
            "김도윤B", "김종민C", "김승호D", "오선록", "최종문A",
            "임철승", "김중백", "김경은E", "정준기C",
        ],
    },
]

# 기준 토요일: 2026-04-18 → 다음 날(일) A조 봉사 시작
REFERENCE_SATURDAY = date(2026, 4, 18)

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
        f"이번주 식당봉사는 {team['name']}입니다.\n"
        f"정조장: {team['leader']} / 부조장: {team['vice_leader']}\n"
        f"조원: {members_str}"
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

    if today.weekday() != 4:
        print(f"경고: 오늘({today})은 금요일이 아닙니다. 계속 실행합니다.")

    saturday = today + timedelta(days=1)
    sunday = today + timedelta(days=2)

    team = get_duty_team(saturday)
    subject, body = build_message(team, sunday)

    print(f"수신: {RECIPIENT}")
    print(f"제목: {subject}")
    print(f"본문:\n{body}")

    send_email(gmail_user, gmail_password, subject, body)
    print("이메일 전송 완료!")


if __name__ == "__main__":
    main()
