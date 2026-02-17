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
    papers: list[Paper],
    all_papers_count: int,
    trends: list[dict],
    weekly_trends: list[dict] | None = None,
    briefing: dict | None = None,
) -> str:
    """HTML 이메일 리포트 생성."""
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")

    # DOI 링크 생성
    for p in papers:
        if p.doi and not p.link:
            p.link = f"https://doi.org/{p.doi}"

    # 주간 트렌드 데이터 포맷
    weekly_trend_text = ""
    if weekly_trends:
        weekly_trend_text = _format_weekly_trends(weekly_trends)

    # 브리핑 데이터 기본값
    if briefing is None:
        briefing = {}

    # 템플릿 렌더링
    template_dir = _get_template_dir()
    env = Environment(loader=FileSystemLoader(template_dir), autoescape=True)
    template = env.get_template("email_template.html")

    # all_papers는 원본 순서 유지 (briefing의 paper_indices와 매칭)
    # display_papers는 PPEL 점수순 정렬 (하단 전체 목록용)
    display_papers = sorted(papers, key=lambda p: p.ppel_score, reverse=True)

    html = template.render(
        date=today,
        total_collected=all_papers_count,
        analyzed_count=len(papers),
        journal_count=len(set(p.journal for p in papers)),
        briefing=briefing,
        weekly_trend_text=weekly_trend_text,
        all_papers=papers,
        display_papers=display_papers,
    )

    logger.info(f"리포트 생성 완료: {len(papers)}편 포함")
    return html


def _format_weekly_trends(weekly_trends: list[dict]) -> str:
    """주간 트렌드를 텍스트 기반 시각화로 포맷."""
    if not weekly_trends:
        return ""

    lines = []
    for item in weekly_trends[:10]:
        keyword = item.get("keyword", "")
        counts = item.get("counts", [])
        if not counts:
            continue

        # 최근 7일 바 차트 (텍스트 기반)
        max_count = max(counts) if max(counts) > 0 else 1
        bars = ""
        for c in counts:
            bar_len = int((c / max_count) * 8) if max_count > 0 else 0
            bars += "\u2588" * bar_len + "\u2591" * (8 - bar_len) + " "

        total = sum(counts)
        lines.append(f"{keyword:<25} {bars} (총 {total}회)")

    return "\n".join(lines)


def get_email_subject(papers: list[Paper]) -> str:
    """이메일 제목 생성."""
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")

    if not papers:
        return f"[Paper Digest] {today} | 오늘은 관련 논문이 없습니다"

    # 최고 PPEL 점수 논문
    top = max(papers, key=lambda p: p.ppel_score)
    # 제목 축약 (40자)
    short_title = top.title[:40] + "..." if len(top.title) > 40 else top.title

    return f"[Paper Digest] {today} | \U0001f525 Top: {short_title}"
