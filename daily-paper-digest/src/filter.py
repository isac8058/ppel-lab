"""키워드 기반 논문 필터링 및 PPEL 분야별 분류 모듈."""

import logging
import re
from collections import defaultdict

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from src.collector import Paper

logger = logging.getLogger(__name__)

# PPEL 연구 분야 정의
PPEL_FIELDS = {
    "에너지 하베스팅": [
        "energy harvesting", "triboelectric", "piezoelectric",
        "nanogenerator", "self-powered", "thermoelectric",
        "solar cell", "photovoltaic",
    ],
    "바이오센서": [
        "biosensor", "electrochemical sensor", "glucose sensor",
        "impedimetric", "voltammetric", "immunosensor",
        "aptasensor", "bioelectronics",
    ],
    "유연/웨어러블 전자소자": [
        "flexible electronics", "wearable", "strain sensor",
        "stretchable", "e-skin", "soft electronics",
        "flexible sensor", "textile electronics",
    ],
    "프린팅 전자소자": [
        "printed electronics", "screen printing", "inkjet printing",
        "3d printing", "additive manufacturing", "roll-to-roll",
        "gravure printing", "aerosol jet",
    ],
    "DFT/계산소재과학": [
        "dft", "first-principles", "first principles",
        "2d materials", "mxene", "perovskite",
        "density functional", "ab initio", "molecular dynamics",
    ],
}


def _classify_paper(paper: Paper) -> str | None:
    """논문을 PPEL 분야로 분류. 매칭되지 않으면 None."""
    text = f"{paper.title} {paper.abstract}".lower()

    best_field = None
    best_count = 0

    for field, keywords in PPEL_FIELDS.items():
        count = sum(
            1 for kw in keywords
            if re.search(r'\b' + re.escape(kw) + r'\b', text)
        )
        if count > best_count:
            best_count = count
            best_field = field

    return best_field if best_count > 0 else None


def compute_relevance(papers: list[Paper], keywords: list[str]) -> list[Paper]:
    """TF-IDF 기반 키워드 관련성 점수 계산."""
    if not papers:
        return []

    keyword_doc = " ".join(keywords)

    paper_docs = []
    for p in papers:
        text = f"{p.title} {p.abstract}".strip()
        if not text:
            text = p.title
        paper_docs.append(text)

    all_docs = [keyword_doc] + paper_docs
    vectorizer = TfidfVectorizer(
        stop_words="english",
        max_features=5000,
        ngram_range=(1, 2),
    )

    try:
        tfidf_matrix = vectorizer.fit_transform(all_docs)
    except ValueError:
        logger.warning("TF-IDF 벡터화 실패: 유효한 텍스트 부족")
        return papers

    keyword_vector = tfidf_matrix[0:1]
    paper_vectors = tfidf_matrix[1:]
    similarities = cosine_similarity(keyword_vector, paper_vectors).flatten()

    max_sim = similarities.max() if similarities.max() > 0 else 1.0
    for i, paper in enumerate(papers):
        paper.relevance_score = round((similarities[i] / max_sim) * 10, 2)

    return papers


def filter_and_classify(
    papers: list[Paper],
    keywords: list[str],
    relevance_threshold: float = 3.0,
) -> dict:
    """논문 필터링 후 분야별 분류.

    Returns:
        {
            "featured": {분야명: Paper, ...},        # 분야별 대표 1편
            "others": [Paper, ...],                  # 나머지 관련 논문 (전체)
            "field_others": {분야명: [Paper], ...},  # 분야별 나머지 관련 논문
            "unclassified": [Paper, ...],            # 미분류 관련 논문
            "field_counts": {분야명: int, ...},      # 분야별 전체 논문 수
            "unrelated_count": int,                  # PPEL 무관 논문 수
        }
    """
    if not papers:
        return {
            "featured": {}, "others": [], "field_others": {},
            "unclassified": [], "field_counts": {}, "unrelated_count": 0,
        }

    # 1. 관련성 점수 계산
    papers = compute_relevance(papers, keywords)

    # 2. 관련성 있는 논문만 선별
    sorted_papers = sorted(papers, key=lambda p: p.relevance_score, reverse=True)
    relevant = [p for p in sorted_papers if p.relevance_score >= relevance_threshold]

    if not relevant:
        relevant = sorted_papers[:5]
        logger.info(f"관련 논문 없음. 상위 {len(relevant)}편 사용")

    # 3. 분야별 분류
    field_papers: dict[str, list[Paper]] = defaultdict(list)
    unclassified: list[Paper] = []

    for p in relevant:
        field = _classify_paper(p)
        if field:
            p.relevance_label = field
            field_papers[field].append(p)
        else:
            p.relevance_label = ""
            unclassified.append(p)

    # 4. 분야별 대표 1편 선정 (관련성 점수 최고)
    featured: dict[str, Paper] = {}
    field_others_map: dict[str, list[Paper]] = {}
    others: list[Paper] = []

    for field, field_list in field_papers.items():
        # 점수순 정렬
        field_list.sort(key=lambda p: p.relevance_score, reverse=True)
        featured[field] = field_list[0]
        field_others_map[field] = field_list[1:]
        others.extend(field_list[1:])

    # 미분류 논문은 전부 others로
    others.extend(unclassified)
    others.sort(key=lambda p: p.relevance_score, reverse=True)

    # 5. 분야별 전체 논문 수 (전체 papers 기준)
    field_counts: dict[str, int] = defaultdict(int)
    unrelated_count = 0
    for p in papers:
        field = _classify_paper(p)
        if field:
            field_counts[field] += 1
        else:
            unrelated_count += 1

    logger.info(
        f"분야별 분류 완료: 대표 {len(featured)}편, "
        f"기타 관련 {len(others)}편, "
        f"전체 분야 분포 {dict(field_counts)}"
    )

    return {
        "featured": featured,
        "others": others,
        "field_others": field_others_map,
        "unclassified": unclassified,
        "field_counts": dict(field_counts),
        "unrelated_count": unrelated_count,
    }
