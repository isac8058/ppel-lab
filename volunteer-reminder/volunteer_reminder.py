#!/usr/bin/env python3
"""
광주채플 식당 홀 청소 알림 (격주 A/B조 운영, 2026 하반기 편성)

- 발송 시점: 매주 금요일 09:30 KST (GitHub Actions cron, 00:30 UTC)
- 차례 판정: 다음 일요일 기준 A/B 조 결정
- 기준점: 2026-05-03 (일) = A조 시작 (변경 없음)
- 메시지 형식: 직책(정조장/부조장) 표기 없이 이름만 나열
- 청소 명단 자동 제외:
    · SG목장 부목자 3명 (식당봉사 자체 제외, 편성 미포함: 김현호A, 김진남, 이정일)
    · 주일목장 부목자 2명 (청소만 제외, 별도 표기)
"""

import os
import sys
import smtplib
from datetime import datetime, timedelta, timezone
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# =========================================================
# 편성표 (2026 하반기, 26.07 확정)
# 마을 번호 재부여: 211 정상연, 212 배철한, 213 조윤희F,
#                   214 송두헌, 215 김영석A
# =========================================================
TEAMS = {
    "A": {
        "label": "A조",
        "명단": [
            "임수만",    # 215, 정조장(내부 관리용, 메시지 미표기)
            "최성계",    # 212, 부조장(내부 관리용, 메시지 미표기)
            "김호기",    # 211
            "모종명",    # 211, 신규
            "김준영H",   # 212
            "김병수C",   # 213
            "박광진",    # 213
            "홍성일A",   # 214
            "장쾌남",    # 214
            "김성철E",   # 215
        ],
    },
    "B": {
        "label": "B조",
        "명단": [
            "정정진",    # 212, 정조장(내부 관리용, 메시지 미표기)
            "김대연A",   # 214, 부조장(내부 관리용, 메시지 미표기)
            "김도윤B",   # 211
            "박철수B",   # 212, 신규
            "오선록",    # 213
            "김중백",    # 214
            "김경은E",   # 214
            "정준기C",   # 214
            "정재성A",   # 215
            "안정욱D",   # 215, 신규
        ],
    },
}

# 청소 명단에서 제외 (참고용 표기)
# 2026 하반기 변경: 김종민(목자 전환), 강신우(목원 전환) 삭제
주일목장_제외 = ["임철승", "김승호D"]

# =========================================================
# 차례 판정
# =========================================================
KST = timezone(timedelta(hours=9))
ANCHOR_SUNDAY = datetime(2026, 5, 3, tzinfo=KST).date()  # A조 시작
ANCHOR_TEAM = "A"


def next_sunday(today):
    """오늘 이후 가장 가까운 일요일 (오늘이 일요일이면 오늘)."""
    days_ahead = (6 - today.weekday()) % 7  # Monday=0, Sunday=6
    return today + timedelta(days=days_ahead)


def team_for_sunday(sunday):
    """격주 교대 기준점(2026-05-03=A조)으로 해당 일요일의 조 판정."""
    weeks = (sunday - ANCHOR_SUNDAY).days // 7
    if weeks % 2 == 0:
        return ANCHOR_TEAM
    return "B" if ANCHOR_TEAM == "A" else "A"


# =========================================================
# 메시지 생성 (이름만 나열, 직책 미표기)
# =========================================================
def build_message(sunday, team_key):
    team = TEAMS[team_key]
    subject = f"[식당봉사 알림] {sunday.strftime('%m/%d')}"
    names = ", ".join(team["명단"])
    body = (
        f"이번주 식당봉사는 {team['label']}입니다.\n\n"
        f"{names}\n\n"
        f"— 광주채플"
    )
    return subject, body


# =========================================================
# Gmail SMTP 발송 (저장소 기존 인증 방식 유지)
# =========================================================
RECIPIENT = "smlim@jbnu.ac.kr"


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

    today = datetime.now(KST).date()
    sunday = next_sunday(today)
    team_key = team_for_sunday(sunday)
    subject, body = build_message(sunday, team_key)

    print(f"수신: {RECIPIENT}")
    print(f"제목: {subject}")
    print(f"본문:\n{body}")

    send_email(gmail_user, gmail_password, subject, body)
    print(f"발송 완료: {subject} ({TEAMS[team_key]['label']})")


if __name__ == "__main__":
    main()
