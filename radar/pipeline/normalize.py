"""수집 레코드를 레이더 HTML 스키마로 정규화하고 중복을 제거함."""

import datetime as dt
import pathlib
import re

import yaml

from crawlers.common import kst_today

ROOT = pathlib.Path(__file__).resolve().parent.parent
PROFILE = yaml.safe_load((ROOT / "config" / "profile.yml").read_text(encoding="utf-8"))


def _norm_title(t):
    """중복 판정용 제목 정규화. 공백, 괄호, 연도 표기 차이를 흡수."""
    t = re.sub(r"\s+", "", t or "")
    t = re.sub(r"[()\[\]<>·,\.]", "", t)
    t = re.sub(r"20\d{2}년도?", "", t)
    return t


def passes_prefilter(rec):
    """LLM 채점 대상인지 판단. 비용 관문."""
    title = rec.get("title") or ""
    haystack = (title + " " + (rec.get("body") or ""))[:2500]
    for bad in PROFILE.get("exclude_keywords", []):
        if bad in title:
            return False
    for good in PROFILE.get("include_keywords", []):
        if good in haystack:
            return True
    return False


def to_schema(rec):
    """레이더 HTML이 읽는 필드 구조로 변환. 채점 전 상태."""
    today = kst_today()
    deadline = rec.get("deadline") or ""
    if not deadline:
        window = int(PROFILE.get("fallback_window_days", 30))
        deadline = (today + dt.timedelta(days=window)).isoformat()
        estimated = True
    else:
        estimated = False

    start = rec.get("start") or rec.get("posted") or today.isoformat()
    if start > deadline:
        start = deadline

    return {
        "id": "%s-%s" % (rec.get("src", "x"), rec.get("ancm_id", "0")),
        "title": rec.get("title", "").strip(),
        "ministry": rec.get("ministry") or "미상",
        "agency": rec.get("agency") or "미상",
        "category": "미분류",
        "start": start,
        "deadline": deadline,
        "fit": 0,
        "role": "미정",
        "axes": {},
        "flags": (["마감일 추정치"] if estimated else []),
        "summary": "",
        "rationale": "",
        "action": "",
        "source": rec.get("source", ""),
        "_meta": {
            "src": rec.get("src", ""),
            "ancm_no": rec.get("ancm_no", ""),
            "kind": rec.get("kind", ""),
            "posted": rec.get("posted", ""),
            "crawled_at": today.isoformat(),
            "scored_at": "",
            "body": (rec.get("body") or "")[:3000],
        },
    }


def dedupe(items):
    """IRIS와 NTIS에 같은 공고가 올라오므로 제목 기준으로 병합.

    IRIS 쪽이 접수 정보가 정확하므로 우선함.
    """
    by_title = {}
    order = []
    for item in items:
        key = _norm_title(item["title"])
        if not key:
            continue
        if key not in by_title:
            by_title[key] = item
            order.append(key)
            continue
        kept = by_title[key]
        incoming_iris = item["_meta"].get("src") == "iris"
        kept_iris = kept["_meta"].get("src") == "iris"
        if incoming_iris and not kept_iris:
            by_title[key] = item
        elif incoming_iris == kept_iris and len(item.get("_meta", {}).get("body", "")) > len(kept.get("_meta", {}).get("body", "")):
            by_title[key] = item
    return [by_title[k] for k in order]


def normalize(records):
    """수집 레코드 목록 전체를 처리."""
    kept, dropped = [], 0
    for rec in records:
        if not (rec.get("title") or "").strip():
            dropped += 1
            continue
        if not passes_prefilter(rec):
            dropped += 1
            continue
        kept.append(to_schema(rec))
    merged = dedupe(kept)
    print("[normalize] 입력 %d건 -> 관련 %d건 -> 중복제거 %d건 (제외 %d건)"
          % (len(records), len(kept), len(merged), dropped))
    return merged
