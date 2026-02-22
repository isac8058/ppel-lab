"""
부목자 월간 모임 알림 스크립트
- 매월 마지막 주 주일 전날(토요일)에 발송
- 5개 마을 순환 (기준: 2026년 2월 = 209 정상연)
- 기도 / 말씀 요약 / 간식당번 랜덤 배정 (월별 고정 seed)
"""

import os
import sys
import smtplib
import random
import calendar
from datetime import date, timedelta
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# ─────────────────────────────────────────────
# 마을별 부목자 명단
# ─────────────────────────────────────────────
VILLAGES = [
    {
        "name": "209 정상연",
        "members": ["김호기", "김현호A", "김진남", "이정일", "김도윤B"],
    },
    {
        "name": "210 배철한",
        "members": ["최성계", "김준영H", "김재근B", "김종민C", "김승호D", "정정진"],
    },
    {
        "name": "211 조윤희F",
        "members": ["김병수C", "진영북", "오선록", "박광진", "최종문A", "이철승"],
    },
    {
        "name": "212 송두헌",
        "members": ["김대연A", "홍성일A", "김중백", "장쾌남", "김경은E", "정준기C"],
    },
    {
        "name": "213 김영석A",
        "members": ["임수만", "김성철E", "정재성A"],
    },
]

# 기준: 2026년 2월 = 인덱스 0 (209 정상연)
REFERENCE_YEAR = 2026
REFERENCE_MONTH = 2

RECIPIENT = "smlim@jbnu.ac.kr"


def last_sunday_of_month(year: int, month: int) -> date:
    last_day = calendar.monthrange(year, month)[1]
    d = date(year, month, last_day)
    # weekday(): 월=0 ... 토=5 ... 일=6
    days_back = (d.weekday() + 1) % 7
    return d - timedelta(days=days_back)


def get_village_for_month(year: int, month: int) -> dict:
    months_since_ref = (year - REFERENCE_YEAR) * 12 + (month - REFERENCE_MONTH)
    return VILLAGES[months_since_ref % len(VILLAGES)]


def assign_roles(village: dict, year: int, month: int) -> tuple:
    """기도 / 말씀요약 / 간식담당 랜덤 배정 (같은 달엔 항상 동일하게 나오도록 seed 고정)"""
    rng = random.Random(year * 100 + month)
    prayer, word_summary, snack = rng.sample(village["members"], 3)
    return prayer, word_summary, snack


def build_email(village: dict, roles: tuple, sunday: date) -> tuple:
    """(제목, 본문) 반환 — 그대로 복사해 공지로 사용 가능한 형식"""
    prayer, word_summary, snack = roles
    m, d = sunday.month, sunday.day

    subject = f"[공지] {m}월 부목자 모임 안내"
    body = f"""\
[공지] 부목자 모임 안내

샬롬! 부목자님들, 평안하신지요.
매월 넷째 주 주일은 정기 부목자 모임이 있는 날입니다. 다가오는 이번 주 주일({d}일)에 부목자 모임으로 모이고자 하오니, 모든 부목자님들께서 빠짐없이 참석해 주시기를 부탁드립니다.

■ 일시: {m}월 {d}일(주일) 오후 4시
■ 장소: 새가족실
■ 이번 달 순서 담당 안내 ({village['name']} 마을)
 * 기도: {prayer} 부목자님
 * 말씀 요약: {word_summary} 부목자님
 * 간식: {snack} 부목자님
(담당 역할은 상황에 따라 다른 분과 자유롭게 변경 가능합니다. 변경이 필요하신 경우 편하게 조율해 주시기 바랍니다.)

원활한 모임 준비를 위해 참석 여부를 파악하고 있습니다. 공지를 확인하신 부목자님들께서는 참석 여부를 회신해 주시면 감사하겠습니다.

주일에 기쁜 모습으로 뵙겠습니다!
"""
    return subject, body


def send_email(gmail_user: str, gmail_password: str, subject: str, body: str) -> None:
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

    # 이 스크립트는 토요일에 실행됨
    # 내일(일요일)이 해당 월의 마지막 주 일요일인지 확인
    tomorrow = today + timedelta(days=1)
    year, month = tomorrow.year, tomorrow.month
    last_sun = last_sunday_of_month(year, month)

    if tomorrow != last_sun:
        print(f"내일({tomorrow})은 마지막 주 일요일이 아닙니다 (마지막 주 일요일: {last_sun}). 종료.")
        sys.exit(0)

    village = get_village_for_month(year, month)
    roles = assign_roles(village, year, month)
    subject, body = build_email(village, roles, last_sun)

    print(f"수신: {RECIPIENT}")
    print(f"제목: {subject}")
    print(f"본문:\n{body}")

    send_email(gmail_user, gmail_password, subject, body)
    print("이메일 전송 완료!")


if __name__ == "__main__":
    main()
