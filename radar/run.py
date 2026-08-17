#!/usr/bin/env python3
"""정부 R&D 공고 레이더 수집 파이프라인.

사용법
  python run.py --probe              구조 진단만. 원본 HTML을 data/raw 에 저장
  python run.py --no-score           크롤링과 빌드만. API 호출 없음
  python run.py                      전체 실행
  python run.py --source iris        특정 소스만
"""

import argparse
import json
import sys
import traceback

from crawlers import iris, ntis
from pipeline import build, normalize, score


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--probe", action="store_true", help="구조 진단 출력")
    ap.add_argument("--no-score", action="store_true", help="LLM 채점 생략")
    ap.add_argument("--no-detail", action="store_true", help="상세 페이지 조회 생략")
    ap.add_argument("--source", default="all", choices=["all", "iris", "ntis"])
    ap.add_argument("--limit", type=int, default=40, help="1회 최대 채점 건수")
    args = ap.parse_args()

    detail = not args.no_detail
    records = []

    if args.source in ("all", "iris"):
        try:
            records += iris.crawl(detail=detail, probe=args.probe)
        except Exception:
            traceback.print_exc()
            print("[warn] IRIS 수집 실패. 계속 진행함")

    if args.source in ("all", "ntis"):
        try:
            records += ntis.crawl(detail=detail, probe=args.probe)
        except Exception:
            traceback.print_exc()
            print("[warn] NTIS 수집 실패. 계속 진행함")

    if args.probe:
        print("\n[probe] 수집 원시 레코드 %d건" % len(records))
        print(json.dumps(records[:2], ensure_ascii=False, indent=2)[:2200])
        return 0

    if not records:
        print("[abort] 수집 결과 0건. 기존 데이터를 보존하고 종료함")
        return 1

    items = normalize.normalize(records)
    if not args.no_score:
        items = score.score_all(items, limit=args.limit)

    live = build.run(items)
    print("\n완료. 활성 공고 %d건" % len(live))
    return 0


if __name__ == "__main__":
    sys.exit(main())
