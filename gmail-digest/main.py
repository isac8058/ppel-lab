"""Gmail Weekly Digest - 매주 월요일 한 주간 중요 이메일을 분석하여 총평 발송."""

import logging
import os
import sys

from src.gmail_reader import read_recent_emails
from src.email_analyzer import EmailAnalyzer
from src.mailer import send_digest

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger(__name__)

# 설정
RECIPIENT = os.environ.get("DIGEST_RECIPIENT", "smlim@jbnu.ac.kr")
HOURS_LOOKBACK = int(os.environ.get("HOURS_LOOKBACK", "168"))
MIN_IMPORTANCE = int(os.environ.get("MIN_IMPORTANCE", "5"))


def main():
    logger.info("=" * 50)
    logger.info("Gmail Weekly Digest 시작")
    logger.info("=" * 50)

    gmail_user = os.environ.get("GMAIL_USER", "")
    gmail_pass = os.environ.get("GMAIL_APP_PASSWORD", "")

    if not gmail_user or not gmail_pass:
        logger.error("GMAIL_USER 또는 GMAIL_APP_PASSWORD 환경변수가 필요합니다.")
        sys.exit(1)

    # 1. Gmail에서 최근 이메일 읽기
    logger.info(f"[1/3] Gmail에서 최근 {HOURS_LOOKBACK}시간 이메일 수집...")
    emails = read_recent_emails(
        gmail_user=gmail_user,
        gmail_app_password=gmail_pass,
        hours=HOURS_LOOKBACK,
    )
    total_count = len(emails)
    logger.info(f"  → {total_count}개 유효 이메일 수집 완료")

    # 2. Gemini로 중요도 분석
    analysis = None
    if emails:
        logger.info("[2/3] Gemini로 이메일 중요도 분석 중...")
        try:
            analyzer = EmailAnalyzer()
            analysis = analyzer.analyze(emails, min_score=MIN_IMPORTANCE)
            if analysis:
                important = len(analysis.get("emails", []))
                logger.info(f"  → {important}개 중요 이메일 발견")
            else:
                logger.info("  → Gemini 분석 실패, 기본 리포트 발송")
        except Exception as e:
            logger.warning(f"  → Gemini 분석 불가: {e}")
    else:
        logger.info("[2/3] 분석할 이메일 없음, 건너뜀")

    # 3. 요약 이메일 발송
    logger.info(f"[3/3] 요약 이메일 발송 → {RECIPIENT}")
    success = send_digest(
        analysis=analysis,
        total_count=total_count,
        recipient=RECIPIENT,
    )

    if success:
        logger.info("Gmail Weekly Digest 완료!")
    else:
        logger.error("이메일 발송 실패!")
        sys.exit(1)


if __name__ == "__main__":
    main()
