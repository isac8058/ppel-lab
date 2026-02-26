"""HTML 이메일 리포트 생성 모듈."""

import logging
import os
from collections import defaultdict
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
        field_analysis = ai_result.get("field_analysis", {})
    else:
        overview = (
            f"오늘 총 {total_collected}편의 논문에서 "
            f"{len(featured)}개 분야, {len(featured) + len(others)}편의 관련 논문이 선별되었습니다."
        )
        field_analysis = {}

    # others를 분야별로 그룹핑
    field_others: dict[str, list[Paper]] = defaultdict(list)
    unclassified_others: list[Paper] = []
    for p in others:
        label = getattr(p, "relevance_label", "") or ""
        if label:
            field_others[label].append(p)
        else:
            unclassified_others.append(p)

    # 분야별 섹션 구성
    field_sections = []
    for field, paper in featured.items():
        field_sections.append({
            "field": field,
            "count": field_counts.get(field, 1),
            "analysis": field_analysis.get(field, ""),
            "featured": paper,
            "others": field_others.get(field, []),
        })

    template_dir = _get_template_dir()
    env = Environment(loader=FileSystemLoader(template_dir), autoescape=True)
    template = env.get_template("email_template.html")

    html = template.render(
        date=today,
        total_collected=total_collected,
        field_sections=field_sections,
        unclassified_others=unclassified_others,
        overview=overview,
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
