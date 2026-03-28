"""Gemini API로 이메일 중요도를 분석합니다."""

import json
import logging
import os

import google.generativeai as genai

from src.gmail_reader import EmailMessage

logger = logging.getLogger(__name__)

ANALYSIS_PROMPT = """당신은 PPEL 연구실 (에너지 하베스팅, 바이오센서, 유연/프린팅 전자소자, DFT 계산소재과학) 소속 교수의 이메일 비서입니다.
아래 이메일들의 중요도를 분석하여 교수님이 꼭 확인해야 할 것들만 골라주세요.

**중요도 판단 기준:**
- 🔴 HIGH (8-10): 직접 답장/행동이 필요한 메일 (동료/학생 요청, 논문 리뷰 요청, 학회 초대, 인용 알림, 보안 경고, 프로젝트 관련)
- 🟡 MEDIUM (5-7): 참고할 가치 있음 (기술 뉴스레터, 연구 관련 업데이트, 서비스 변경 공지)
- ⚪ LOW (1-4): 무시 가능 (일반 공지, 루틴 알림)

**분석할 이메일 목록:**
{emails_text}

JSON으로만 응답하세요:
{{
  "emails": [
    {{
      "index": 0,
      "importance": 8,
      "category": "연구/인용",
      "summary_kr": "핵심 내용 1-2문장 한글 요약",
      "action_needed": "필요한 행동 (없으면 빈 문자열)"
    }}
  ],
  "daily_summary": "오늘 이메일 전체 요약 2-3문장 (한글)"
}}"""


class EmailAnalyzer:
    """Gemini 기반 이메일 중요도 분석기."""

    def __init__(self):
        api_key = os.environ.get("GEMINI_API_KEY", "")
        if not api_key:
            raise ValueError("GEMINI_API_KEY 환경변수가 설정되지 않았습니다.")

        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel(
            "gemini-2.0-flash",
            generation_config={
                "response_mime_type": "application/json",
                "temperature": 0.2,
            },
        )

    def analyze(
        self, emails: list[EmailMessage], min_score: int = 5,
    ) -> dict | None:
        """이메일 목록을 분석하여 중요한 것들을 반환합니다.

        Args:
            emails: 분석할 이메일 목록
            min_score: 최소 중요도 점수 (이 이상만 결과에 포함)

        Returns:
            분석 결과 dict 또는 None
        """
        if not emails:
            logger.info("분석할 이메일이 없습니다.")
            return None

        # 이메일 텍스트 준비 (최대 20개)
        emails_to_analyze = emails[:20]
        emails_text = ""
        for i, em in enumerate(emails_to_analyze):
            emails_text += f"--- Email {i} ---\n{em.to_analysis_text()}\n"

        prompt = ANALYSIS_PROMPT.format(emails_text=emails_text)

        try:
            response = self.model.generate_content(
                prompt,
                request_options={"timeout": 60},
            )
            result = json.loads(response.text)
            logger.info(f"Gemini 이메일 분석 완료: {len(result.get('emails', []))}개 결과")

            # 중요도 점수에 따라 필터링
            if "emails" in result:
                result["emails"] = [
                    e for e in result["emails"]
                    if e.get("importance", 0) >= min_score
                ]
                # 중요도 내림차순 정렬
                result["emails"].sort(
                    key=lambda x: x.get("importance", 0), reverse=True
                )

            # 원본 이메일 정보 매칭
            for item in result.get("emails", []):
                idx = item.get("index", -1)
                if 0 <= idx < len(emails_to_analyze):
                    em = emails_to_analyze[idx]
                    item["subject"] = em.subject
                    item["sender"] = f"{em.sender_name} <{em.sender}>"
                    item["date"] = em.date.strftime("%Y-%m-%d %H:%M")

            return result

        except Exception as e:
            error_str = str(e)
            if "429" in error_str or "quota" in error_str.lower():
                logger.warning(f"Gemini 할당량 초과 → 이메일 분석 건너뜀: {error_str[:100]}")
            else:
                logger.error(f"Gemini 이메일 분석 실패: {error_str[:100]}")
            return None
