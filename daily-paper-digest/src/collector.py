"""RSS/API 기반 논문 수집 모듈."""

import logging
import re
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone

import feedparser
import requests
import yaml

logger = logging.getLogger(__name__)


@dataclass
class Paper:
    """수집된 논문 데이터."""

    title: str
    abstract: str
    doi: str
    authors: list[str]
    journal: str
    published_date: datetime
    link: str = ""
    keywords: list[str] = field(default_factory=list)
    relevance_score: float = 0.0
    summary: str = ""
    novelty: str = ""
    tags: list[str] = field(default_factory=list)
    ppel_score: int = 0
    relevance_label: str = ""


def load_config(config_path: str = "config.yaml") -> dict:
    """설정 파일 로드."""
    with open(config_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def _parse_date(entry: dict) -> datetime | None:
    """RSS 엔트리에서 날짜 파싱."""
    date_fields = ["published_parsed", "updated_parsed"]
    for field_name in date_fields:
        parsed = entry.get(field_name)
        if parsed:
            try:
                return datetime(*parsed[:6], tzinfo=timezone.utc)
            except (ValueError, TypeError):
                continue

    date_str_fields = ["published", "updated", "dc_date"]
    for field_name in date_str_fields:
        date_str = entry.get(field_name, "")
        if date_str:
            for fmt in [
                "%a, %d %b %Y %H:%M:%S %z",
                "%Y-%m-%dT%H:%M:%S%z",
                "%Y-%m-%dT%H:%M:%SZ",
                "%Y-%m-%d",
            ]:
                try:
                    return datetime.strptime(date_str, fmt).replace(tzinfo=timezone.utc)
                except ValueError:
                    continue
    return None


def _extract_doi(entry: dict) -> str:
    """RSS 엔트리에서 DOI 추출."""
    # prism:doi 태그
    doi = entry.get("prism_doi", "") or entry.get("dc_identifier", "")
    if doi and doi.startswith("10."):
        return doi

    # 링크에서 DOI 추출
    link = entry.get("link", "") or entry.get("id", "")
    doi_match = re.search(r"(10\.\d{4,}/[^\s&?#]+)", link)
    if doi_match:
        return doi_match.group(1)

    # id 필드
    entry_id = entry.get("id", "")
    doi_match = re.search(r"(10\.\d{4,}/[^\s&?#]+)", entry_id)
    if doi_match:
        return doi_match.group(1)

    return ""


def _extract_abstract(entry: dict) -> str:
    """RSS 엔트리에서 초록 추출."""
    # summary 필드
    abstract = entry.get("summary", "")
    if abstract:
        # HTML 태그 제거
        abstract = re.sub(r"<[^>]+>", "", abstract).strip()
        if len(abstract) > 50:
            return abstract

    # description 필드
    desc = entry.get("description", "")
    if desc:
        desc = re.sub(r"<[^>]+>", "", desc).strip()
        if len(desc) > 50:
            return desc

    # content 필드
    content = entry.get("content", [])
    if content and isinstance(content, list):
        for c in content:
            text = c.get("value", "")
            text = re.sub(r"<[^>]+>", "", text).strip()
            if len(text) > 50:
                return text

    return abstract or desc or ""


def _extract_authors(entry: dict) -> list[str]:
    """RSS 엔트리에서 저자 추출."""
    authors = []

    # authors 필드
    if "authors" in entry:
        for a in entry["authors"]:
            name = a.get("name", "")
            if name:
                authors.append(name)

    # author 필드
    if not authors and "author" in entry:
        author = entry["author"]
        if isinstance(author, str):
            authors = [a.strip() for a in author.split(",")]

    # author_detail 필드
    if not authors and "author_detail" in entry:
        name = entry["author_detail"].get("name", "")
        if name:
            authors = [name]

    return authors


def fetch_crossref_abstract(doi: str) -> str:
    """CrossRef API로 초록 보완."""
    if not doi:
        return ""
    try:
        url = f"https://api.crossref.org/works/{doi}"
        headers = {"User-Agent": "DailyPaperDigest/1.0 (mailto:smlim@jbnu.ac.kr)"}
        resp = requests.get(url, headers=headers, timeout=10)
        if resp.status_code == 200:
            data = resp.json()
            abstract = data.get("message", {}).get("abstract", "")
            if abstract:
                return re.sub(r"<[^>]+>", "", abstract).strip()
    except Exception as e:
        logger.debug(f"CrossRef API 호출 실패 (DOI: {doi}): {e}")
    return ""


def collect_papers(config: dict) -> list[Paper]:
    """모든 저널에서 논문 수집."""
    journals = config.get("journals", [])
    time_window = config.get("analysis", {}).get("time_window_hours", 48)
    cutoff = datetime.now(timezone.utc) - timedelta(hours=time_window)
    all_papers = []

    for journal in journals:
        name = journal["name"]
        url = journal["url"]
        logger.info(f"수집 중: {name}")

        try:
            feed = feedparser.parse(url)
            if feed.bozo and not feed.entries:
                logger.warning(f"RSS 파싱 실패: {name} - {feed.bozo_exception}")
                continue

            count = 0
            for entry in feed.entries:
                pub_date = _parse_date(entry)

                # 날짜 파싱 실패시 최근 논문으로 간주
                if pub_date is None:
                    pub_date = datetime.now(timezone.utc)

                # 시간 범위 필터링
                if pub_date < cutoff:
                    continue

                title = entry.get("title", "").strip()
                if not title:
                    continue

                doi = _extract_doi(entry)
                abstract = _extract_abstract(entry)

                # 초록 없으면 CrossRef API로 보완
                if not abstract and doi:
                    abstract = fetch_crossref_abstract(doi)

                authors = _extract_authors(entry)
                link = entry.get("link", "")

                paper = Paper(
                    title=title,
                    abstract=abstract,
                    doi=doi,
                    authors=authors,
                    journal=name,
                    published_date=pub_date,
                    link=link,
                )
                all_papers.append(paper)
                count += 1

            logger.info(f"  {name}: {count}편 수집")

        except Exception as e:
            logger.error(f"저널 수집 실패: {name} - {e}")
            continue

    logger.info(f"총 {len(all_papers)}편 수집 완료")
    return all_papers
