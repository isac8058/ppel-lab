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

BRIEFING_PROMPT = """당신은 PPEL(Printed & Flexible Electronics Lab) 연구실의 연구 동향 브리핑 담당자입니다.
교수님께 매일 아침 보고하는 간결하면서도 통찰력 있는 연구 브리핑을 작성해주세요.

PPEL 연구실 핵심 연구 분야:
{ppel_fields}

오늘 주요 학술지에서 수집된 논문 {paper_count}편 중 관련성 높은 {analyzed_count}편입니다:

{papers_list}

위 논문들을 종합 분석하여 아래 JSON 형식으로 일일 연구 브리핑을 작성하세요.
다른 텍스트 없이 JSON만 출력하세요:
{{
    "overview": "오늘 수집된 논문들의 전체 동향을 2-3문장으로 요약. 어떤 분야에서 어떤 흐름이 보이는지 거시적으로.",
    "themes": [
        {{
            "title": "주요 연구 테마명 (예: 차세대 에너지 하베스팅 소재)",
            "summary": "이 테마에 해당하는 연구들의 동향을 3-4문장으로 설명. 무엇이 연구되고 있고, 어떤 방향으로 가고 있는지.",
            "ppel_relevance": "PPEL 연구실의 구체적 연구(에너지 하베스팅, 바이오센서, 유연소자, 프린팅, DFT 등)와 어떤 접점이 있는지 1-2문장으로.",
            "relevance_level": "high 또는 medium 또는 low",
            "paper_indices": [0, 2]
        }}
    ],
    "ppel_action_items": [
        "PPEL 연구실에서 주목하거나 참고할 만한 구체적 시사점 (2-4개)"
    ],
    "hot_keywords": ["오늘의 핵심 키워드 5개 (영어)"]
}}

작성 가이드:
- themes는 3~5개, 연관 논문끼리 테마별로 묶어주세요
- paper_indices는 위 논문 목록의 번호(0부터)를 사용하세요
- relevance_level이 high인 테마를 먼저 배치하세요
- 한글로, 교수님께 보고하는 자연스럽고 간결한 문체로 작성
- 단순 나열이 아닌, 왜 중요한지/어떤 의미인지 분석적 시각을 담아주세요
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

    def generate_briefing(
        self, papers: list[Paper], total_collected: int
    ) -> dict:
        """전체 논문을 종합 분석하여 브리핑 리포트 생성."""
        if not papers:
            return {}

        # 논문 목록 텍스트 생성
        papers_list = ""
        for i, p in enumerate(papers):
            abstract_short = (p.abstract[:200] + "...") if len(p.abstract) > 200 else p.abstract
            papers_list += (
                f"[{i}] 제목: {p.title}\n"
                f"    저널: {p.journal}\n"
                f"    초록: {abstract_short}\n"
                f"    태그: {', '.join(p.tags)}\n"
                f"    PPEL 점수: {p.ppel_score}/10\n\n"
            )

        self._rate_limit_wait()

        prompt = BRIEFING_PROMPT.format(
            ppel_fields=PPEL_FIELDS,
            paper_count=total_collected,
            analyzed_count=len(papers),
            papers_list=papers_list,
        )

        try:
            response = self.model.generate_content(prompt)
            result = self._parse_json_response(response.text)
            if result and "overview" in result:
                logger.info("종합 브리핑 생성 완료")
                return result
            else:
                logger.warning("브리핑 JSON 파싱 실패, 폴백 사용")
        except Exception as e:
            logger.error(f"브리핑 생성 실패: {e}")

        # 폴백: 기본 브리핑
        return self._fallback_briefing(papers)

    def _fallback_briefing(self, papers: list[Paper]) -> dict:
        """Gemini 실패 시 기본 브리핑 생성."""
        # 태그별 논문 그룹핑
        from collections import defaultdict
        tag_groups: dict[str, list[int]] = defaultdict(list)
        for i, p in enumerate(papers):
            for tag in p.tags:
                tag_groups[tag].append(i)

        themes = []
        for tag, indices in sorted(tag_groups.items(), key=lambda x: -len(x[1]))[:5]:
            themes.append({
                "title": tag,
                "summary": f"이 분야에서 {len(indices)}편의 논문이 발표되었습니다.",
                "ppel_relevance": "개별 논문을 확인해주세요.",
                "relevance_level": "medium",
                "paper_indices": indices,
            })

        top_ppel = sorted(papers, key=lambda p: p.ppel_score, reverse=True)[:3]
        action_items = [
            f"[PPEL {p.ppel_score}/10] {p.title[:60]}" for p in top_ppel
        ]

        all_keywords = []
        for p in papers:
            all_keywords.extend(p.keywords)
        keyword_counts = Counter(all_keywords)

        return {
            "overview": f"오늘 총 {len(papers)}편의 논문이 분석되었습니다. AI 분석이 일시적으로 불가하여 기본 요약을 제공합니다.",
            "themes": themes,
            "ppel_action_items": action_items,
            "hot_keywords": [kw for kw, _ in keyword_counts.most_common(5)],
        }
