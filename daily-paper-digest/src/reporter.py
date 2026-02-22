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


def _generate_field_comment(
    field: str, stats: dict, featured_paper: Paper | None
) -> str:
    """분야별 분석 코멘트를 데이터 기반으로 생성."""
    count = stats["count"]
    top_journals = stats.get("top_journals", [])
    hot_subtopics = stats.get("hot_subtopics", [])

    parts = []

    # 저널 동향
    if top_journals:
        journal_names = [f"{j}({c}편)" for j, c in top_journals[:2]]
        parts.append(f"주요 게재: {', '.join(journal_names)}")

    # 세부 키워드 트렌드
    if hot_subtopics:
        top_kws = [f"{kw}({c})" for kw, c in hot_subtopics[:3]]
        parts.append(f"주요 키워드: {', '.join(top_kws)}")

    # 대표 논문 기반 코멘트
    if featured_paper and featured_paper.novelty:
        parts.append(f"주목: {featured_paper.novelty}")

    if not parts:
        parts.append(f"총 {count}편 발표")

    return ". ".join(parts) + "."


def _generate_overview(
    total_collected: int,
    featured: dict[str, Paper],
    field_stats: dict[str, dict],
) -> str:
    """데이터 기반 overview 생성."""
    total_related = sum(s["count"] for s in field_stats.values())

    # 가장 활발한 분야
    if field_stats:
        top_field = max(field_stats.items(), key=lambda x: x[1]["count"])
        top_name, top_stat = top_field

        # 전체에서 가장 핫한 서브토픽
        all_subtopics = []
        for s in field_stats.values():
            all_subtopics.extend(s.get("hot_subtopics", []))
        all_subtopics.sort(key=lambda x: -x[1])
        hot_kw = all_subtopics[0][0] if all_subtopics else ""

        overview = (
            f"오늘 총 {total_collected}편의 논문 중 PPEL 관련 {total_related}편이 확인되었습니다. "
            f"{top_name} 분야가 {top_stat['count']}편으로 가장 활발하며"
        )
        if hot_kw:
            overview += f", '{hot_kw}' 관련 연구가 두드러집니다."
        else:
            overview += "."

        # 저널 다양성
        all_journals = set()
        for s in field_stats.values():
            for j, _ in s.get("top_journals", []):
                all_journals.add(j)
        if len(all_journals) >= 3:
            overview += (
                f" {', '.join(list(all_journals)[:3])} 등 "
                f"다양한 저널에서 관련 연구가 발표되었습니다."
            )
    else:
        overview = f"오늘 총 {total_collected}편의 논문이 수집되었습니다."

    return overview


def generate_report(
    featured: dict[str, Paper],
    others: list[Paper],
    field_stats: dict[str, dict],
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

    # Overview
    if ai_success and ai_result.get("overview"):
        overview = ai_result["overview"]
    else:
        overview = _generate_overview(total_collected, featured, field_stats)

    # 분야별 트렌드 + 분석 코멘트
    ai_field_trends = ai_result.get("field_trends", {}) if ai_result else {}

    trend_items = []
    for field, stats in sorted(field_stats.items(), key=lambda x: -x[1]["count"]):
        # AI 트렌드가 있으면 우선 사용, 없으면 데이터 기반 생성
        if field in ai_field_trends and ai_field_trends[field]:
            comment = ai_field_trends[field]
        else:
            comment = _generate_field_comment(
                field, stats, featured.get(field)
            )

        trend_items.append({
            "field": field,
            "count": stats["count"],
            "comment": comment,
            "has_featured": field in featured,
            "hot_subtopics": [kw for kw, _ in stats.get("hot_subtopics", [])[:3]],
        })

    # Featured 논문에 분석 코멘트 추가 (AI summary 없는 경우)
    featured_comments = {}
    for field, paper in featured.items():
        if paper.summary:
            featured_comments[field] = paper.summary
        elif field in field_stats:
            featured_comments[field] = _generate_field_comment(
                field, field_stats[field], paper
            )

    template_dir = _get_template_dir()
    env = Environment(loader=FileSystemLoader(template_dir), autoescape=True)
    template = env.get_template("email_template.html")

    html = template.render(
        date=today,
        total_collected=total_collected,
        featured=featured,
        featured_comments=featured_comments,
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
