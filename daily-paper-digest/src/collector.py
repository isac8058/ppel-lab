"""RSS/API 기반 논문 수집 모듈 (주간 수집)."""

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
    url: str = ""
    keywords: list[str] = field(default_factory=list)
    relevance_score: float = 0.0
    summary: str = ""
    novelty: str = ""
    tags: list[str] = field(default_factory=list)
    ppel_score: int = 0
    relevance_label: str = ""
    highlight_title: str = ""
    summary_kr: str = ""
    sub_group: str = ""
    category: str = ""


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
    doi = entry.get("prism_doi", "") or entry.get("dc_identifier", "")
    if doi and doi.startswith("10."):
        return doi

    link = entry.get("link", "") or entry.get("id", "")
    doi_match = re.search(r"(10\.\d{4,}/[^\s&?#]+)", link)
    if doi_match:
        return doi_match.group(1)

    entry_id = entry.get("id", "")
    doi_match = re.search(r"(10\.\d{4,}/[^\s&?#]+)", entry_id)
    if doi_match:
        return doi_match.group(1)

    return ""


def _extract_abstract(entry: dict) -> str:
    """RSS 엔트리에서 초록 추출."""
    abstract = entry.get("summary", "")
    if abstract:
        abstract = re.sub(r"<[^>]+>", "", abstract).strip()
        if len(abstract) > 50:
            return abstract

    desc = entry.get("description", "")
    if desc:
        desc = re.sub(r"<[^>]+>", "", desc).strip()
        if len(desc) > 50:
            return desc

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

    if "authors" in entry:
        for a in entry["authors"]:
            name = a.get("name", "")
            if name:
                authors.append(name)

    if not authors and "author" in entry:
        author = entry["author"]
        if isinstance(author, str):
            authors = [a.strip() for a in author.split(",")]

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
        headers = {"User-Agent": "PPELWeeklyDigest/1.0 (mailto:smlim@jbnu.ac.kr)"}
        resp = requests.get(url, headers=headers, timeout=10)
        if resp.status_code == 200:
            data = resp.json()
            abstract = data.get("message", {}).get("abstract", "")
            if abstract:
                return re.sub(r"<[^>]+>", "", abstract).strip()
    except Exception as e:
        logger.debug(f"CrossRef API 호출 실패 (DOI: {doi}): {e}")
    return ""


def fetch_crossref_papers(keywords: list[str], from_date: str, until_date: str, rows: int = 50) -> list[dict]:
    """CrossRef API로 키워드 기반 논문 검색 (RSS 보완용)."""
    query = " OR ".join(keywords[:10])
    url = "https://api.crossref.org/works"
    params = {
        "query": query,
        "filter": f"from-pub-date:{from_date},until-pub-date:{until_date}",
        "rows": rows,
        "sort": "published",
        "order": "desc",
    }
    headers = {"User-Agent": "PPELWeeklyDigest/1.0 (mailto:smlim@jbnu.ac.kr)"}

    try:
        resp = requests.get(url, params=params, headers=headers, timeout=30)
        if resp.status_code == 200:
            items = resp.json().get("message", {}).get("items", [])
            logger.info(f"CrossRef API: {len(items)}편 보완 수집")
            return items
    except Exception as e:
        logger.warning(f"CrossRef API 검색 실패: {e}")
    return []


def _crossref_item_to_paper(item: dict) -> Paper | None:
    """CrossRef API 결과를 Paper 객체로 변환."""
    title_list = item.get("title", [])
    if not title_list:
        return None
    title = title_list[0]

    doi = item.get("DOI", "")
    abstract = item.get("abstract", "")
    if abstract:
        abstract = re.sub(r"<[^>]+>", "", abstract).strip()

    authors = []
    for a in item.get("author", []):
        name = f"{a.get('given', '')} {a.get('family', '')}".strip()
        if name:
            authors.append(name)

    journal = ""
    container = item.get("container-title", [])
    if container:
        journal = container[0]

    pub_date = datetime.now(timezone.utc)
    date_parts = item.get("published", {}).get("date-parts", [[]])
    if date_parts and date_parts[0]:
        parts = date_parts[0]
        try:
            year = parts[0]
            month = parts[1] if len(parts) > 1 else 1
            day = parts[2] if len(parts) > 2 else 1
            pub_date = datetime(year, month, day, tzinfo=timezone.utc)
        except (ValueError, TypeError):
            pass

    link = f"https://doi.org/{doi}" if doi else ""

    return Paper(
        title=title,
        abstract=abstract,
        doi=doi,
        authors=authors,
        journal=journal,
        published_date=pub_date,
        link=link,
        url=link,
    )


def collect_papers(config: dict) -> list[Paper]:
    """모든 저널에서 논문 수집 (RSS + CrossRef 보완)."""
    journals = config.get("journals", [])
    collection_days = config.get("schedule", {}).get("collection_window_days", 7)
    cutoff = datetime.now(timezone.utc) - timedelta(days=collection_days)
    all_papers = []
    seen_dois = set()

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

                if pub_date is None:
                    pub_date = datetime.now(timezone.utc)

                if pub_date < cutoff:
                    continue

                title = entry.get("title", "").strip()
                if not title:
                    continue

                doi = _extract_doi(entry)

                if doi and doi in seen_dois:
                    continue
                if doi:
                    seen_dois.add(doi)

                abstract = _extract_abstract(entry)

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
                    url=link or (f"https://doi.org/{doi}" if doi else ""),
                )
                all_papers.append(paper)
                count += 1

            logger.info(f"  {name}: {count}편 수집")

        except Exception as e:
            logger.error(f"저널 수집 실패: {name} - {e}")
            continue

    logger.info(f"RSS 수집 완료: {len(all_papers)}편")

    # RSS가 7일치를 충분히 못 주면 CrossRef API로 보완
    if len(all_papers) < 20:
        logger.info("RSS 수집 부족 → CrossRef API 보완 수집 시작")
        today = datetime.now(timezone.utc)
        from_date = (today - timedelta(days=collection_days)).strftime("%Y-%m-%d")
        until_date = today.strftime("%Y-%m-%d")

        all_keywords = []
        categories = config.get("categories", {})
        for cat_info in categories.values():
            all_keywords.extend(cat_info.get("keywords", []))

        crossref_items = fetch_crossref_papers(all_keywords, from_date, until_date)
        crossref_count = 0
        for item in crossref_items:
            doi = item.get("DOI", "")
            if doi and doi in seen_dois:
                continue

            paper = _crossref_item_to_paper(item)
            if paper:
                if doi:
                    seen_dois.add(doi)
                all_papers.append(paper)
                crossref_count += 1

        logger.info(f"CrossRef 보완: {crossref_count}편 추가")

    logger.info(f"총 {len(all_papers)}편 수집 완료")
    return all_papers
