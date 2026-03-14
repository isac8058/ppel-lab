"""키워드 기반 논문 필터링 및 7개 카테고리별 분류 모듈."""

import logging
import re
from collections import defaultdict

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from src.collector import Paper

logger = logging.getLogger(__name__)


def _classify_paper(paper: Paper, categories: dict) -> tuple[str | None, int]:
    """논문을 카테고리로 분류. (카테고리키, 매칭수) 반환."""
    text = f"{paper.title} {paper.abstract}".lower()

    best_cat = None
    best_count = 0

    for cat_key, cat_info in categories.items():
        keywords = cat_info.get("keywords", [])
        count = sum(
            1 for kw in keywords
            if re.search(r'\b' + re.escape(kw.lower()) + r'\b', text)
        )
        if count > best_count:
            best_count = count
            best_cat = cat_key

    return (best_cat, best_count) if best_count > 0 else (None, 0)


def compute_relevance(papers: list[Paper], categories: dict) -> list[Paper]:
    """TF-IDF 기반 키워드 관련성 점수 계산."""
    if not papers:
        return []

    all_keywords = []
    for cat_info in categories.values():
        all_keywords.extend(cat_info.get("keywords", []))

    keyword_doc = " ".join(all_keywords)

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
    config: dict,
) -> dict[str, list[Paper]]:
    """논문 필터링 후 7개 카테고리별 분류.

    Returns:
        {"peng": [Paper, ...], "teng": [...], ...}
        각 카테고리 내에서 관련성 점수 상위 max_papers_per_category개 선별.
    """
    categories = config.get("categories", {})
    max_per_cat = config.get("analysis", {}).get("max_papers_per_category", 8)
    max_total = config.get("analysis", {}).get("max_total_papers", 50)
    threshold = config.get("analysis", {}).get("relevance_threshold", 4)

    if not papers:
        return {cat_key: [] for cat_key in categories}

    # 1. 관련성 점수 계산
    papers = compute_relevance(papers, categories)

    # 2. 각 논문을 가장 높은 점수의 카테고리에 배정
    cat_papers: dict[str, list[Paper]] = defaultdict(list)

    for p in papers:
        cat_key, match_count = _classify_paper(p, categories)
        if cat_key and (p.relevance_score >= threshold or match_count >= 2):
            p.category = cat_key
            p.relevance_label = categories[cat_key].get("name", cat_key)
            cat_papers[cat_key].append(p)

    # 3. 각 카테고리 내에서 관련성 점수 상위 max_per_cat개 선별
    result: dict[str, list[Paper]] = {}
    total_selected = 0

    for cat_key in categories:
        papers_in_cat = cat_papers.get(cat_key, [])
        papers_in_cat.sort(key=lambda p: p.relevance_score, reverse=True)
        selected = papers_in_cat[:max_per_cat]
        result[cat_key] = selected
        total_selected += len(selected)

    # 4. max_total_papers 제한
    if total_selected > max_total:
        all_selected = []
        for cat_key, cat_list in result.items():
            for p in cat_list:
                all_selected.append((cat_key, p))
        all_selected.sort(key=lambda x: x[1].relevance_score, reverse=True)

        kept = set()
        for cat_key, p in all_selected[:max_total]:
            kept.add(id(p))

        for cat_key in result:
            result[cat_key] = [p for p in result[cat_key] if id(p) in kept]

    total_final = sum(len(v) for v in result.values())
    cat_summary = {categories[k]["name"]: len(v) for k, v in result.items() if v}
    logger.info(
        f"카테고리별 분류 완료: 총 {total_final}편 선별, "
        f"분포 {cat_summary}"
    )

    return result
