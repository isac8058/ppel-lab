"""Gmail IMAP 리더 - 최근 24시간 이메일을 읽어옵니다."""

import email
import imaplib
import logging
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from email.header import decode_header
from email.utils import parsedate_to_datetime

logger = logging.getLogger(__name__)

# 자동 무시할 발신자 패턴 (프로모션/스팸/자동알림)
SKIP_SENDERS = [
    "noreply", "no-reply", "mailer-daemon", "postmaster",
    "notifications@", "digest@", "newsletter@",
    "marketing@", "promotions@", "ads@", "deals@",
    "innovations.samsungusa.com", "sv.cub.com",
    "premium@academia-mail.com", "ccsend.com",
    "quora.com",
]

# 자동 무시할 제목 패턴
SKIP_SUBJECTS = [
    "unsubscribe", "pre-order", "savings", "discount",
    "don't miss", "limited time", "special offer",
    "your single-use code", "verify your email",
]


@dataclass
class EmailMessage:
    """파싱된 이메일 메시지."""
    msg_id: str
    subject: str
    sender: str
    sender_name: str
    date: datetime
    snippet: str  # 본문 앞 500자
    labels: list[str] = field(default_factory=list)
    is_reply: bool = False

    def to_analysis_text(self) -> str:
        """Gemini 분석용 텍스트."""
        return (
            f"From: {self.sender_name} <{self.sender}>\n"
            f"Subject: {self.subject}\n"
            f"Date: {self.date.strftime('%Y-%m-%d %H:%M')}\n"
            f"Body preview: {self.snippet}\n"
        )


def _decode_mime_header(header_value: str) -> str:
    """MIME 인코딩된 헤더를 디코딩합니다."""
    if not header_value:
        return ""
    parts = decode_header(header_value)
    decoded = []
    for part, charset in parts:
        if isinstance(part, bytes):
            decoded.append(part.decode(charset or "utf-8", errors="replace"))
        else:
            decoded.append(part)
    return " ".join(decoded)


def _extract_body(msg: email.message.Message, max_len: int = 500) -> str:
    """이메일 본문에서 텍스트를 추출합니다."""
    body = ""
    if msg.is_multipart():
        for part in msg.walk():
            content_type = part.get_content_type()
            if content_type == "text/plain":
                try:
                    charset = part.get_content_charset() or "utf-8"
                    body = part.get_payload(decode=True).decode(charset, errors="replace")
                    break
                except Exception:
                    continue
            elif content_type == "text/html" and not body:
                try:
                    charset = part.get_content_charset() or "utf-8"
                    raw = part.get_payload(decode=True).decode(charset, errors="replace")
                    # 간단한 HTML 태그 제거
                    import re
                    body = re.sub(r"<[^>]+>", " ", raw)
                    body = re.sub(r"\s+", " ", body).strip()
                except Exception:
                    continue
    else:
        try:
            charset = msg.get_content_charset() or "utf-8"
            body = msg.get_payload(decode=True).decode(charset, errors="replace")
        except Exception:
            body = ""

    # 공백 정리 및 길이 제한
    body = " ".join(body.split())
    return body[:max_len] if body else "(본문 없음)"


def _should_skip(sender: str, subject: str) -> bool:
    """프로모션/스팸 이메일인지 판단합니다."""
    sender_lower = sender.lower()
    subject_lower = subject.lower()

    for pattern in SKIP_SENDERS:
        if pattern in sender_lower:
            return True
    for pattern in SKIP_SUBJECTS:
        if pattern in subject_lower:
            return True
    return False


def read_recent_emails(
    gmail_user: str,
    gmail_app_password: str,
    hours: int = 24,
    max_emails: int = 50,
) -> list[EmailMessage]:
    """Gmail IMAP으로 최근 N시간 이내 이메일을 읽어옵니다.

    Args:
        gmail_user: Gmail 주소
        gmail_app_password: Gmail 앱 비밀번호
        hours: 몇 시간 이내 이메일을 읽을지
        max_emails: 최대 읽을 이메일 수

    Returns:
        EmailMessage 리스트 (최신순)
    """
    since_date = (datetime.now(timezone.utc) - timedelta(hours=hours)).strftime("%d-%b-%Y")

    logger.info(f"Gmail IMAP 연결 중... (since {since_date})")

    try:
        mail = imaplib.IMAP4_SSL("imap.gmail.com")
        mail.login(gmail_user, gmail_app_password)
        mail.select("INBOX", readonly=True)
    except Exception as e:
        logger.error(f"Gmail IMAP 연결 실패: {e}")
        return []

    try:
        # 최근 N시간 이내 이메일 검색
        _, data = mail.search(None, f'(SINCE "{since_date}")')
        msg_ids = data[0].split()

        if not msg_ids:
            logger.info("새 이메일이 없습니다.")
            mail.logout()
            return []

        # 최신 이메일부터 처리 (최대 max_emails개)
        msg_ids = msg_ids[-max_emails:]
        msg_ids.reverse()

        emails: list[EmailMessage] = []

        for mid in msg_ids:
            try:
                _, msg_data = mail.fetch(mid, "(RFC822)")
                raw = msg_data[0][1]
                msg = email.message_from_bytes(raw)

                subject = _decode_mime_header(msg.get("Subject", ""))
                from_header = _decode_mime_header(msg.get("From", ""))

                # 발신자 파싱
                if "<" in from_header:
                    sender_name = from_header.split("<")[0].strip().strip('"')
                    sender_addr = from_header.split("<")[1].rstrip(">")
                else:
                    sender_name = from_header
                    sender_addr = from_header

                # 프로모션/스팸 필터링
                if _should_skip(sender_addr, subject):
                    continue

                # 자기 자신이 보낸 메일 제외 (PPEL Digest 등)
                if sender_addr.lower() == gmail_user.lower():
                    continue

                # 날짜 파싱
                date_str = msg.get("Date", "")
                try:
                    msg_date = parsedate_to_datetime(date_str)
                except Exception:
                    msg_date = datetime.now(timezone.utc)

                # 본문 추출
                snippet = _extract_body(msg, max_len=500)

                # Reply 여부
                is_reply = subject.lower().startswith(("re:", "답장:"))

                emails.append(EmailMessage(
                    msg_id=mid.decode(),
                    subject=subject,
                    sender=sender_addr,
                    sender_name=sender_name or sender_addr,
                    date=msg_date,
                    snippet=snippet,
                    is_reply=is_reply,
                ))

            except Exception as e:
                logger.warning(f"이메일 파싱 실패 (ID {mid}): {e}")
                continue

        logger.info(f"총 {len(emails)}개 유효 이메일 수집 (프로모션/스팸 제외)")
        return emails

    finally:
        try:
            mail.logout()
        except Exception:
            pass
