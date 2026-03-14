"""Gemini API 논문 분석 모듈 - 주간 다이제스트용.

google-genai SDK 사용 (google-generativeai deprecated 대체).
"""

import json
import logging
import os
import time

from google import genai
from google.genai import types

from src.collector import Paper

logger = logging.getLogger(__name__)

ANALYSIS_PROMPT = """당신은 재료공학/전자공학 분야 논문 분석 전문가입니다.
아래 논문들을 7개 카테고리별로 분석하여 JSON으로 응답하세요.

분석 대상 연구실(PPEL Lab, 전북대학교):
- 에너지 하베스팅 (TENG, PENG)
- 바이오센서 (전기화학 센서, 압타머)
- 유연/프린팅 전자소자
- MXene 소재 응용
- DFT 계산소재과학
- 멤리스터 (ReRAM)

[논문 목록 - 카테고리별]
{papers_by_category}

각 논문에 대해:
- highlight_title: 핵심 소재/기술명 (한글, 짧게, 예: "BeO/PVDF 복합 박막")
- summary_kr: 한글 핵심 요약 1줄 (소재 → 방법 → 결과 순, 수치 포함)
- relevance: PPEL 연관성 점수 (1-10)
- sub_group: "소재" | "응용" | "트렌드" 중 하나

추가로:
- weekly_summary: PPEL 연구 시사점 총평 (한글, 4개 문단, 각 문단은 HTML <p> 태그 형식:
  <p><b>번호. 주제 — 키워드.</b> 설명</p>
  <p style="margin-top:10px;"><b>번호. 주제 — 키워드.</b> 설명</p>
  총평에서는 PPEL의 구체적 연구 프로젝트(cherry blossom TENG, 셀룰로오스/GCN TENG, MXene/Fe3O4 전극, 5-hmC 암진단 센서, p-tau217 알츠하이머 진단, CuO@PDA 멤리스터, DLP 마이크로니들 패치)와 이번 주 논문의 연관성을 직접 언급)

반드시 JSON만 출력하세요. 다른 텍스트 없이.

응답 형식:
{{
    "papers": {{
        "카테고리키": [
            {{
                "doi": "10.xxx/yyy",
                "highlight_title": "핵심 소재/기술명",
                "summary_kr": "한글 핵심 요약 1줄",
                "relevance": 7,
                "sub_group": "소재"
            }}
        ]
    }},
    "weekly_summary": "<p><b>1. ...</b> ...</p>..."
}}"""


class GeminiAnalyzer:
    """제미니 분석기 - 실패해도 리포트에 영향 없음."""

    def __init__(self, config: dict):
        api_key = os.environ.get("GEMINI_API_KEY", "")
        if not api_key:
            raise ValueError("GEMINI_API_KEY 환경변수가 설정되지 않았습니다.")

        self.model_name = config.get("gemini", {}).get("model", "gemini-2.5-flash")
        self.client = genai.Client(api_key=api_key)
        self.config = types.GenerateContentConfig(
            response_mime_type="application/json",
            temperature=0.2,
        )
        self.api_calls = 0

    def analyze_papers(
        self,
        categorized_papers: dict[str, list[Paper]],
        categories_config: dict,
    ) -> dict | None:
        """전체 카테고리별 논문을 1회 API 호출로 분석.

        Returns:
            파싱된 결과 dict 또는 None (실패시)
        """
        # 논문 목록 텍스트 구성
        papers_text = ""
        paper_lookup = {}  # doi -> Paper

        for cat_key, papers in categorized_papers.items():
            if not papers:
                continue
            cat_name = categories_config.get(cat_key, {}).get("name", cat_key)
            papers_text += f"\n=== {cat_name} ===\n"

            for p in papers:
                abstract = p.abstract or "(초록 없음)"
                if len(abstract) > 300:
                    abstract = abstract[:300] + "..."
                doi_str = p.doi or "N/A"
                url_str = p.url or p.link or ""
                papers_text += (
                    f"- [{cat_key}] {p.title}\n"
                    f"  DOI: {doi_str} | URL: {url_str}\n"
                    f"  초록: {abstract}\n\n"
                )
                if p.doi:
                    paper_lookup[p.doi] = p

        if not papers_text.strip():
            return None

        prompt = ANALYSIS_PROMPT.format(papers_by_category=papers_text)

        # 1회 시도, 429면 즉시 포기
        self.api_calls += 1
        try:
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=prompt,
                config=self.config,
            )
            logger.info("Gemini API 호출 성공 (1회)")
            result = json.loads(response.text)

            # 결과를 논문에 적용
            papers_result = result.get("papers", {})
            if isinstance(papers_result, dict):
                for cat_key, paper_list in papers_result.items():
                    for pr in paper_list:
                        doi = pr.get("doi", "")
                        if doi and doi in paper_lookup:
                            paper = paper_lookup[doi]
                            paper.highlight_title = pr.get("highlight_title", paper.title)
                            paper.summary_kr = pr.get("summary_kr", "")
                            paper.ppel_score = int(pr.get("relevance", 0))
                            paper.sub_group = pr.get("sub_group", "소재")

            return result

        except Exception as e:
            error_str = str(e)
            if "429" in error_str or "quota" in error_str.lower() or "ResourceExhausted" in error_str:
                logger.warning(f"Gemini 할당량 초과 → AI 분석 건너뛰: {error_str[:100]}")
                return None

            logger.warning(f"Gemini API 실패: {error_str[:100]} → 30초 후 재시도")
            time.sleep(30)

            self.api_calls += 1
            try:
                response = self.client.models.generate_content(
                    model=self.model_name,
                    contents=prompt,
                    config=self.config,
                )
                logger.info("Gemini API 재시도 성공")
                result = json.loads(response.text)

                papers_result = result.get("papers", {})
                if isinstance(papers_result, dict):
                    for cat_key, paper_list in papers_result.items():
                        for pr in paper_list:
                            doi = pr.get("doi", "")
                            if doi and doi in paper_lookup:
                                paper = paper_lookup[doi]
                                paper.highlight_title = pr.get("highlight_title", paper.title)
                                paper.summary_kr = pr.get("summary_kr", "")
                                paper.ppel_score = int(pr.get("relevance", 0))
                                paper.sub_group = pr.get("sub_group", "소재")

                return result

            except Exception as e2:
                logger.error(f"Gemini API 최종 실패: {str(e2)[:100]}")
                return None
