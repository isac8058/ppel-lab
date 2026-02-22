"""
식당봉사 주간 알림 스크립트
- 매주 토요일에 다음 주 일요일 봉사팀을 카카오톡으로 알림
- 기준: 2026-03-01(일) 1팀 시작, 이후 매주 순환
"""

import os
import sys
from datetime import date, timedelta
import requests

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


def get_duty_team(saturday: date) -> dict:
    """해당 토요일 기준 다음 날(일) 봉사팀 반환"""
    days_since_ref = (saturday - REFERENCE_SATURDAY).days
    week_index = days_since_ref // 7
    team_index = week_index % len(TEAMS)
    return TEAMS[team_index]


def get_kakao_access_token(refresh_token: str, client_id: str) -> str:
    """Kakao refresh token으로 새 access token 발급"""
    resp = requests.post(
        "https://kauth.kakao.com/oauth/token",
        data={
            "grant_type": "refresh_token",
            "client_id": client_id,
            "refresh_token": refresh_token,
        },
        timeout=10,
    )
    resp.raise_for_status()
    data = resp.json()
    if "access_token" not in data:
        raise RuntimeError(f"카카오 토큰 갱신 실패: {data}")
    return data["access_token"]


def send_kakao_message(access_token: str, text: str) -> None:
    """카카오톡 나에게 보내기"""
    payload = {
        "object_type": "text",
        "text": text,
        "link": {
            "web_url": "",
            "mobile_web_url": "",
        },
    }
    resp = requests.post(
        "https://kapi.kakao.com/v2/api/talk/memo/default/send",
        headers={"Authorization": f"Bearer {access_token}"},
        data={"template_object": __import__("json").dumps(payload, ensure_ascii=False)},
        timeout=10,
    )
    resp.raise_for_status()
    result = resp.json()
    if result.get("result_code") != 0:
        raise RuntimeError(f"카카오톡 전송 실패: {result}")


def build_message(team: dict, sunday: date) -> str:
    members_str = ", ".join(team["members"])
    return (
        f"[식당봉사 알림]\n"
        f"📅 일시: {sunday.strftime('%Y년 %m월 %d일')} (일요일)\n\n"
        f"이번 주 봉사팀: {team['name']}\n"
        f"  조장: {team['leader']}\n"
        f"  팀원: {members_str}\n\n"
        f"봉사에 수고해 주세요! 🙏"
    )


def main():
    kakao_refresh_token = os.environ.get("KAKAO_REFRESH_TOKEN")
    kakao_client_id = os.environ.get("KAKAO_CLIENT_ID")

    if not kakao_refresh_token or not kakao_client_id:
        print("오류: 환경변수 KAKAO_REFRESH_TOKEN, KAKAO_CLIENT_ID 를 설정하세요.")
        sys.exit(1)

    today = date.today()

    # 가장 가까운 토요일(당일 포함)을 기준으로 계산
    # GitHub Actions는 토요일에 실행되므로 today가 토요일
    # weekday(): 월=0 ... 토=5 ... 일=6
    if today.weekday() != 5:
        print(f"경고: 오늘({today})은 토요일이 아닙니다. 계속 실행합니다.")

    saturday = today
    sunday = saturday + timedelta(days=1)

    team = get_duty_team(saturday)
    message = build_message(team, sunday)

    print(f"발송 메시지:\n{message}\n")

    access_token = get_kakao_access_token(kakao_refresh_token, kakao_client_id)
    send_kakao_message(access_token, message)
    print("카카오톡 알림 전송 완료!")


if __name__ == "__main__":
    main()
