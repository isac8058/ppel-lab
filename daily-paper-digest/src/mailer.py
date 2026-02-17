"""SMTP 이메일 발송 모듈."""

import logging
import os
import smtplib
import time
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

logger = logging.getLogger(__name__)


def send_email(
    subject: str,
    html_body: str,
    recipient: str = "smlim@jbnu.ac.kr",
    max_retries: int = 3,
) -> bool:
    """Gmail SMTP로 HTML 이메일 발송."""
    gmail_user = os.environ.get("GMAIL_USER", "")
    gmail_password = os.environ.get("GMAIL_APP_PASSWORD", "")

    if not gmail_user or not gmail_password:
        logger.error("GMAIL_USER 또는 GMAIL_APP_PASSWORD 환경변수가 설정되지 않았습니다.")
        return False

    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = gmail_user
    msg["To"] = recipient

    # HTML 본문
    html_part = MIMEText(html_body, "html", "utf-8")
    msg.attach(html_part)

    # 재시도 로직 (지수 백오프)
    for attempt in range(max_retries):
        try:
            with smtplib.SMTP("smtp.gmail.com", 587, timeout=30) as server:
                server.ehlo()
                server.starttls()
                server.ehlo()
                server.login(gmail_user, gmail_password)
                server.sendmail(gmail_user, [recipient], msg.as_string())

            logger.info(f"이메일 발송 성공: {recipient}")
            return True

        except Exception as e:
            wait = 2 ** (attempt + 1)
            logger.warning(
                f"이메일 발송 실패 (시도 {attempt + 1}/{max_retries}): {e}"
            )
            if attempt < max_retries - 1:
                logger.info(f"{wait}초 후 재시도...")
                time.sleep(wait)

    logger.error(f"이메일 발송 최종 실패: {recipient}")
    return False
