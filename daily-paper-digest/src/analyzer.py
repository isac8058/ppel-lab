"""Gemini API 기반 논문 분석 모듈 - 1회 API 호출로 전체 분석."""

import json
import logging
import os
import time
from collections import defaultdict

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

UNIFIED_PROMPT = """당신은 재료공학/전자공학 분야 논문 분석 전문가입니다.
아래 논문들을 분석하여 JSON 형식으로 응답하세요.

분석 대상 연구실(PPEL): {ppel_fields}

[논문 목록]
{papers_list}

각 논문에 대해:
- summary_kr: 한글 2줄 핵심 요약 (리스트)
- novelty: 핵심 기여 1줄 (한글)
- relevance: PPEL 연관성 점수 (1-10)
- tags: 분야 태그 리스트 (영어)

추가로:
- top5: PPEL 연관성 상위 5편 번호 리스트 (0-based index)
- trend_keywords: 오늘의 트렌드 키워드 3개 리스트 (영어)
- overview: 오늘 수집된 논문들의 전체 동향 2-3문장 요약 (한글, 교수님께 보고하는 톤)
- themes: 연관 논문끼리 묶은 3-5개 테마
- ppel_action_items: PPEL 연구실 시사점 2-4개 (한글)

반드시 아래 JSON 형식으로만 출력하세요:
{{
    "papers": [
        {{
            "index": 0,
            "summary_kr": ["첫 번째 요약", "두 번째 요약"],
            "novelty": "핵심 기여",
            "relevance": 7,
            "tags": ["tag1", "tag2"]
        }}
    ],
    "top5": [0, 3, 1, 4, 2],
    "trend_keywords": ["keyword1", "keyword2", "keyword3"],
    "overview": "전체 동향 요약 2-3문장",
    "themes": [
        {{
            "title": "테마명",
            "summary": "이 테마의 연구 동향 3-4문장 설명",
            "ppel_relevance": "PPEL 연구실과의 접점 1-2문장",
            "relevance_level": "high",
            "paper_indices": [0, 2]
        }}
    ],
    "ppel_action_items": ["시사점1", "시사점2"]
}}"""


class GeminiAnalyzer:
    """Gemini API 기반 논문 분석기 - 1회 호출로 전체 분석."""

    def __init__(self, config: dict):
        api_key = os.environ.get("GEMINI_API_KEY", "")
        if not api_key:
            raise ValueError("GEMINI_API_KEY 환경변수가 설정되지 않았습니다.")

        genai.configure(api_key=api_key)
        model_name = config.get("gemini", {}).get("model", "gemini-2.0-flash")
        self.model = genai.GenerativeModel(
            model_name,
            generation_config={
                "response_mime_type": "application/json",
                "temperature": 0.2,
            },
        )
        self.api_calls = 0
        self._errors: list[str] = []

    def analyze_all(
        self, papers: list[Paper], total_collected: int
    ) -> dict:
        """전체 논문을 1회 API 호출로 일괄 분석.

        Returns:
            {"papers", "briefing", "trends", "success"}
        """
        if not papers:
            return {"papers": papers, "briefing": {}, "trends": [], "success": False}

        # 프롬프트 생성
        papers_list = ""
        for i, p in enumerate(papers):
            abstract = p.abstract or "(초록 없음)"
            if len(abstract) > 300:
                abstract = abstract[:300] + "..."
            papers_list += (
                f"{i}. 제목: {p.title}\n"
                f"   저널: {p.journal}\n"
                f"   초록: {abstract}\n\n"
            )

        prompt = UNIFIED_PROMPT.format(
            ppel_fields=PPEL_FIELDS,
            papers_list=papers_list,
        )

        # API 호출 (1회 + 실패시 30초 대기 후 1회 재시도)
        response_text = self._call_gemini(prompt)

        if response_text is None:
            logger.error("Gemini API 분석 실패 → fallback 모드 사용")
            return {
                "papers": papers,
                "briefing": self._fallback_briefing(papers, total_collected),
                "trends": [],
                "success": False,
            }

        # JSON 파싱
        try:
            parsed = json.loads(response_text)
        except json.JSONDecodeError:
            logger.error(f"JSON 파싱 실패: {response_text[:200]}")
            return {
                "papers": papers,
                "briefing": self._fallback_briefing(papers, total_collected),
                "trends": [],
                "success": False,
            }

        # 논문별 결과 적용
        paper_results = parsed.get("papers", [])
        result_map = {pr.get("index", i): pr for i, pr in enumerate(paper_results)}

        success_count = 0
        for i, p in enumerate(papers):
            pr = result_map.get(i)
            if pr and "summary_kr" in pr:
                summary_lines = pr.get("summary_kr", [])
                p.summary = "\n".join(summary_lines) if isinstance(summary_lines, list) else str(summary_lines)
                p.novelty = pr.get("novelty", "")
                p.ppel_score = int(pr.get("relevance", 0))
                p.tags = pr.get("tags", [])
                p.keywords = pr.get("tags", [])[:3]
                success_count += 1

        logger.info(
            f"Gemini 분석 완료: {success_count}/{len(papers)}편 성공 "
            f"(API 호출: {self.api_calls}회)"
        )

        # 브리핑 구성
        briefing = {
            "overview": parsed.get("overview", ""),
            "themes": parsed.get("themes", []),
            "ppel_action_items": parsed.get("ppel_action_items", []),
            "hot_keywords": parsed.get("trend_keywords", []),
        }

        # 트렌드
        trends = [
            {"keyword": kw, "description": "오늘의 트렌드"}
            for kw in parsed.get("trend_keywords", [])
        ]

        return {
            "papers": papers,
            "briefing": briefing,
            "trends": trends,
            "success": True,
        }

    def _call_gemini(self, prompt: str) -> str | None:
        """Gemini API 호출 (1회 + 실패시 30초 대기 후 재시도 1회)."""
        for attempt in range(2):
            self.api_calls += 1
            try:
                response = self.model.generate_content(
                    prompt,
                    request_options={"timeout": 60},
                )
                logger.info(f"Gemini API 호출 성공 (시도 {attempt + 1}/2)")
                return response.text
            except Exception as e:
                error_str = str(e)
                self._errors.append(error_str[:150])

                # 429 할당량 초과는 재시도해도 해결 안 됨
                if "429" in error_str or "quota" in error_str.lower() or "ResourceExhausted" in error_str:
                    logger.error(f"Gemini API 할당량 초과: {error_str[:150]}")
                    return None

                if attempt == 0:
                    logger.warning(
                        f"Gemini API 실패 (시도 1/2): {error_str[:100]} "
                        "→ 30초 후 재시도"
                    )
                    time.sleep(30)
                else:
                    logger.error(f"Gemini API 최종 실패: {error_str[:150]}")

        return None

    def _fallback_briefing(
        self, papers: list[Paper], total_collected: int
    ) -> dict:
        """Gemini 실패 시 키워드 매칭 기반 브리핑 생성."""
        # 저널별 그룹핑
        journal_groups: dict[str, list[int]] = defaultdict(list)
        for i, p in enumerate(papers):
            journal_groups[p.journal].append(i)

        themes = []
        for journal, indices in sorted(
            journal_groups.items(), key=lambda x: -len(x[1])
        )[:5]:
            titles = [papers[i].title[:50] for i in indices[:3]]
            themes.append({
                "title": f"{journal} ({len(indices)}편)",
                "summary": "; ".join(titles),
                "ppel_relevance": "개별 논문을 확인해주세요.",
                "relevance_level": "medium",
                "paper_indices": indices,
            })

        # 키워드 매칭 점수 기준 상위 논문
        top_papers = sorted(
            papers, key=lambda p: p.relevance_score, reverse=True
        )[:3]
        action_items = [
            f"[관련도 {self._relevance_label(p.relevance_score)}] {p.title[:65]}"
            for p in top_papers
        ]

        # 에러 정보
        error_note = ""
        if self._errors:
            error_note = f" (오류: {self._errors[0][:80]})"

        return {
            "overview": (
                f"오늘 총 {total_collected}편 중 {len(papers)}편이 선별되었습니다. "
                f"AI 분석이 일시적으로 불가하여 키워드 매칭 기반 관련성을 제공합니다."
                f"{error_note}"
            ),
            "themes": themes,
            "ppel_action_items": action_items,
            "hot_keywords": [],
        }

    @staticmethod
    def _relevance_label(score: float) -> str:
        """키워드 매칭 점수를 High/Medium/Low 라벨로 변환."""
        if score >= 7:
            return "High"
        elif score >= 4:
            return "Medium"
        return "Low"
