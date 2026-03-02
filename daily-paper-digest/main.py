"""Daily Paper Digest - 전체 파이프라인 실행."""

import logging
import os
import sys

from dotenv import load_dotenv

from src.analyzer import GeminiAnalyzer
from src.collector import collect_papers, load_config
from src.database import PaperDatabase
from src.filter import filter_and_classify
from src.mailer import send_email
from src.reporter import generate_report, get_email_subject

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)


def main():
    """메인 파이프라인 실행."""
    load_dotenv()

    logger.info("=" * 60)
    logger.info("Daily Paper Digest 시작")
    logger.info("=" * 60)

    # 1. 설정 로드
    config_path = os.environ.get("CONFIG_PATH", "config.yaml")
    try:
        config = load_config(config_path)
    except FileNotFoundError:
        logger.error(f"설정 파일을 찾을 수 없습니다: {config_path}")
        sys.exit(1)

    # 2. 데이터베이스 초기화
    db = PaperDatabase()

    # 3. 논문 수집
    logger.info("--- 1단계: 논문 수집 ---")
    all_papers = collect_papers(config)
    total_collected = len(all_papers)

    if total_collected == 0:
        logger.warning("수집된 논문이 없습니다.")
        html = generate_report({}, [], {}, 0)
        subject = get_email_subject(0)
        recipient = config.get("email", {}).get("recipient", "smlim@jbnu.ac.kr")
        send_email(subject, html, recipient)
        return

    # 4. 중복 제거
    logger.info("--- 2단계: 중복 제거 ---")
    new_papers = db.filter_new_papers(all_papers)
    logger.info(f"신규 논문: {len(new_papers)}편 (전체 {total_collected}편)")

    if not new_papers:
        logger.info("모든 논문이 이미 처리되었습니다.")
        html = generate_report({}, [], {}, total_collected)
        subject = get_email_subject(0)
        recipient = config.get("email", {}).get("recipient", "smlim@jbnu.ac.kr")
        send_email(subject, html, recipient)
        return

    # 5. 키워드 필터링 + 분야별 분류
    logger.info("--- 3단계: 키워드 필터링 & 분야별 분류 ---")
    keywords = config.get("keywords", [])
    threshold = config.get("analysis", {}).get("relevance_threshold", 3)
    classification = filter_and_classify(new_papers, keywords, threshold)

    featured = classification["featured"]       # {분야: Paper}
    others = classification["others"]           # [Paper, ...]
    field_counts = classification["field_counts"]
    field_others = classification["field_others"]   # {분야: [Paper, ...]}
    unclassified = classification["unclassified"]   # [Paper, ...]

    logger.info(f"분야별 대표: {len(featured)}편, 기타: {len(others)}편")

    # 6. Gemini 분석 (선택적 - 실패해도 OK)
    logger.info("--- 4단계: Gemini 분석 (대표 논문만, 최대 1회 API) ---")
    ai_result = None
    ai_success = False

    try:
        analyzer = GeminiAnalyzer(config)
        ai_result = analyzer.analyze_featured(featured, field_counts)
        ai_success = ai_result is not None
        logger.info(
            f"Gemini: {'성공' if ai_success else '실패 (fallback)'} | "
            f"API 호출: {analyzer.api_calls}회"
        )
    except ValueError as e:
        logger.warning(f"Gemini 초기화 실패 (GEMINI_API_KEY 미설정?): {e}")
    except Exception as e:
        logger.warning(f"Gemini 오류: {e}")

    # 7. 데이터베이스 저장
    logger.info("--- 5단계: 데이터베이스 저장 ---")
    all_analyzed = list(featured.values()) + others
    db.save_papers(all_analyzed)

    # 8. 리포트 생성
    logger.info("--- 6단계: 리포트 생성 ---")
    html = generate_report(
        featured=featured,
        others=others,
        field_counts=field_counts,
        total_collected=total_collected,
        ai_result=ai_result,
        field_others=field_others,
        unclassified=unclassified,
    )
    subject = get_email_subject(len(featured))

    # 9. 이메일 발송
    logger.info("--- 7단계: 이메일 발송 ---")
    recipient = config.get("email", {}).get("recipient", "smlim@jbnu.ac.kr")
    success = send_email(subject, html, recipient)

    if success:
        logger.info("=" * 60)
        logger.info("Daily Paper Digest 완료!")
        logger.info(
            f"수집: {total_collected}편 | 대표: {len(featured)}편 | "
            f"기타: {len(others)}편 | AI: {'Y' if ai_success else 'N'} | "
            f"발송: {recipient}"
        )
        logger.info("=" * 60)
    else:
        logger.error("이메일 발송 실패")
        sys.exit(1)


if __name__ == "__main__":
    main()
