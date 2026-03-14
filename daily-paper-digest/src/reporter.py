"""HTML 이메일 리포트 생성 모듈 (주간 다이제스트)."""

import logging
import os
from collections import OrderedDict
from datetime import datetime, timedelta, timezone

from jinja2 import Environment, FileSystemLoader

from src.collector import Paper

logger = logging.getLogger(__name__)


def _get_template_dir() -> str:
    """템플릿 디렉토리 경로."""
    base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base, "templates")


def _ensure_paper_url(paper: Paper) -> str:
    """논문의 URL을 확보. DOI가 있으면 반드시 링크 생성."""
    if paper.url:
        return paper.url
    if paper.link:
        return paper.link
    if paper.doi:
        return f"https://doi.org/{paper.doi}"
    return ""


def _ensure_highlight_title(paper: Paper) -> str:
    """highlight_title이 없으면 제목에서 생성."""
    if paper.highlight_title:
        return paper.highlight_title
    title = paper.title
    if len(title) > 40:
        title = title[:40] + "..."
    return title


def _group_papers_by_sub_group(papers: list[Paper]) -> OrderedDict:
    """논문들을 sub_group별로 그룹핑 (소재 → 응용 → 트렌드 순서)."""
    groups = OrderedDict([
        ("소재", []),
        ("응용", []),
        ("트렌드", []),
    ])

    for p in papers:
        group = p.sub_group if p.sub_group in groups else "소재"
        groups[group].append(p)

    return groups


def _get_date_range(collection_days: int = 7) -> tuple[str, str, str]:
    """주간 날짜 범위 반환: (date_range_display, start_date, end_date)."""
    today = datetime.now(timezone.utc)
    start = today - timedelta(days=collection_days)
    start_str = start.strftime("%Y-%m-%d")
    end_str = today.strftime("%Y-%m-%d")
    return f"{start_str} ~ {end_str}", start_str, end_str


def generate_report(
    categorized_papers: dict[str, list[Paper]],
    categories_config: dict,
    ai_result: dict | None = None,
    collection_days: int = 7,
) -> str:
    """HTML 이메일 리포트 생성."""
    date_range, start_date, end_date = _get_date_range(collection_days)

    # 각 논문의 URL 및 highlight_title 확보
    for cat_key, papers in categorized_papers.items():
        for p in papers:
            p.url = _ensure_paper_url(p)
            p.highlight_title = _ensure_highlight_title(p)
            if not p.summary_kr:
                abstract = p.abstract or ""
                p.summary_kr = abstract[:100] + "..." if len(abstract) > 100 else abstract

    # 총 논문 수
    total_papers = sum(len(papers) for papers in categorized_papers.values())
    review_count = total_papers

    # 카테고리 섹션 구성
    template_categories = []
    for cat_key, cat_info in categories_config.items():
        papers = categorized_papers.get(cat_key, [])
        if not papers:
            template_categories.append({
                "name": cat_info.get("name", cat_key),
                "icon": cat_info.get("icon", "📄"),
                "css_class": cat_info.get("css_class", ""),
                "papers": [],
                "grouped_papers": OrderedDict(),
            })
            continue

        grouped = _group_papers_by_sub_group(papers)

        template_categories.append({
            "name": cat_info.get("name", cat_key),
            "icon": cat_info.get("icon", "📄"),
            "css_class": cat_info.get("css_class", ""),
            "papers": papers,
            "grouped_papers": grouped,
        })

    # 주간 총평
    weekly_summary = ""
    if ai_result:
        weekly_summary = ai_result.get("weekly_summary", "")
    if not weekly_summary:
        weekly_summary = (
            f"<p>이번 주 총 {total_papers}편의 논문이 7개 분야에서 선별되었습니다. "
            f"자세한 분석은 다음 주에 제공됩니다.</p>"
        )

    template_dir = _get_template_dir()
    env = Environment(loader=FileSystemLoader(template_dir), autoescape=True)
    template = env.get_template("weekly_email_template.html")

    html = template.render(
        date_range=date_range,
        total_papers=total_papers,
        review_count=review_count,
        categories=template_categories,
        weekly_summary=weekly_summary,
    )

    cat_summary = {c["name"]: len(c["papers"]) for c in template_categories if c["papers"]}
    logger.info(
        f"리포트 생성 완료: 총 {total_papers}편, "
        f"카테고리 분포 {cat_summary}"
    )
    return html


def get_email_subject(config: dict, total_categories: int = 7) -> str:
    """이메일 제목 생성."""
    _, start_date, end_date = _get_date_range(
        config.get("schedule", {}).get("collection_window_days", 7)
    )

    subject_fmt = config.get("email", {}).get(
        "subject_format",
        "[PPEL Digest] {start_date}~{end_date} | {total}개 분야 주요 논문"
    )

    return subject_fmt.format(
        start_date=start_date,
        end_date=end_date,
        total=total_categories,
    )
