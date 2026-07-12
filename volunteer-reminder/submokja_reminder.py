#!/usr/bin/env python3
"""
광주채플 부목자 월간 모임 공지 (마을 순환, 2026 하반기 편성)

- 실행: 매주 월요일 09:30 KST (GitHub Actions cron, 00:30 UTC)
- 발송 조건: 다가오는 일요일이 그 달의 넷째 주 주일일 때만 발송
- 마을 순환: 211 -> 212 -> 213 -> 214 -> 215 -> 211, 기준점 2026-07 = 211 정상연
- 정규 시간: 오후 3시 30분, 장소: 새가족실
- 역할 배정: 진행 마을 부목자 명단의 앞 3명 순서대로 기도, 말씀 요약, 간식
  (배정을 바꾸려면 해당 마을 명단의 이름 순서만 수정)
- 진행 마을 마을장님 초청 문구 포함
"""

import os
import sys
import smtplib
from datetime import datetime, timedelta, timezone
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# =========================================================
# 모임 기본 정보
# =========================================================
MEETING_TIME = "오후 3시 30분"
MEETING_PLACE = "새가족실"
RECIPIENT = "smlim@jbnu.ac.kr"

# =========================================================
# 마을 편성 (2026 하반기, 26.07 확정)
# 부목자 명단 순서 = 역할 우선순위 (앞 3명: 기도, 말씀 요약, 간식)
# =========================================================
VILLAGES = [
    {
        "번호": "211",
        "마을장": "정상연",
        "부목자": ["김호기", "김도윤B", "모종명", "김현호A", "김진남", "이정일"],
    },
    {
        "번호": "212",
        "마을장": "배철한",
        "부목자": ["최성계", "김준영H", "박철수B", "정정진", "임철승", "김승호D"],
    },
    {
        "번호": "213",
        "마을장": "조윤희F",
        "부목자": ["김병수C", "오선록", "박광진"],
    },
    {
        "번호": "214",
        "마을장": "송두헌",
        # 홍성일A는 가족 간병으로 참석이 어려워 후순위, 김대연A는 격주 근무로 후순위
        "부목자": ["장쾌남", "김경은E", "김중백", "정준기C", "김대연A", "홍성일A"],
    },
    {
        "번호": "215",
        "마을장": "김영석A",
        # 임수만은 진행자이므로 후순위
        "부목자": ["김성철E", "안정욱D", "정재성A", "임수만"],
    },
]

# 마을 순환 기준점: 2026년 7월 = VILLAGES[0] (211 정상연)
ANCHOR_YEAR = 2026
ANCHOR_MONTH = 7

KST = timezone(timedelta(hours=9))


def next_sunday(today):
    """오늘 이후 가장 가까운 일요일 (오늘이 일요일이면 오늘)."""
    days_ahead = (6 - today.weekday()) % 7  # Monday=0, Sunday=6
    return today + timedelta(days=days_ahead)


def fourth_sunday(year, month):
    """해당 연월의 넷째 주 주일 날짜."""
    d = datetime(year, month, 1, tzinfo=KST).date()
    first_sunday = d + timedelta(days=(6 - d.weekday()) % 7)
    return first_sunday + timedelta(days=21)


def village_for_month(year, month):
    """마을 순환 판정. 기준점 2026-07 = 211 정상연."""
    months = (year - ANCHOR_YEAR) * 12 + (month - ANCHOR_MONTH)
    return VILLAGES[months % len(VILLAGES)]


# =========================================================
# 공지문 생성
# =========================================================
def build_message(sunday, village):
    roles = village["부목자"][:3]  # 기도, 말씀 요약, 간식
    subject = f"[부목자 모임 공지] {sunday.strftime('%m/%d')}"
    body = (
        "샬롬! 부목자님들, 평안하신지요.\n"
        "매월 넷째 주 주일은 정기 부목자 모임이 있는 날입니다. "
        f"다가오는 이번 주 주일({sunday.day}일)에 {sunday.month}월 부목자 모임으로 모이고자 하오니, "
        "모든 부목자님들께서 빠짐없이 참석해 주시기를 부탁드립니다.\n\n"
        f"■ 일시: {sunday.month}월 {sunday.day}일(주일) {MEETING_TIME}\n"
        f"■ 장소: {MEETING_PLACE}\n"
        f"■ 이번 달 순서 담당 안내 ({village['번호']} {village['마을장']} 마을)\n"
        f" * 기도: {roles[0]} 부목자님\n"
        f" * 말씀 요약: {roles[1]} 부목자님\n"
        f" * 간식 당번: {roles[2]} 부목자님\n"
        "(담당 역할은 상황에 따라 다른 분과 자유롭게 변경 가능합니다. "
        "변경이 필요하신 경우 편하게 조율해 주시기 바랍니다.)\n\n"
        f"아울러 이번 달 진행 마을이신 {village['마을장']} 마을장님께서도 "
        "참석이 가능하시면 함께해 주시기를 부탁드립니다.\n\n"
        "원활한 모임 준비를 위해 참석 여부를 파악하고 있습니다. "
        "공지를 확인하신 부목자님들께서는 참석 여부를 회신해 주시면 감사하겠습니다.\n"
        "부득이한 사정으로 이번 모임에 참석하지 못하시는 부목자님들께서는 "
        "간략한 불참 사유를 꼭 함께 기재해 주시기를 부탁드립니다. 양육을 위한 교회 방침이라 하십니다.\n"
        "모두 함께 모여 은혜 나누는 귀한 시간이 되기를 소망합니다. 주일에 기쁜 모습으로 뵙겠습니다!"
    )
    return subject, body


# =========================================================
# Gmail SMTP 발송 (저장소 기존 인증 방식 유지)
# =========================================================
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
    if sunday != fourth_sunday(sunday.year, sunday.month):
        print(f"이번 주 일요일({sunday})은 넷째 주 주일이 아니므로 발송하지 않습니다.")
        return
    village = village_for_month(sunday.year, sunday.month)
    subject, body = build_message(sunday, village)

    print(f"수신: {RECIPIENT}")
    print(f"제목: {subject}")
    print(f"본문:\n{body}")

    send_email(gmail_user, gmail_password, subject, body)
    print(f"발송 완료: {subject} ({village['번호']} {village['마을장']} 마을)")


if __name__ == "__main__":
    main()
