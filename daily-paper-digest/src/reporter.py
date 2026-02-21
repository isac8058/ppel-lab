"""HTML 이메일 리포트 생성 모듈."""

import logging
import os
from datetime import datetime, timezone

from jinja2 import Environment, FileSystemLoader

from src.collector import Paper

logger = logging.getLogger(__name__)


def _get_template_dir() -> str:
    """템플릿 디렉토리 경로."""
    base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base, "templates")


def generate_report(
    featured: dict[str, Paper],
    others: list[Paper],
    field_counts: dict[str, int],
    total_collected: int,
    ai_result: dict | None = None,
) -> str:
    """HTML 이메일 리포트 생성."""
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")

    # DOI 링크 생성
    for p in list(featured.values()) + others:
        if p.doi and not p.link:
            p.link = f"https://doi.org/{p.doi}"

    ai_success = ai_result is not None

    # AI overview 또는 기본 overview
    if ai_success:
        overview = ai_result.get("overview", "")
        field_trends = ai_result.get("field_trends", {})
    else:
        overview = (
            f"오늘 총 {total_collected}편의 논문에서 "
            f"{len(featured)}개 분야, {len(featured) + len(others)}편의 관련 논문이 선별되었습니다."
        )
        field_trends = {}

    # 분야별 트렌드 (AI 없어도 field_counts 기반으로 생성)
    trend_items = []
    for field, count in sorted(field_counts.items(), key=lambda x: -x[1]):
        ai_trend = field_trends.get(field, "")
        trend_items.append({
            "field": field,
            "count": count,
            "trend": ai_trend,
            "has_featured": field in featured,
        })

    template_dir = _get_template_dir()
    env = Environment(loader=FileSystemLoader(template_dir), autoescape=True)
    template = env.get_template("email_template.html")

    html = template.render(
        date=today,
        total_collected=total_collected,
        featured=featured,
        others=others,
        overview=overview,
        trend_items=trend_items,
        ai_success=ai_success,
        featured_count=len(featured),
        others_count=len(others),
    )

    logger.info(
        f"리포트 생성 완료: 대표 {len(featured)}편, 기타 {len(others)}편 "
        f"(AI: {'Y' if ai_success else 'N'})"
    )
    return html


def get_email_subject(featured_count: int) -> str:
    """이메일 제목 생성."""
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")

    if featured_count == 0:
        return f"[PPEL Digest] {today} | 오늘은 관련 논문이 없습니다"

    return f"[PPEL Digest] {today} | {featured_count}개 분야 주요 논문"
