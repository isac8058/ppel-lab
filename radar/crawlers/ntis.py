"""NTIS 국가R&D통합공고 크롤러.

실제 구조(2026-08-17 원본 HTML 확인):
- 목록(mng.do)은 서버 렌더링 표. 각 행(tr)에 data-title 속성이 붙음:
  순번 / 현황(접수예정·접수중·마감) / 공고명 / 부처명 / 접수일 / 마감일 / D-day.
- 공고명 링크는 <a href=".../view.do" onclick="fn_view('1268336')" title="...">
  형태로, roRndUid는 onclick 인자로만 전달됨.
- 상세는 폼 POST(view.do, roRndUid + flag=rndList). 페이징은 pageIndex POST.
- 목록에 접수일·마감일이 있으므로 상세는 채점용 본문 확보 용도.
"""

import re

from bs4 import BeautifulSoup

from .common import (find_dates, get, make_session, period_from_text, post,
                     save_raw, squeeze)

BASE = "https://www.ntis.go.kr"
LIST_URL = BASE + "/rndgate/eg/un/ra/mng.do"
VIEW_URL = BASE + "/rndgate/eg/un/ra/view.do"

FN_VIEW = re.compile(r"fn_view\(\s*['\"](\d{3,12})['\"]")


def _cell(tr, name):
    td = tr.find("td", attrs={"data-title": name})
    return squeeze(td.get_text(" ", strip=True)) if td else ""


def parse_list(html):
    """목록 HTML에서 fn_view 링크 기반으로 레코드를 추출."""
    soup = BeautifulSoup(html, "lxml")
    records, seen = [], set()

    for a in soup.find_all("a", onclick=FN_VIEW):
        m = FN_VIEW.search(a.get("onclick", ""))
        if not m:
            continue
        uid = m.group(1)
        if uid in seen:
            continue
        title = squeeze(a.get("title") or a.get_text(" ", strip=True))
        if not title:
            continue

        ministry = start = deadline = status = ""
        tr = a.find_parent("tr")
        if tr is not None:
            ministry = _cell(tr, "부처명")
            status = _cell(tr, "현황")
            d1 = find_dates(_cell(tr, "접수일"))
            d2 = find_dates(_cell(tr, "마감일"))
            start = d1[0] if d1 else ""
            deadline = d2[0] if d2 else ""
            if not ministry:
                # data-title 속성이 사라진 경우: 링크 셀을 뺀 텍스트 셀 중 첫 한글 셀
                cells = [squeeze(td.get_text(" ", strip=True)) for td in tr.find_all("td")]
                cells = [c for c in cells if c and c != title]
                for c in cells:
                    if re.search(r"[가-힣]", c) and c not in ("접수중", "접수예정", "마감"):
                        ministry = c
                        break
                dates = find_dates(" ".join(cells))
                if dates:
                    start = start or dates[0]
                    deadline = deadline or (dates[-1] if len(dates) > 1 else "")

        seen.add(uid)
        records.append({
            "src": "ntis",
            "ancm_id": "n" + uid,
            "ro_uid": uid,
            "title": title,
            "ministry": ministry,
            "agency": "",
            "ancm_no": "",
            "posted": start,
            "kind": status,
            "start": start,
            "deadline": deadline,
            "source": "%s?roRndUid=%s" % (VIEW_URL, uid),
        })
    return records


def fetch_detail(session, record, save=False):
    """상세 본문을 확보. 목록에서 얻은 접수일·마감일은 상세가 더 정확할 때만 교체."""
    html = post(session, VIEW_URL,
                data={"roRndUid": record["ro_uid"], "flag": "rndList"},
                headers={"Referer": LIST_URL})
    if not html:
        return record
    if save:
        save_raw("ntis_detail_%s" % record["ro_uid"], html)
    soup = BeautifulSoup(html, "lxml")
    for tag in soup(["script", "style", "nav", "header", "footer"]):
        tag.decompose()
    body = squeeze(soup.get_text(" ", strip=True))

    start, deadline = period_from_text(body)
    record["start"] = record.get("start") or start or record.get("posted") or ""
    record["deadline"] = record.get("deadline") or deadline or ""
    record["body"] = body[:4000]
    return record


def crawl(pages=3, detail=True, probe=False):
    """NTIS 공고 목록을 최신순으로 수집. 1페이지 10건, 기본 3페이지."""
    session = make_session()
    records, seen = [], set()

    for page in range(1, pages + 1):
        if page == 1:
            html = get(session, LIST_URL)
        else:
            html = post(session, LIST_URL, data={"pageIndex": str(page)},
                        headers={"Referer": LIST_URL})
        if not html:
            break
        if page == 1:
            save_raw("ntis_list", html)
        got = parse_list(html)
        fresh = [r for r in got if r["ro_uid"] not in seen]
        for r in fresh:
            seen.add(r["ro_uid"])
        records += fresh
        if probe and page == 1:
            print("--- NTIS probe ---")
            print("fn_view 링크 기반 레코드: %d건" % len(got))
            for r in got[:3]:
                print("  %s | %s | %s ~ %s | %s"
                      % (r["ancm_id"], r["ministry"], r["start"] or "?",
                         r["deadline"] or "?", r["title"][:40]))
        if not fresh:
            break

    print("[ntis] 목록 %d건" % len(records))
    if detail:
        for i, rec in enumerate(records, 1):
            fetch_detail(session, rec, save=(probe and i == 1))
            print("  (%d/%d) %s | %s ~ %s"
                  % (i, len(records), rec["title"][:38],
                     rec.get("start") or "?", rec.get("deadline") or "?"))
    return records
