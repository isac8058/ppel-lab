"""IRIS 사업공고 크롤러.

실제 구조(2026-08-17 원본 HTML 확인):
- 목록 화면(retrieveBsnsAncmBtinSituListView.do)은 검색 폼 + 서버 렌더링된
  1페이지 목록을 담은 셸이고, 목록 데이터는 JSON API
  (POST retrieveBsnsAncmBtinSituList.do)가 제공함.
- JSON 키: listBsnsAncmBtinSitu[] 안에 ancmId, ancmTl(공고명),
  blngGovdSeNm(부처), sorgnNm(전문기관), ancmNo(공고번호), ancmDe(공고일자),
  rcveSttSeNmLst(공고상태), pbofrTpSeNmLst(공모유형),
  paginationInfo.totalPageCount 로 페이징.
- 상세 링크는 f_bsnsAncmBtinSituListForm_view('023457','ancmIng') 형태의
  onclick 이며, 상세 화면은 GET이 막히면 폼 POST로 열림.

1차는 JSON API, 실패 시 셸 HTML의 서버 렌더링 목록을 파싱함.
"""

import json
import re

from bs4 import BeautifulSoup

from .common import (find_dates, get, make_session, period_from_text, post,
                     save_raw, squeeze)

BASE = "https://www.iris.go.kr"
LIST_VIEW_URL = BASE + "/contents/retrieveBsnsAncmBtinSituListView.do"
LIST_API_URL = BASE + "/contents/retrieveBsnsAncmBtinSituList.do"
VIEW_URL = BASE + "/contents/retrieveBsnsAncmView.do"

# f_bsnsAncmBtinSituListForm_view('023457','ancmIng') / fn_view('023557') 모두 수용
VIEW_ONCLICK = re.compile(r"\w*_?view\w*\(\s*['\"](\d{4,8})['\"]\s*(?:,\s*['\"](\w+)['\"])?", re.I)
ANCM_ID = re.compile(r"ancmId['\"]?\s*[=:,]\s*['\"]?(\d{4,8})")
# "우주항공청 공고 제2026-0095호"처럼 부처명(공백 포함)이 앞에 붙는 형태까지 수용
ANCM_NO = re.compile(r"공고번호\s*:?\s*([가-힣A-Za-z()·\s]{0,30}?공고\s*제?\s*[\d\-－–]+호|[A-Z]{2}_\d{4}_\d{3})")
POSTED = re.compile(r"공고일자\s*:?\s*(20\d{2}[.\-]\s*\d{1,2}[.\-]\s*\d{1,2})")
KIND = re.compile(r"공모유형\s*:?\s*([가-힣,\s]{2,30})")

# 목록에 섞여 들어오는 테스트 공고 제외
NOISE = re.compile(r"\(TEST\)|테스트\s*입니다|^\s*$")

AJAX_HEADERS = {
    "X-Requested-With": "XMLHttpRequest",
    "Referer": LIST_VIEW_URL,
    "Accept": "application/json, text/javascript, */*; q=0.01",
}


def _record(ancm_id, title, ministry="", agency="", ancm_no="", posted="", kind=""):
    return {
        "src": "iris",
        "ancm_id": ancm_id,
        "title": title,
        "ministry": ministry,
        "agency": agency,
        "ancm_no": ancm_no,
        "posted": posted,
        "kind": kind,
        "source": "%s?ancmId=%s&ancmPrg=ancmIng" % (VIEW_URL, ancm_id),
    }


def _api_payload(page):
    """목록 폼(serializeObject)이 보내는 것과 같은 이름의 필드를 빈 값으로 전송."""
    return {
        "bizSearch": "", "bsnsTl": "", "ancmPrg": "ancmIng",
        "pageIndex": str(page), "ancmId": "", "ancmNo": "", "ancmTurn": "",
        "seq": "", "hirkSorgnBsnsCd": "", "bsnsAncmTap": "", "shSorgnYyBsnsCd": "",
        "sorgnIdArr": "", "ancmSttArr": "", "pbofrTpArr": "", "qualCndtArr": "",
        "blngGovdSeArr": "", "techFildArr": "", "shBsnsYy": "",
    }


def parse_api_json(data):
    """JSON API 응답에서 레코드 목록을 추출."""
    records = []
    for it in data.get("listBsnsAncmBtinSitu") or []:
        ancm_id = squeeze(str(it.get("ancmId") or ""))
        title = squeeze(str(it.get("ancmTl") or ""))
        if not ancm_id or not title or NOISE.search(title):
            continue
        posted = find_dates(str(it.get("ancmDe") or ""))
        records.append(_record(
            ancm_id, title,
            ministry=squeeze(str(it.get("blngGovdSeNm") or "")),
            agency=squeeze(str(it.get("sorgnNm") or "")),
            ancm_no=squeeze(str(it.get("ancmNo") or "")),
            posted=posted[0] if posted else "",
            kind=squeeze(str(it.get("pbofrTpSeNmLst") or "")),
        ))
    return records


def fetch_api(session, max_pages=5, probe=False):
    """JSON API로 접수중 공고 전체 페이지를 수집."""
    records, page, total_pages = [], 1, 1
    while page <= min(total_pages, max_pages):
        text = post(session, LIST_API_URL, data=_api_payload(page),
                    headers=AJAX_HEADERS)
        if not text:
            break
        try:
            data = json.loads(text)
        except ValueError:
            if probe:
                print("[iris probe] API 응답이 JSON이 아님: %r" % text[:200])
            break
        info = data.get("paginationInfo") or {}
        try:
            total_pages = int(info.get("totalPageCount") or 1)
        except (TypeError, ValueError):
            total_pages = 1
        got = parse_api_json(data)
        records += got
        if probe and page == 1:
            print("[iris probe] API 총 %s건 / %s페이지, 1페이지 %d건 파싱"
                  % (info.get("totalRecordCount"), total_pages, len(got)))
        if not got:
            break
        page += 1

    dedup, seen = [], set()
    for r in records:
        if r["ancm_id"] not in seen:
            seen.add(r["ancm_id"])
            dedup.append(r)
    return dedup


def parse_list(html):
    """셸 HTML에 서버 렌더링된 목록(li 블록)을 파싱. API 실패 시 폴백."""
    soup = BeautifulSoup(html, "lxml")
    records, seen = [], set()

    for a in soup.find_all("a", onclick=VIEW_ONCLICK):
        m = VIEW_ONCLICK.search(a.get("onclick", ""))
        if not m:
            continue
        ancm_id = m.group(1)
        if ancm_id in seen:
            continue
        title = squeeze(a.get_text(" ", strip=True))
        if not title or NOISE.search(title):
            continue

        ministry = agency = ancm_no = posted = kind = ""
        block = a.find_parent("li") or a.find_parent("tr")
        if block is not None:
            text = squeeze(block.get_text(" ", strip=True))
            inst = block.find("span", class_="inst_title")
            head = squeeze(inst.get_text(" ", strip=True)) if inst else \
                (text.split(title)[0] if title in text else text[:120])
            if ">" in head:
                parts = [squeeze(p) for p in head.split(">") if squeeze(p)]
                if len(parts) >= 2:
                    ministry, agency = parts[-2], parts[-1]
                elif parts:
                    ministry = parts[-1]
            no_m = ANCM_NO.search(text)
            if no_m:
                ancm_no = squeeze(no_m.group(1))
            p_m = POSTED.search(text)
            if p_m:
                d = find_dates(p_m.group(1))
                posted = d[0] if d else ""
            k_m = KIND.search(text)
            if k_m:
                kind = squeeze(k_m.group(1))

        seen.add(ancm_id)
        records.append(_record(ancm_id, title, ministry, agency,
                               ancm_no, posted, kind))
    return records


def _body_text(html):
    soup = BeautifulSoup(html, "lxml")
    for tag in soup(["script", "style", "nav", "header", "footer"]):
        tag.decompose()
    return squeeze(soup.get_text(" ", strip=True))


def _looks_like_detail(body):
    return any(label in body for label in
               ("접수기간", "신청기간", "접수 기간", "신청자격", "공고번호"))


def fetch_detail(session, record, save=False):
    """상세 페이지에서 접수 시작일, 마감일, 본문 요약을 채움.

    GET이 셸/메인 페이지를 돌려주면 목록 폼과 같은 방식의 POST로 재시도.
    """
    html = get(session, VIEW_URL,
               params={"ancmId": record["ancm_id"], "ancmPrg": "ancmIng"})
    body = _body_text(html) if html else ""
    if not _looks_like_detail(body):
        payload = _api_payload(1)
        payload["ancmId"] = record["ancm_id"]
        html2 = post(session, VIEW_URL, data=payload,
                     headers={"Referer": LIST_VIEW_URL})
        if html2:
            body2 = _body_text(html2)
            if _looks_like_detail(body2):
                html, body = html2, body2
    if save and html:
        save_raw("iris_detail_%s" % record["ancm_id"], html)
    if not body:
        return record

    start, deadline = period_from_text(body)
    record["start"] = start or record.get("posted") or ""
    record["deadline"] = deadline or ""
    record["body"] = body[:4000]
    return record


def crawl(detail=True, probe=False):
    """IRIS 접수중 목록을 수집. JSON API 우선, 셸 파싱 폴백."""
    session = make_session()

    # 셸을 먼저 열어 세션 쿠키를 받아둠 (API가 세션을 요구할 수 있음)
    shell = get(session, LIST_VIEW_URL)
    if shell:
        save_raw("iris_list", shell)

    records = fetch_api(session, probe=probe)
    if records:
        print("[iris] JSON API로 %d건" % len(records))
    elif shell:
        records = parse_list(shell)
        print("[iris] 셸 파싱 폴백으로 %d건" % len(records))
    else:
        print("[iris] 목록 페이지 접근 실패")
        return []

    if probe:
        _probe_report(shell or "", records)

    if detail:
        for i, rec in enumerate(records, 1):
            fetch_detail(session, rec, save=(probe and i == 1))
            print("  (%d/%d) %s | %s ~ %s"
                  % (i, len(records), rec["title"][:38],
                     rec.get("start") or "?", rec.get("deadline") or "?"))
    return records


def _probe_report(html, records):
    """구조 진단용 출력."""
    print("--- IRIS probe ---")
    print("수집 레코드: %d건" % len(records))
    for r in records[:3]:
        print("  %s | %s > %s | %s"
              % (r["ancm_id"], r["ministry"], r["agency"], r["title"][:40]))
    if html:
        soup = BeautifulSoup(html, "lxml")
        links = soup.find_all("a", onclick=VIEW_ONCLICK)
        print("셸의 _view onclick 링크: %d개" % len(links))
    print("원본은 data/raw 에 저장됨")
