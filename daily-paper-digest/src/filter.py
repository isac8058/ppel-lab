"""키워드 기반 논문 필터링 모듈."""

import logging

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from src.collector import Paper

logger = logging.getLogger(__name__)


def compute_relevance(papers: list[Paper], keywords: list[str]) -> list[Paper]:
    """TF-IDF 기반 키워드 관련성 점수 계산."""
    if not papers:
        return []

    # 키워드를 하나의 문서로 결합
    keyword_doc = " ".join(keywords)

    # 논문 텍스트 준비 (제목 + 초록)
    paper_docs = []
    for p in papers:
        text = f"{p.title} {p.abstract}".strip()
        if not text:
            text = p.title
        paper_docs.append(text)

    # TF-IDF 벡터화
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

    # 키워드 문서와 각 논문 간 코사인 유사도
    keyword_vector = tfidf_matrix[0:1]
    paper_vectors = tfidf_matrix[1:]
    similarities = cosine_similarity(keyword_vector, paper_vectors).flatten()

    # 점수 할당 (0-10 스케일)
    max_sim = similarities.max() if similarities.max() > 0 else 1.0
    for i, paper in enumerate(papers):
        paper.relevance_score = round((similarities[i] / max_sim) * 10, 2)

    return papers


def filter_papers(
    papers: list[Paper],
    keywords: list[str],
    max_papers: int = 10,
    relevance_threshold: float = 3.0,
) -> list[Paper]:
    """키워드 기반 필터링 및 상위 논문 선별."""
    if not papers:
        logger.info("필터링할 논문이 없습니다.")
        return []

    # 관련성 점수 계산
    papers = compute_relevance(papers, keywords)

    # 관련성 점수순 정렬
    sorted_papers = sorted(papers, key=lambda p: p.relevance_score, reverse=True)

    # 임계값 이상 논문 필터링
    relevant = [p for p in sorted_papers if p.relevance_score >= relevance_threshold]

    if relevant:
        selected = relevant[:max_papers]
        logger.info(
            f"관련 논문 {len(relevant)}편 중 상위 {len(selected)}편 선별 "
            f"(임계값: {relevance_threshold})"
        )
        return selected
    else:
        # 관련 논문 없으면 전체 저널 하이라이트 5개
        highlights = sorted_papers[:5]
        logger.info(
            f"관련 논문 없음. 전체 저널 하이라이트 {len(highlights)}편 선별"
        )
        return highlights
