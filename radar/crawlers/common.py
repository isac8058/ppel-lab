"""HTTP 공통 유틸. 세션 재사용, 재시도, 원본 HTML 보존."""

import hashlib
import pathlib
import re
import time

import requests

RAW_DIR = pathlib.Path(__file__).resolve().parent.parent / "data" / "raw"
UA = ("Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/126.0 Safari/537.36")


def make_session():
    s = requests.Session()
    s.headers.update({
        "User-Agent": UA,
        "Accept-Language": "ko-KR,ko;q=0.9",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    })
    return s


def get(session, url, params=None, tries=3, pause=1.2, timeout=25):
    """GET 후 텍스트 반환. 실패 시 None."""
    last = None
    for attempt in range(tries):
        try:
            r = session.get(url, params=params, timeout=timeout)
            if r.status_code == 200 and r.text:
                r.encoding = r.apparent_encoding or "utf-8"
                return r.text
            last = "status %s" % r.status_code
        except Exception as exc:
            last = repr(exc)
        time.sleep(pause * (attempt + 1))
    print("  [fail] %s (%s)" % (url, last))
    return None


def post(session, url, data=None, tries=3, pause=1.2, timeout=25):
    last = None
    for attempt in range(tries):
        try:
            r = session.post(url, data=data or {}, timeout=timeout)
            if r.status_code == 200 and r.text:
                r.encoding = r.apparent_encoding or "utf-8"
                return r.text
            last = "status %s" % r.status_code
        except Exception as exc:
            last = repr(exc)
        time.sleep(pause * (attempt + 1))
    print("  [fail:post] %s (%s)" % (url, last))
    return None


def save_raw(tag, html):
    """원본 HTML 보존. 구조 변경 진단과 probe 모드에서 사용."""
    if not html:
        return None
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    stamp = time.strftime("%Y%m%d")
    digest = hashlib.md5(tag.encode("utf-8")).hexdigest()[:8]
    path = RAW_DIR / ("%s_%s_%s.html" % (stamp, tag[:40].replace("/", "_"), digest))
    path.write_text(html, encoding="utf-8")
    return path


def squeeze(text):
    """공백 정리."""
    if not text:
        return ""
    return re.sub(r"\s+", " ", text).strip()


DATE_PATTERNS = [
    re.compile(r"(20\d{2})[.\-/년]\s*(\d{1,2})[.\-/월]\s*(\d{1,2})"),
    re.compile(r"(20\d{2})(\d{2})(\d{2})"),
]


def find_dates(text):
    """텍스트에서 YYYY-MM-DD 목록을 등장 순서대로, 중복 없이 추출."""
    out = []
    if not text:
        return out
    for pat in DATE_PATTERNS:
        for m in pat.finditer(text):
            y, mo, d = m.group(1), int(m.group(2)), int(m.group(3))
            if not (1 <= mo <= 12 and 1 <= d <= 31):
                continue
            out.append((m.start(), "%s-%02d-%02d" % (y, mo, d)))
        if out:
            break
    out.sort(key=lambda x: x[0])
    result = []
    for _, iso in out:
        if iso not in result:
            result.append(iso)
    return result


def period_from_text(text):
    """접수기간 문구에서 (시작일, 마감일) 추출.

    라벨 우선 탐색 후 실패 시 문서 전체에서 가장 이른/늦은 날짜쌍을 사용.
    """
    if not text:
        return None, None
    labels = ["접수기간", "신청기간", "접수 기간", "공고기간", "접수일정", "신청 기간"]
    for label in labels:
        idx = text.find(label)
        if idx == -1:
            continue
        window = text[idx:idx + 260]
        dates = find_dates(window)
        if len(dates) >= 2:
            return dates[0], dates[1]
        if len(dates) == 1:
            return None, dates[0]
    dates = find_dates(text)
    if len(dates) >= 2:
        return dates[0], dates[-1]
    if len(dates) == 1:
        return None, dates[0]
    return None, None


def kst_today():
    """GitHub Actions는 UTC로 도므로 날짜 기준은 항상 KST로 맞춤."""
    import datetime as _dt
    return (_dt.datetime.now(_dt.timezone.utc) + _dt.timedelta(hours=9)).date()
