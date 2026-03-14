"""SQLite 데이터베이스 관리 모듈 - 중복 방지 및 트렌드 추적."""

import json
import logging
import os
import sqlite3
from collections import defaultdict
from datetime import datetime, timedelta, timezone

from src.collector import Paper

logger = logging.getLogger(__name__)

DEFAULT_DB_PATH = "papers.db"


class PaperDatabase:
    """논문 데이터베이스 관리."""

    def __init__(self, db_path: str | None = None):
        self.db_path = db_path or DEFAULT_DB_PATH
        self._init_db()

    def _init_db(self):
        """데이터베이스 초기화."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS papers (
                    doi TEXT PRIMARY KEY,
                    title TEXT NOT NULL,
                    journal TEXT,
                    date TEXT,
                    keywords TEXT,
                    relevance_score REAL,
                    summary TEXT,
                    ppel_score INTEGER DEFAULT 0,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
            """)
            conn.execute("""
                CREATE TABLE IF NOT EXISTS daily_trends (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    date TEXT NOT NULL,
                    keyword TEXT NOT NULL,
                    count INTEGER DEFAULT 1,
                    UNIQUE(date, keyword)
                )
            """)
            conn.execute("""
                CREATE TABLE IF NOT EXISTS weekly_trends (
                    week_start TEXT,
                    category TEXT,
                    paper_count INTEGER,
                    top_keywords TEXT,
                    PRIMARY KEY (week_start, category)
                )
            """)
            conn.commit()
        logger.info(f"데이터베이스 초기화 완료: {self.db_path}")

    def is_duplicate(self, doi: str) -> bool:
        """DOI 기준 중복 체크."""
        if not doi:
            return False
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("SELECT 1 FROM papers WHERE doi = ?", (doi,))
            return cursor.fetchone() is not None

    def filter_new_papers(self, papers: list[Paper]) -> list[Paper]:
        """중복 논문 제거."""
        new_papers = []
        for p in papers:
            if not p.doi or not self.is_duplicate(p.doi):
                new_papers.append(p)
            else:
                logger.debug(f"중복 논문 스킵: {p.doi}")

        skipped = len(papers) - len(new_papers)
        if skipped:
            logger.info(f"중복 논문 {skipped}편 제거, {len(new_papers)}편 유지")
        return new_papers

    def save_paper(self, paper: Paper):
        """논문 저장."""
        if not paper.doi:
            return
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                """
                INSERT OR REPLACE INTO papers
                (doi, title, journal, date, keywords, relevance_score, summary, ppel_score)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    paper.doi,
                    paper.title,
                    paper.journal,
                    paper.published_date.isoformat(),
                    ",".join(paper.keywords),
                    paper.relevance_score,
                    paper.summary_kr or paper.summary,
                    paper.ppel_score,
                ),
            )
            conn.commit()

    def save_papers(self, papers: list[Paper]):
        """여러 논문 저장."""
        for p in papers:
            self.save_paper(p)
        logger.info(f"{len(papers)}편 데이터베이스 저장 완료")

    def save_weekly_trends(
        self,
        categorized_papers: dict[str, list[Paper]],
        categories_config: dict,
        week_start: str | None = None,
    ):
        """주간 트렌드 저장."""
        if not week_start:
            today = datetime.now(timezone.utc)
            start = today - timedelta(days=today.weekday())
            week_start = start.strftime("%Y-%m-%d")

        with sqlite3.connect(self.db_path) as conn:
            for cat_key, papers in categorized_papers.items():
                if not papers:
                    continue

                cat_name = categories_config.get(cat_key, {}).get("name", cat_key)

                # 카테고리 내 키워드 빈도 집계
                keyword_counts: dict[str, int] = defaultdict(int)
                cat_keywords = categories_config.get(cat_key, {}).get("keywords", [])
                for p in papers:
                    text = f"{p.title} {p.abstract}".lower()
                    for kw in cat_keywords:
                        if kw.lower() in text:
                            keyword_counts[kw] += 1

                top_kw = sorted(keyword_counts.items(), key=lambda x: x[1], reverse=True)[:5]
                top_keywords_json = json.dumps(
                    [{"keyword": k, "count": c} for k, c in top_kw],
                    ensure_ascii=False,
                )

                conn.execute(
                    """
                    INSERT OR REPLACE INTO weekly_trends
                    (week_start, category, paper_count, top_keywords)
                    VALUES (?, ?, ?, ?)
                    """,
                    (week_start, cat_name, len(papers), top_keywords_json),
                )
            conn.commit()

        logger.info(f"주간 트렌드 저장 완료: {week_start}")

    def save_daily_trends(self, trends: list[dict], date: str | None = None):
        """일간 트렌드 키워드 저장."""
        if not date:
            date = datetime.now(timezone.utc).strftime("%Y-%m-%d")

        with sqlite3.connect(self.db_path) as conn:
            for trend in trends:
                keyword = trend.get("keyword", "")
                if not keyword:
                    continue
                conn.execute(
                    """
                    INSERT OR REPLACE INTO daily_trends (date, keyword, count)
                    VALUES (?, ?, COALESCE(
                        (SELECT count + 1 FROM daily_trends WHERE date = ? AND keyword = ?),
                        1
                    ))
                    """,
                    (date, keyword, date, keyword),
                )
            conn.commit()
        logger.info(f"트렌드 키워드 {len(trends)}개 저장 완료")

    def get_weekly_trends(self) -> list[dict]:
        """최근 7일간 트렌드 데이터 조회."""
        end_date = datetime.now(timezone.utc)
        start_date = end_date - timedelta(days=7)

        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(
                """
                SELECT keyword, date, count
                FROM daily_trends
                WHERE date >= ? AND date <= ?
                ORDER BY keyword, date
                """,
                (
                    start_date.strftime("%Y-%m-%d"),
                    end_date.strftime("%Y-%m-%d"),
                ),
            )

            rows = cursor.fetchall()

        keyword_data: dict[str, dict[str, int]] = defaultdict(dict)
        for keyword, date, count in rows:
            keyword_data[keyword][date] = count

        dates = [
            (end_date - timedelta(days=i)).strftime("%Y-%m-%d") for i in range(6, -1, -1)
        ]

        result = []
        for keyword, date_counts in keyword_data.items():
            counts = [date_counts.get(d, 0) for d in dates]
            total = sum(counts)
            result.append(
                {
                    "keyword": keyword,
                    "counts": counts,
                    "total": total,
                    "dates": dates,
                }
            )

        result.sort(key=lambda x: x["total"], reverse=True)
        return result
