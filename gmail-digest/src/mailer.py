"""이메일 요약 리포트를 SMTP로 발송합니다."""

import logging
import os
import smtplib
from datetime import datetime, timezone, timedelta
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

logger = logging.getLogger(__name__)

KST = timezone(timedelta(hours=9))

EMAIL_TEMPLATE = """<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<style>
  body {{ font-family: -apple-system, 'Segoe UI', sans-serif; background: #f5f5f5; margin: 0; padding: 20px; }}
  .container {{ max-width: 640px; margin: 0 auto; background: #fff; border-radius: 12px; overflow: hidden; box-shadow: 0 2px 8px rgba(0,0,0,0.08); }}
  .header {{ background: linear-gradient(135deg, #1a73e8, #4285f4); color: white; padding: 24px 28px; }}
  .header h1 {{ margin: 0; font-size: 20px; font-weight: 600; }}
  .header p {{ margin: 6px 0 0; opacity: 0.85; font-size: 13px; }}
  .summary {{ background: #e8f0fe; padding: 16px 28px; border-left: 4px solid #1a73e8; margin: 20px 28px; border-radius: 6px; font-size: 14px; line-height: 1.6; color: #1a1a1a; }}
  .email-card {{ margin: 12px 28px; padding: 16px; border: 1px solid #e0e0e0; border-radius: 8px; }}
  .email-card.high {{ border-left: 4px solid #d93025; }}
  .email-card.medium {{ border-left: 4px solid #f9ab00; }}
  .badge {{ display: inline-block; padding: 2px 8px; border-radius: 4px; font-size: 11px; font-weight: 600; margin-right: 6px; }}
  .badge.high {{ background: #fce8e6; color: #d93025; }}
  .badge.medium {{ background: #fef7e0; color: #e37400; }}
  .badge.category {{ background: #e8f0fe; color: #1967d2; }}
  .email-subject {{ font-weight: 600; font-size: 14px; margin: 6px 0 4px; color: #1a1a1a; }}
  .email-meta {{ font-size: 12px; color: #666; margin-bottom: 6px; }}
  .email-summary {{ font-size: 13px; color: #333; line-height: 1.5; }}
  .email-action {{ font-size: 12px; color: #d93025; margin-top: 6px; font-weight: 500; }}
  .footer {{ text-align: center; padding: 20px; font-size: 11px; color: #999; }}
  .empty {{ text-align: center; padding: 40px 28px; color: #666; }}
</style>
</head>
<body>
<div class="container">
  <div class="header">
    <h1>📬 Gmail Weekly Digest</h1>
    <p>{date} | {total_count}개 수신 → {important_count}개 중요</p>
  </div>

  {summary_section}

  {email_cards}

  <div class="footer">
    PPEL Lab Gmail Digest &middot; 매주 월요일 KST 07:30 자동 발송<br>
    GitHub Actions 기반 자동화
  </div>
</div>
</body>
</html>"""


def _build_email_card(item: dict) -> str:
    """개별 이메일 카드 HTML을 생성합니다."""
    importance = item.get("importance", 0)
    level = "high" if importance >= 8 else "medium"
    level_label = "🔴 HIGH" if importance >= 8 else "🟡 MEDIUM"

    action_html = ""
    action = item.get("action_needed", "")
    if action:
        action_html = f'<div class="email-action">→ {action}</div>'

    return f"""
    <div class="email-card {level}">
      <div>
        <span class="badge {level}">{level_label} ({importance})</span>
        <span class="badge category">{item.get("category", "")}</span>
      </div>
      <div class="email-subject">{item.get("subject", "제목 없음")}</div>
      <div class="email-meta">{item.get("sender", "")} &middot; {item.get("date", "")}</div>
      <div class="email-summary">{item.get("summary_kr", "")}</div>
      {action_html}
    </div>"""


def send_digest(
    analysis: dict | None,
    total_count: int,
    recipient: str,
) -> bool:
    """분석 결과를 이메일로 발송합니다.

    Args:
        analysis: Gemini 분석 결과 dict
        total_count: 전체 수신 이메일 수
        recipient: 수신자 이메일 주소

    Returns:
        발송 성공 여부
    """
    gmail_user = os.environ.get("GMAIL_USER", "")
    gmail_pass = os.environ.get("GMAIL_APP_PASSWORD", "")

    if not gmail_user or not gmail_pass:
        logger.error("GMAIL_USER 또는 GMAIL_APP_PASSWORD가 설정되지 않았습니다.")
        return False

    now_kst = datetime.now(KST)
    date_str = now_kst.strftime("%Y-%m-%d (%a)")

    if analysis and analysis.get("emails"):
        important_emails = analysis["emails"]
        important_count = len(important_emails)

        summary_section = f'<div class="summary">{analysis.get("weekly_summary", "")}</div>'
        email_cards = "\n".join(_build_email_card(item) for item in important_emails)
    else:
        important_count = 0
        summary_section = '<div class="empty">이번 주는 특별히 중요한 이메일이 없습니다. 좋은 한 주 되세요! 🎉</div>'
        email_cards = ""

    html = EMAIL_TEMPLATE.format(
        date=date_str,
        total_count=total_count,
        important_count=important_count,
        summary_section=summary_section,
        email_cards=email_cards,
    )

    # 이메일 구성
    msg = MIMEMultipart("alternative")
    msg["Subject"] = f"[Weekly Digest] {date_str} | {important_count}개 중요 메일"
    msg["From"] = gmail_user
    msg["To"] = recipient
    msg.attach(MIMEText(html, "html", "utf-8"))

    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(gmail_user, gmail_pass)
            server.send_message(msg)
        logger.info(f"Gmail Digest 발송 완료 → {recipient}")
        return True
    except Exception as e:
        logger.error(f"이메일 발송 실패: {e}")
        return False
