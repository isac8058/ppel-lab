"""수기 조정본과 병합하고, 마감 공고를 아카이브하고, HTML을 빌드함.

원칙: overrides.json 이 항상 이긴다. 손으로 고친 값은 크롤러가 덮지 않는다.
"""

import datetime as dt
import json
import pathlib
import re

from crawlers.common import kst_today

ROOT = pathlib.Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
OPPS = DATA / "opportunities.json"
ARCHIVE = DATA / "archive.json"
OVERRIDES = DATA / "overrides.json"
TEMPLATE = ROOT / "template.html"
OUTPUT = ROOT / "index.html"

BLOCK = re.compile(
    r'(<script id="opportunityData" type="application/json">)(.*?)(</script>)',
    re.S)

# 자동 수집이 덮으면 안 되는 필드
PROTECTED = ["fit", "axes", "flags", "role", "category",
             "summary", "rationale", "action", "start", "deadline",
             "internalDeadline"]


def _read_json(path, default):
    if path.exists():
        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except Exception as exc:
            print("[build] %s 읽기 실패: %r" % (path.name, exc))
    return default


def apply_overrides(items):
    """수기 조정값을 덮어씌움. 오직 여기서만 사람 손이 이김."""
    ov = _read_json(OVERRIDES, {})
    hits = 0
    for item in items:
        patch = ov.get(item["id"])
        if not patch:
            continue
        hits += 1
        for key, value in patch.items():
            if key in PROTECTED or key not in item:
                item[key] = value
    if hits:
        print("[build] 수기 조정 %d건 적용" % hits)
    return items


ANCM_IN_URL = re.compile(r"ancmId=(\d{4,8})")


def _norm_title(t):
    """중복 판정용 제목 정규화. normalize._norm_title 과 동일 규칙."""
    t = re.sub(r"\s+", "", t or "")
    t = re.sub(r"[()\[\]<>·,\.]", "", t)
    t = re.sub(r"20\d{2}년도?", "", t)
    return t


def _match_legacy(item, legacy_items):
    """크롤러 도입 전에 수기로 만든 항목과 같은 공고인지 판정.

    1순위는 source URL의 ancmId, 2순위는 정규화 제목의 포함 관계.
    수기 항목은 제목을 줄여 적는 경우가 많아 완전 일치는 기대할 수 없음.
    """
    ancm = ANCM_IN_URL.search(item.get("source") or "")
    fresh_title = _norm_title(item.get("title"))
    for legacy in legacy_items:
        lancm = ANCM_IN_URL.search(legacy.get("source") or "")
        if ancm and lancm and ancm.group(1) == lancm.group(1):
            return legacy
        lt = _norm_title(legacy.get("title"))
        if len(lt) >= 12 and (lt in fresh_title or fresh_title in lt):
            return legacy
    return None


def merge_with_existing(fresh):
    """기존 목록과 병합. 사라진 공고도 마감 전이면 유지함.

    크롤링 실패나 목록 페이지 이탈로 항목이 통째로 증발하는 사고를 막음.
    크롤러 도입 전 수기 항목(레거시)은 같은 공고의 크롤러 항목이 오면
    수기 판단값을 물려주고 흡수해 중복 노출을 막음.
    """
    existing = _read_json(OPPS, [])
    by_id = {i["id"]: i for i in existing}
    legacy_items = [i for i in existing if not i.get("_meta", {}).get("src")]

    for item in fresh:
        prev = by_id.get(item["id"])
        if prev is None:
            legacy = _match_legacy(item, legacy_items)
            if legacy is not None:
                # 수기 큐레이션이 LLM 채점을 이김. 레거시 항목은 흡수 후 제거
                for key in PROTECTED:
                    if legacy.get(key):
                        item[key] = legacy[key]
                item["_meta"]["first_seen"] = legacy.get("_meta", {}).get(
                    "first_seen", item["_meta"]["crawled_at"])
                item["_meta"]["curated"] = True
                by_id.pop(legacy["id"], None)
                legacy_items = [l for l in legacy_items if l["id"] != legacy["id"]]
                print("[build] 수기 항목 %s -> %s 병합" % (legacy["id"], item["id"]))
            else:
                item["_meta"]["first_seen"] = item["_meta"]["crawled_at"]
        else:
            # 수기 확정(curated) 항목은 캐시된 LLM 점수로 되돌리지 않고,
            # 그 외에는 아직 채점 안 된 항목만 이전 채점값을 물려받음
            if prev.get("_meta", {}).get("curated") or (not item.get("fit") and prev.get("fit")):
                for key in PROTECTED:
                    if prev.get(key):
                        item[key] = prev[key]
                if prev.get("_meta", {}).get("curated"):
                    item["_meta"]["curated"] = True
            item["_meta"]["first_seen"] = prev.get("_meta", {}).get("first_seen", item["_meta"]["crawled_at"])
        by_id[item["id"]] = item
    return list(by_id.values())


def split_archive(items):
    """마감 지난 공고는 아카이브로 이동. 차년도 재도전 근거로 남김."""
    today = kst_today().isoformat()
    live, expired = [], []
    for item in items:
        (expired if item.get("deadline", "9999") < today else live).append(item)

    if expired:
        archive = _read_json(ARCHIVE, [])
        known = {a["id"] for a in archive}
        added = 0
        for item in expired:
            if item["id"] in known:
                continue
            item["_meta"]["archived_at"] = today
            archive.append(item)
            added += 1
        ARCHIVE.write_text(json.dumps(archive, ensure_ascii=False, indent=1), encoding="utf-8")
        print("[build] 아카이브 이동 %d건 (누적 %d건)" % (added, len(archive)))
    return live


def strip_meta(items):
    out = []
    for item in items:
        clean = {k: v for k, v in item.items() if k != "_meta"}
        out.append(clean)
    return out


def build_html(items):
    if not TEMPLATE.exists():
        print("[build] template.html 없음. HTML 빌드 생략")
        return False
    html = TEMPLATE.read_text(encoding="utf-8")
    if not BLOCK.search(html):
        print("[build] template.html 에서 opportunityData 블록을 못 찾음")
        return False

    ordered = sorted(items, key=lambda i: (-i.get("fit", 0), i.get("deadline", "")))
    payload = json.dumps(strip_meta(ordered), ensure_ascii=False, indent=2)
    payload = "\n  " + payload.replace("\n", "\n  ") + "\n  "
    new_html = BLOCK.sub(lambda m: m.group(1) + payload + m.group(3), html, count=1)

    stamp = kst_today().isoformat()
    new_html = re.sub(r'(<meta name="data-date" content=")[^"]*(")',
                      r"\g<1>%s\g<2>" % stamp, new_html)
    OUTPUT.write_text(new_html, encoding="utf-8")
    print("[build] index.html 생성. 공고 %d건" % len(ordered))
    return True


def run(fresh_items):
    DATA.mkdir(parents=True, exist_ok=True)
    merged = merge_with_existing(fresh_items)
    merged = apply_overrides(merged)
    live = split_archive(merged)
    OPPS.write_text(json.dumps(live, ensure_ascii=False, indent=1), encoding="utf-8")
    build_html(live)
    return live
