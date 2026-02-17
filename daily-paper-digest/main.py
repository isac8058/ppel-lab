"""Daily Paper Digest - 전체 파이프라인 실행."""

import logging
import os
import sys

from dotenv import load_dotenv

from src.analyzer import GeminiAnalyzer
from src.collector import collect_papers, load_config
from src.database import PaperDatabase
from src.filter import filter_papers
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
    # .env 파일 로드
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
        # 빈 리포트 발송
        html = generate_report([], 0, [])
        subject = get_email_subject([])
        recipient = config.get("email", {}).get("recipient", "smlim@jbnu.ac.kr")
        send_email(subject, html, recipient)
        logger.info("빈 리포트 발송 완료")
        return

    # 4. 중복 제거
    logger.info("--- 2단계: 중복 제거 ---")
    new_papers = db.filter_new_papers(all_papers)
    logger.info(f"신규 논문: {len(new_papers)}편 (전체 {total_collected}편)")

    if not new_papers:
        logger.info("모든 논문이 이미 처리되었습니다.")
        html = generate_report([], total_collected, [])
        subject = get_email_subject([])
        recipient = config.get("email", {}).get("recipient", "smlim@jbnu.ac.kr")
        send_email(subject, html, recipient)
        return

    # 5. 키워드 필터링
    logger.info("--- 3단계: 키워드 필터링 ---")
    keywords = config.get("keywords", [])
    max_papers = config.get("analysis", {}).get("max_papers", 20)
    threshold = config.get("analysis", {}).get("relevance_threshold", 3)
    filtered = filter_papers(new_papers, keywords, max_papers, threshold)

    # 6. Gemini 분석
    logger.info("--- 4단계: Gemini 분석 ---")
    analyzer = None
    briefing = {}
    try:
        analyzer = GeminiAnalyzer(config)
        analyzed = analyzer.analyze_papers(filtered)
        trends = analyzer.get_daily_trends(analyzed)
    except ValueError as e:
        logger.error(f"Gemini 초기화 실패: {e}")
        analyzed = filtered
        trends = []
    except Exception as e:
        logger.error(f"분석 중 오류: {e}")
        analyzed = filtered
        trends = []

    # 6-1. 종합 브리핑 생성
    logger.info("--- 4-1단계: 종합 브리핑 생성 ---")
    if analyzer is not None:
        try:
            briefing = analyzer.generate_briefing(analyzed, total_collected)
        except Exception as e:
            logger.error(f"브리핑 생성 오류: {e}")
    else:
        logger.warning("Gemini 미초기화 - 브리핑 생략")

    # 7. 데이터베이스 저장
    logger.info("--- 5단계: 데이터베이스 저장 ---")
    db.save_papers(analyzed)
    if trends:
        db.save_daily_trends(trends)

    # 8. 주간 트렌드 조회
    weekly_trends = db.get_weekly_trends()

    # 9. 리포트 생성
    logger.info("--- 6단계: 리포트 생성 ---")
    html = generate_report(analyzed, total_collected, trends, weekly_trends, briefing)
    subject = get_email_subject(analyzed)

    # 10. 이메일 발송
    logger.info("--- 7단계: 이메일 발송 ---")
    recipient = config.get("email", {}).get("recipient", "smlim@jbnu.ac.kr")
    success = send_email(subject, html, recipient)

    if success:
        logger.info("=" * 60)
        logger.info("Daily Paper Digest 완료!")
        logger.info(f"수집: {total_collected}편 | 분석: {len(analyzed)}편 | 발송: {recipient}")
        logger.info("=" * 60)
    else:
        logger.error("이메일 발송 실패")
        sys.exit(1)


if __name__ == "__main__":
    main()
