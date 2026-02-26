"""Gemini API 논문 분석 모듈 - 선택적 AI 강화."""

import json
import logging
import os
import time

import google.generativeai as genai

from src.collector import Paper

logger = logging.getLogger(__name__)

PPEL_FIELDS_DESC = (
    "에너지 하베스팅, 바이오센서, 유연/프린팅 전자소자, DFT 계산소재과학"
)

# 분야별 대표 논문(최대 5편) + 전체 논문 목록을 분석하는 프롬프트
ANALYSIS_PROMPT = """PPEL 연구실({ppel_fields}) 관점에서 아래 논문들을 분석하세요.

=== 분야별 대표 논문 (개별 요약 생성 필요) ===
{papers_list}

=== 분야별 전체 논문 목록 (동향 분석 참고용) ===
{field_papers_summary}

JSON으로만 응답하세요:
{{
    "papers": [
        {{
            "index": 0,
            "summary_kr": "한글 2줄 핵심 요약",
            "novelty": "핵심 기여 1줄 (한글)",
            "ppel_score": 7
        }}
    ],
    "overview": "오늘의 전체 연구 동향 2-3문장 요약 (한글)",
    "field_analysis": {{
        "분야명": "이 분야 오늘 논문들 동향 3-4문장: 주요 재료·방법, 핵심 트렌드, 응용 방향, PPEL 랩 시사점 포함 (한글)"
    }}
}}"""


class GeminiAnalyzer:
    """Gemini 분석기 - 실패해도 리포트에 영향 없음."""

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

    def analyze_featured(
        self, featured: dict[str, Paper], others: list | None = None
    ) -> dict | None:
        """분야별 대표 논문(최대 5편)을 1회 API 호출로 분석.

        Args:
            featured: 분야별 대표 논문 dict
            others: 기타 관련 논문 리스트 (동향 분석 컨텍스트용)

        Returns:
            파싱된 결과 dict 또는 None (실패시)
        """
        if not featured:
            return None

        papers_list = ""
        paper_index = {}
        for i, (field, paper) in enumerate(featured.items()):
            abstract = paper.abstract or "(초록 없음)"
            if len(abstract) > 250:
                abstract = abstract[:250] + "..."
            papers_list += (
                f"{i}. [{field}] {paper.title}\n"
                f"   초록: {abstract}\n\n"
            )
            paper_index[i] = (field, paper)

        # 분야별 전체 논문 목록 구성 (동향 분석 컨텍스트)
        field_papers: dict[str, list[str]] = {}
        for field, paper in featured.items():
            field_papers[field] = [paper.title]
        if others:
            for p in others:
                label = getattr(p, "relevance_label", "") or ""
                if label:
                    if label not in field_papers:
                        field_papers[label] = []
                    field_papers[label].append(p.title)

        field_papers_summary = ""
        for field, titles in field_papers.items():
            field_papers_summary += f"{field} ({len(titles)}편):\n"
            for title in titles[:8]:
                field_papers_summary += f"  - {title}\n"
            field_papers_summary += "\n"

        prompt = ANALYSIS_PROMPT.format(
            ppel_fields=PPEL_FIELDS_DESC,
            papers_list=papers_list,
            field_papers_summary=field_papers_summary,
        )

        # 1회 시도, 429면 즉시 포기
        self.api_calls += 1
        try:
            response = self.model.generate_content(
                prompt,
                request_options={"timeout": 60},
            )
            logger.info(f"Gemini API 호출 성공 (1회)")
            result = json.loads(response.text)

            # 결과를 논문에 적용
            for pr in result.get("papers", []):
                idx = pr.get("index", -1)
                if idx in paper_index:
                    _, paper = paper_index[idx]
                    paper.summary = pr.get("summary_kr", "")
                    paper.novelty = pr.get("novelty", "")
                    paper.ppel_score = int(pr.get("ppel_score", 0))

            return result

        except Exception as e:
            error_str = str(e)
            # 429/quota → 즉시 포기 (재시도 무의미)
            if "429" in error_str or "quota" in error_str.lower() or "ResourceExhausted" in error_str:
                logger.warning(f"Gemini 할당량 초과 → AI 분석 건너뜀: {error_str[:100]}")
                return None

            # 기타 에러 → 30초 후 1회 재시도
            logger.warning(f"Gemini API 실패: {error_str[:100]} → 30초 후 재시도")
            time.sleep(30)

            self.api_calls += 1
            try:
                response = self.model.generate_content(
                    prompt,
                    request_options={"timeout": 60},
                )
                logger.info("Gemini API 재시도 성공")
                result = json.loads(response.text)

                for pr in result.get("papers", []):
                    idx = pr.get("index", -1)
                    if idx in paper_index:
                        _, paper = paper_index[idx]
                        paper.summary = pr.get("summary_kr", "")
                        paper.novelty = pr.get("novelty", "")
                        paper.ppel_score = int(pr.get("ppel_score", 0))

                return result

            except Exception as e2:
                logger.error(f"Gemini API 최종 실패: {str(e2)[:100]}")
                return None
