"""NTIS 국가R&D통합공고 크롤러.

IRIS보다 상류이며 부처 통합공고와 사전예고를 포함함.
상세는 roRndUid 파라미터로 식별됨.
"""

import re

from bs4 import BeautifulSoup

from .common import (find_dates, get, make_session, period_from_text,
                     save_raw, squeeze)

BASE = "https://www.ntis.go.kr"
LIST_URL = BASE + "/rndgate/eg/un/ra/mng.do"
VIEW_URL = BASE + "/rndgate/eg/un/ra/view.do"

RO_UID = re.compile(r"roRndUid['\"]?\s*[=:,]\s*['\"]?(\d{4,10})")


def _extract_ids(html):
    seen, out = set(), []
    for m in RO_UID.finditer(html):
        v = m.group(1)
        if v not in seen:
            seen.add(v)
            out.append(v)
    return out


def parse_list(html):
    """목록에서 roRndUid 기반 레코드 추출.

    NTIS 목록은 표 형태이므로 행 단위로 우선 시도하고, 실패 시 ID만 회수함.
    """
    soup = BeautifulSoup(html, "lxml")
    records, seen = [], set()

    for row in soup.find_all("tr"):
        raw = str(row)
        ids = _extract_ids(raw)
        if not ids:
            continue
        uid = ids[0]
        if uid in seen:
            continue
        cells = [squeeze(td.get_text(" ", strip=True)) for td in row.find_all(["td", "th"])]
        cells = [c for c in cells if c]
        if not cells:
            continue
        title = max(cells, key=len)
        dates = find_dates(" ".join(cells))
        seen.add(uid)
        records.append({
            "src": "ntis",
            "ancm_id": "n" + uid,
            "ro_uid": uid,
            "title": title,
            "ministry": cells[0] if len(cells) > 1 and cells[0] != title else "",
            "agency": "",
            "ancm_no": "",
            "posted": dates[0] if dates else "",
            "kind": "",
            "source": "%s?roRndUid=%s" % (VIEW_URL, uid),
        })

    if not records:
        for uid in _extract_ids(html):
            records.append({
                "src": "ntis", "ancm_id": "n" + uid, "ro_uid": uid,
                "title": "", "ministry": "", "agency": "", "ancm_no": "",
                "posted": "", "kind": "",
                "source": "%s?roRndUid=%s" % (VIEW_URL, uid),
            })
    return records


def fetch_detail(session, record):
    html = get(session, VIEW_URL, params={"roRndUid": record["ro_uid"]})
    if not html:
        return record
    soup = BeautifulSoup(html, "lxml")
    for tag in soup(["script", "style", "nav", "header", "footer"]):
        tag.decompose()
    body = squeeze(soup.get_text(" ", strip=True))

    start, deadline = period_from_text(body)
    record["start"] = start or record.get("posted") or ""
    record["deadline"] = deadline or ""
    if not record.get("title"):
        h = soup.find(["h2", "h3", "h4"])
        record["title"] = squeeze(h.get_text(" ", strip=True)) if h else ""
    record["body"] = body[:4000]
    return record


def crawl(detail=True, probe=False):
    session = make_session()
    html = get(session, LIST_URL)
    if not html:
        return []
    save_raw("ntis_list", html)
    if probe:
        print("--- NTIS probe ---")
        print("roRndUid 발견: %d개 -> %s"
              % (len(_extract_ids(html)), _extract_ids(html)[:5]))
        soup = BeautifulSoup(html, "lxml")
        print("tr 개수: %d" % len(soup.find_all("tr")))

    records = parse_list(html)
    print("[ntis] 목록 %d건" % len(records))
    if detail:
        for i, rec in enumerate(records, 1):
            fetch_detail(session, rec)
            print("  (%d/%d) %s | %s ~ %s"
                  % (i, len(records), rec["title"][:38],
                     rec.get("start") or "?", rec.get("deadline") or "?"))
    return records
