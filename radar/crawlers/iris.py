"""IRIS 사업공고 크롤러.

목록 페이지는 서버 렌더링이며 상세 링크는 ancmId 파라미터로 식별됨.
DOM 클래스명은 개편에 취약하므로 URL 패턴과 텍스트 라벨에만 의존함.
목록에 마감일이 없으므로 상세 페이지를 2단계로 조회함.
"""

import re

from bs4 import BeautifulSoup

from .common import (find_dates, get, make_session, period_from_text,
                     save_raw, squeeze)

BASE = "https://www.iris.go.kr"
LIST_URL = BASE + "/contents/retrieveBsnsAncmBtinSituListView.do"
VIEW_URL = BASE + "/contents/retrieveBsnsAncmView.do"

ANCM_ID = re.compile(r"ancmId['\"]?\s*[=:,]\s*['\"]?(\d{4,8})")
# onclick 이 fn_view('023557') 형태로 ancmId 문자열 없이 넘기는 경우 대비
ANCM_FALLBACK = re.compile(r"\b(?:fn_|go|view|detail)\w*\s*\(\s*['\"](\d{4,8})['\"]")
# "우주항공청 공고 제2026-0095호"처럼 부처명(공백 포함)이 앞에 붙는 형태까지 수용
ANCM_NO = re.compile(r"공고번호\s*:?\s*([가-힣A-Za-z()·\s]{0,30}?공고\s*제?\s*[\d\-\uff0d\u2013]+호|[A-Z]{2}_\d{4}_\d{3})")
POSTED = re.compile(r"공고일자\s*:?\s*(20\d{2}[.\-]\d{1,2}[.\-]\d{1,2})")
KIND = re.compile(r"공모유형\s*:?\s*([가-힣,\s]{2,30})")

# 목록에 섞여 들어오는 테스트 공고 제외
NOISE = re.compile(r"\(TEST\)|테스트\s*입니다|^\s*$")


def _extract_ids(html):
    """페이지 전체에서 ancmId를 등장 순서대로, 중복 없이 추출.

    1차는 ancmId 라벨, 실패 시 JS 함수 인자 형태를 폴백으로 시도함.
    """
    for pattern in (ANCM_ID, ANCM_FALLBACK):
        seen, out = set(), []
        for m in pattern.finditer(html):
            v = m.group(1)
            if v not in seen:
                seen.add(v)
                out.append(v)
        if out:
            return out
    return []


def _item_blocks(soup):
    """목록 항목 블록 후보를 반환.

    클래스명을 모르므로 공고번호 라벨에서 위로 올라가되, 제목 링크까지
    함께 담는 조상에서 멈춤. 목록 컨테이너 태그를 만나면 그것을 블록으로 삼음.
    """
    found = []
    for node in soup.find_all(string=re.compile("공고번호")):
        parent = node.parent
        best, hops = None, 0
        while parent is not None and hops < 7:
            if parent.name in ("li", "tr", "article"):
                best = parent
                break
            text = parent.get_text(" ", strip=True)
            if "공고번호" in text and parent.find("a") is not None:
                best = parent
                break
            parent = parent.parent
            hops += 1
        if best is not None and not any(best is b for b in found):
            found.append(best)

    # 다른 블록 안에 중첩된 블록은 버리고 바깥쪽만 남김
    blocks = []
    for b in found:
        if any(o is not b and o in b.parents for o in found):
            continue
        blocks.append(b)
    return blocks


def parse_list(html):
    """목록 HTML에서 공고 요약 레코드 목록을 반환."""
    soup = BeautifulSoup(html, "lxml")
    records = []

    for block in _item_blocks(soup):
        raw = block.get_text(" ", strip=True)
        text = squeeze(raw)
        if NOISE.search(text):
            continue

        # 제목: 블록 내 링크 중 가장 긴 텍스트
        title = ""
        for a in block.find_all("a"):
            cand = squeeze(a.get_text(" ", strip=True))
            if len(cand) > len(title):
                title = cand
        if not title:
            strong = block.find(["strong", "h3", "h4"])
            title = squeeze(strong.get_text(" ", strip=True)) if strong else ""
        if not title or NOISE.search(title):
            continue

        ids = _extract_ids(str(block))
        ancm_id = ids[0] if ids else None
        if not ancm_id:
            continue

        # 부처 > 전문기관
        ministry, agency = "", ""
        head = text.split(title)[0] if title in text else text[:120]
        if ">" in head:
            parts = [squeeze(p) for p in head.split(">")]
            parts = [p for p in parts if p]
            if len(parts) >= 2:
                ministry, agency = parts[-2], parts[-1]
            elif parts:
                ministry = parts[-1]

        posted = ""
        m = POSTED.search(text)
        if m:
            d = find_dates(m.group(1))
            posted = d[0] if d else ""

        no_m = ANCM_NO.search(text)
        kind_m = KIND.search(text)

        records.append({
            "src": "iris",
            "ancm_id": ancm_id,
            "title": title,
            "ministry": ministry,
            "agency": agency,
            "ancm_no": squeeze(no_m.group(1)) if no_m else "",
            "posted": posted,
            "kind": squeeze(kind_m.group(1)) if kind_m else "",
            "source": "%s?ancmId=%s&ancmPrg=ancmIng" % (VIEW_URL, ancm_id),
        })

    # 블록 파싱이 실패한 경우 ID만이라도 회수
    if not records:
        for ancm_id in _extract_ids(html):
            records.append({
                "src": "iris", "ancm_id": ancm_id, "title": "",
                "ministry": "", "agency": "", "ancm_no": "",
                "posted": "", "kind": "",
                "source": "%s?ancmId=%s&ancmPrg=ancmIng" % (VIEW_URL, ancm_id),
            })

    dedup, seen = [], set()
    for r in records:
        if r["ancm_id"] in seen:
            continue
        seen.add(r["ancm_id"])
        dedup.append(r)
    return dedup


def fetch_detail(session, record):
    """상세 페이지에서 접수 시작일, 마감일, 본문 요약을 채움."""
    html = get(session, VIEW_URL,
               params={"ancmId": record["ancm_id"], "ancmPrg": "ancmIng"})
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

    # 채점용 본문. 앞부분 위주로 자름
    record["body"] = body[:4000]
    return record


def crawl(pages=1, detail=True, probe=False):
    """IRIS 접수중 목록을 수집.

    목록은 최신순이므로 매일 실행하면 1페이지만으로도 신규 공고를 놓치지 않음.
    """
    session = make_session()
    html = get(session, LIST_URL)
    if not html:
        return []
    save_raw("iris_list", html)
    if probe:
        _probe_report(html)

    records = parse_list(html)
    print("[iris] 목록 %d건" % len(records))

    if detail:
        for i, rec in enumerate(records, 1):
            fetch_detail(session, rec)
            print("  (%d/%d) %s | %s ~ %s"
                  % (i, len(records), rec["title"][:38],
                     rec.get("start") or "?", rec.get("deadline") or "?"))
    return records


def _probe_report(html):
    """구조 진단용. 실제 태그와 링크 형태를 눈으로 확인하기 위한 출력."""
    soup = BeautifulSoup(html, "lxml")
    print("--- IRIS probe ---")
    print("ancmId 발견: %d개 -> %s" % (len(_extract_ids(html)), _extract_ids(html)[:5]))
    blocks = _item_blocks(soup)
    print("항목 블록 후보: %d개" % len(blocks))
    if blocks:
        b = blocks[0]
        print("첫 블록 태그: <%s class=%s>" % (b.name, b.get("class")))
        print("첫 블록 텍스트: %s" % squeeze(b.get_text(" ", strip=True))[:220])
        links = b.find_all("a")
        for a in links[:3]:
            print("  a href=%r onclick=%r" % (a.get("href"), a.get("onclick")))
    print("원본은 data/raw 에 저장됨")
