"""Gemini API 기반 논문 분석 모듈."""

import json
import logging
import os
import time
from collections import Counter

import google.generativeai as genai

from src.collector import Paper

logger = logging.getLogger(__name__)

# PPEL 연구 분야 설명
PPEL_FIELDS = (
    "에너지 하베스팅 (triboelectric, piezoelectric, nanogenerator, self-powered), "
    "바이오센서 (biosensor, electrochemical sensor, glucose sensor, impedimetric, voltammetric), "
    "유연전자소자 (flexible electronics, wearable, strain sensor), "
    "프린팅 전자소자 (printed electronics, screen printing, inkjet printing, 3D printing), "
    "DFT 계산소재과학 (DFT, first-principles, 2D materials, MXene, perovskite)"
)

ANALYSIS_PROMPT = """다음 논문을 분석해주세요.

제목: {title}
저널: {journal}
초록: {abstract}

아래 형식의 JSON으로만 응답하세요. 다른 텍스트 없이 JSON만 출력하세요:
{{
    "summary_kr": ["첫 번째 요약 문장", "두 번째 요약 문장", "세 번째 요약 문장"],
    "novelty": "핵심 기여/novelty 한 줄 설명",
    "tags": ["연구 분야 태그1", "태그2"],
    "ppel_score": 5,
    "trend_keywords": ["키워드1", "키워드2", "키워드3"]
}}

분석 기준:
1. summary_kr: 한글로 3문장 요약 (각 문장은 명확하고 구체적으로)
2. novelty: 이 논문의 핵심 기여나 새로운 점을 한 줄로 (한글)
3. tags: 관련 연구 분야 태그 (영어, 복수 가능)
4. ppel_score: PPEL 연구실 연관성 점수 (1-10)
   PPEL 연구분야: {ppel_fields}
5. trend_keywords: 이 논문의 핵심 트렌드 키워드 3개 (영어)
"""

TREND_PROMPT = """다음은 오늘 수집된 논문들의 분석 결과입니다.

{papers_info}

위 논문들을 종합하여 오늘의 일간 트렌드 키워드 Top 5를 선정해주세요.
아래 형식의 JSON으로만 응답하세요:
{{
    "trend_keywords": [
        {{"keyword": "키워드1", "description": "설명"}},
        {{"keyword": "키워드2", "description": "설명"}},
        {{"keyword": "키워드3", "description": "설명"}},
        {{"keyword": "키워드4", "description": "설명"}},
        {{"keyword": "키워드5", "description": "설명"}}
    ]
}}
"""


class GeminiAnalyzer:
    """Gemini API 기반 논문 분석기."""

    def __init__(self, config: dict):
        api_key = os.environ.get("GEMINI_API_KEY", "")
        if not api_key:
            raise ValueError("GEMINI_API_KEY 환경변수가 설정되지 않았습니다.")

        genai.configure(api_key=api_key)
        model_name = config.get("gemini", {}).get("model", "gemini-2.0-flash")
        self.model = genai.GenerativeModel(model_name)
        self.rate_limit = config.get("gemini", {}).get("rate_limit_per_minute", 14)
        self._call_times: list[float] = []

    def _rate_limit_wait(self):
        """Rate limiting: 분당 호출 횟수 제한."""
        now = time.time()
        # 1분 이내 호출 기록만 유지
        self._call_times = [t for t in self._call_times if now - t < 60]

        if len(self._call_times) >= self.rate_limit:
            # 가장 오래된 호출 이후 60초까지 대기
            wait_time = 60 - (now - self._call_times[0]) + 1
            if wait_time > 0:
                logger.info(f"Rate limit 대기: {wait_time:.1f}초")
                time.sleep(wait_time)

        self._call_times.append(time.time())

    def _parse_json_response(self, text: str) -> dict:
        """Gemini 응답에서 JSON 파싱."""
        # 코드 블록 제거
        text = text.strip()
        if text.startswith("```"):
            lines = text.split("\n")
            # 첫 줄(```json 등)과 마지막 줄(```) 제거
            lines = [l for l in lines if not l.strip().startswith("```")]
            text = "\n".join(lines)

        try:
            return json.loads(text)
        except json.JSONDecodeError:
            # JSON 부분만 추출 시도
            import re

            match = re.search(r"\{.*\}", text, re.DOTALL)
            if match:
                try:
                    return json.loads(match.group())
                except json.JSONDecodeError:
                    pass
            logger.warning(f"JSON 파싱 실패: {text[:200]}")
            return {}

    def analyze_paper(self, paper: Paper) -> Paper:
        """단일 논문 분석."""
        if not paper.abstract and not paper.title:
            paper.summary = "분석 불가: 제목 및 초록 없음"
            return paper

        self._rate_limit_wait()

        prompt = ANALYSIS_PROMPT.format(
            title=paper.title,
            journal=paper.journal,
            abstract=paper.abstract or "(초록 없음)",
            ppel_fields=PPEL_FIELDS,
        )

        try:
            response = self.model.generate_content(prompt)
            result = self._parse_json_response(response.text)

            if result:
                summary_lines = result.get("summary_kr", [])
                if isinstance(summary_lines, list):
                    paper.summary = "\n".join(summary_lines)
                else:
                    paper.summary = str(summary_lines)

                paper.novelty = result.get("novelty", "")
                paper.tags = result.get("tags", [])
                paper.ppel_score = int(result.get("ppel_score", 0))
                paper.keywords = result.get("trend_keywords", [])
            else:
                paper.summary = "분석 불가: 응답 파싱 실패"

        except Exception as e:
            logger.error(f"논문 분석 실패: {paper.title[:50]} - {e}")
            paper.summary = f"분석 불가: {str(e)[:100]}"

        return paper

    def analyze_papers(self, papers: list[Paper]) -> list[Paper]:
        """여러 논문 분석."""
        total = len(papers)
        for i, paper in enumerate(papers):
            logger.info(f"분석 중 ({i + 1}/{total}): {paper.title[:60]}")
            self.analyze_paper(paper)
        logger.info(f"총 {total}편 분석 완료")
        return papers

    def get_daily_trends(self, papers: list[Paper]) -> list[dict]:
        """일간 트렌드 키워드 Top 5 추출."""
        if not papers:
            return []

        # 먼저 각 논문의 키워드로 기본 트렌드 계산
        all_keywords = []
        for p in papers:
            all_keywords.extend(p.keywords)

        keyword_counts = Counter(all_keywords)

        # Gemini로 종합 트렌드 분석
        papers_info = ""
        for p in papers:
            papers_info += f"- {p.title} [{p.journal}]: {', '.join(p.tags)}\n"
            if p.keywords:
                papers_info += f"  키워드: {', '.join(p.keywords)}\n"

        self._rate_limit_wait()

        try:
            prompt = TREND_PROMPT.format(papers_info=papers_info)
            response = self.model.generate_content(prompt)
            result = self._parse_json_response(response.text)
            trends = result.get("trend_keywords", [])
            if trends:
                return trends
        except Exception as e:
            logger.error(f"트렌드 분석 실패: {e}")

        # 폴백: 키워드 빈도 기반
        return [
            {"keyword": kw, "description": f"{cnt}회 등장"}
            for kw, cnt in keyword_counts.most_common(5)
        ]
