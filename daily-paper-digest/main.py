"""PPEL Weekly Paper Digest - 주간 파이프라인 실행."""

import argparse
import logging
import os
import sys
from datetime import datetime, timedelta, timezone

from dotenv import load_dotenv

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
    parser = argparse.ArgumentParser(description="PPEL Weekly Paper Digest")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="이메일 발송 생략, HTML을 output.html로 저장",
    )
    args = parser.parse_args()

    load_dotenv()

    today = datetime.now(timezone.utc)
    collection_days = 7
    start_date = (today - timedelta(days=collection_days)).strftime("%Y-%m-%d")
    end_date = today.strftime("%Y-%m-%d")
    date_range = f"{start_date}~{end_date}"

    logger.info("=" * 60)
    logger.info(f"[PPEL Weekly Digest] {date_range}")
    logger.info("=" * 60)

    # 1. 설정 로드
    config_path = os.environ.get("CONFIG_PATH", "config.yaml")
    try:
        config = load_config(config_path)
    except FileNotFoundError:
        logger.error(f"설정 파일을 찾을 수 없습니다: {config_path}")
        sys.exit(1)

    collection_days = config.get("schedule", {}).get("collection_window_days", 7)
    categories_config = config.get("categories", {})

    # 2. 데이터베이스 초기화
    db = PaperDatabase()

    # 3. 논문 수집 (7일간)
    logger.info("--- 1단계: 7일간 논문 수집 ---")
    all_papers = collect_papers(config)
    total_collected = len(all_papers)

    if total_collected == 0:
        logger.warning("수집된 논문이 없습니다.")
        if not args.dry_run:
            html = generate_report({}, categories_config, collection_days=collection_days)
            subject = get_email_subject(config)
            recipient = config.get("email", {}).get("recipient", "smlim@jbnu.ac.kr")
            send_email(subject, html, recipient)
        return

    # 4. 중복 제거
    logger.info("--- 2단계: 중복 제거 ---")
    new_papers = db.filter_new_papers(all_papers)
    logger.info(f"신규 논문: {len(new_papers)}편 (전체 {total_collected}편)")

    if not new_papers:
        logger.info("모든 논문이 이미 처리되었습니다.")
        if not args.dry_run:
            html = generate_report({}, categories_config, collection_days=collection_days)
            subject = get_email_subject(config)
            recipient = config.get("email", {}).get("recipient", "smlim@jbnu.ac.kr")
            send_email(subject, html, recipient)
        return

    # 5. 7개 카테고리별 분류
    logger.info("--- 3단계: 7개 카테고리별 분류 ---")
    categorized = filter_and_classify(new_papers, config)
    total_filtered = sum(len(v) for v in categorized.values())

    # 6. Gemini 분석 (1회 호출)
    logger.info("--- 4단계: Gemini 분석 (1회 API 호출) ---")
    ai_result = None
    ai_success = False

    try:
        from src.analyzer import GeminiAnalyzer
        analyzer = GeminiAnalyzer(config)
        ai_result = analyzer.analyze_papers(categorized, categories_config)
        ai_success = ai_result is not None
        logger.info(
            f"Gemini: {'성공' if ai_success else '실패 (fallback)'} | "
            f"API 호출: {analyzer.api_calls}회"
        )
    except ValueError as e:
        logger.warning(f"Gemini 초기화 실패 (GEMINI_API_KEY 미설정?): {e}")
    except Exception as e:
        logger.warning(f"Gemini 오류: {e}")

    # 7. 리포트 생성 (새 HTML 템플릿)
    logger.info("--- 5단계: 리포트 생성 ---")
    html = generate_report(
        categorized_papers=categorized,
        categories_config=categories_config,
        ai_result=ai_result,
        collection_days=collection_days,
    )
    subject = get_email_subject(config)

    # 8. 발송 또는 dry-run
    if args.dry_run:
        output_path = "output.html"
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(html)
        logger.info(f"[DRY-RUN] HTML 저장 완료: {output_path}")
        logger.info(f"[DRY-RUN] 이메일 제목: {subject}")
    else:
        logger.info("--- 6단계: 이메일 발송 ---")
        recipient = config.get("email", {}).get("recipient", "smlim@jbnu.ac.kr")
        success = send_email(subject, html, recipient)

        if not success:
            logger.error("이메일 발송 실패")
            sys.exit(1)

    # 9. 데이터베이스 저장 (주간 통계)
    logger.info("--- 7단계: 데이터베이스 저장 ---")
    all_analyzed = []
    for papers in categorized.values():
        all_analyzed.extend(papers)
    db.save_papers(all_analyzed)
    db.save_weekly_trends(categorized, categories_config)

    api_calls = analyzer.api_calls if ai_success else 0
    logger.info("=" * 60)
    logger.info(
        f"[PPEL Weekly Digest] {date_range} | "
        f"수집 {total_collected}편 → 필터 {total_filtered}편 | "
        f"API {api_calls}회 | "
        f"{'발송 완료' if not args.dry_run else 'DRY-RUN 완료'}"
    )
    logger.info("=" * 60)


if __name__ == "__main__":
    main()
