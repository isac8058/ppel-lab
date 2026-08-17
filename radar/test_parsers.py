"""파서 단위 테스트. 실제 사이트 접근 없이 로직만 검증함.

픽스처는 2026-08-17 GitHub Actions 실행이 저장한 IRIS·NTIS 원본 HTML에서
목록 항목만 발췌한 것이라 실제 DOM과 동일함(tests/fixtures/).
IRIS는 JSON API가 1차 경로이므로 API 응답 파싱도 함께 검증함.
"""

import json
import pathlib

from crawlers import iris, ntis
from crawlers.common import find_dates, period_from_text
from pipeline import normalize

FIXTURES = pathlib.Path(__file__).resolve().parent / "tests" / "fixtures"
IRIS_SHELL = (FIXTURES / "iris_list_shell.html").read_text(encoding="utf-8")
NTIS_LIST = (FIXTURES / "ntis_list.html").read_text(encoding="utf-8")

# 실제 API 응답 형태(키 이름은 셸의 jsrender 템플릿에서 확인)
IRIS_API_JSON = json.dumps({
    "paginationInfo": {"currentPageNo": 1, "totalPageCount": 3, "totalRecordCount": 22},
    "listBsnsAncmBtinSitu": [
        {"ancmId": "023457", "ancmTl": "2026년도 신규프로젝트 탐색연구 재공고",
         "blngGovdSeNm": "우주항공청", "sorgnNm": "우주항공청",
         "ancmNo": "우주항공청 공고 제2026-0095호", "ancmDe": "2026-08-07",
         "rcveSttSeNmLst": "공고접수중", "pbofrTpSeNmLst": "지정공모"},
        {"ancmId": "017852", "ancmTl": "(TEST) KISTEP 통합공고 테스트 입니다.",
         "blngGovdSeNm": "과학기술정보통신부", "sorgnNm": "한국과학기술기획평가원",
         "ancmNo": "IT_2026_001", "ancmDe": "2026-07-27",
         "rcveSttSeNmLst": "공고접수중", "pbofrTpSeNmLst": "자유공모"},
    ],
}, ensure_ascii=False)

DETAIL_BODY = """
사업공고 상세 2026년도 신규프로젝트 탐색연구 재공고
공고번호 우주항공청 공고 제2026-0095호 공고일자 2026-08-07
접수기간 2026. 08. 11. 09:00 ~ 2026. 09. 10. 18:00 까지
지원분야 우주환경 감시 총 연구개발비 500백만원 이내
신청자격 국내 대학, 출연연, 기업 등 주관연구개발기관
"""


def run():
    fails = []

    def check(label, cond, detail=""):
        mark = "통과" if cond else "실패"
        print("  [%s] %s %s" % (mark, label, detail))
        if not cond:
            fails.append(label)

    print("\n== IRIS JSON API 파싱 ==")
    api_recs = iris.parse_api_json(json.loads(IRIS_API_JSON))
    for r in api_recs:
        print("   %s | %s / %s | %s" % (r["ancm_id"], r["ministry"], r["agency"], r["title"][:44]))
    check("TEST 공고 제외하고 1건", len(api_recs) == 1, "-> %d건" % len(api_recs))
    check("ancmId 추출", api_recs and api_recs[0]["ancm_id"] == "023457")
    check("부처/전문기관 분리", api_recs and api_recs[0]["ministry"] == "우주항공청"
          and api_recs[0]["agency"] == "우주항공청")
    check("공고번호 원문 유지", api_recs and api_recs[0]["ancm_no"] == "우주항공청 공고 제2026-0095호")
    check("공고일자 정규화", api_recs and api_recs[0]["posted"] == "2026-08-07",
          "-> %s" % (api_recs[0]["posted"] if api_recs else None))
    check("상세 URL 생성", api_recs and api_recs[0]["source"].endswith("ancmId=023457&ancmPrg=ancmIng"))

    print("\n== IRIS 셸 HTML 폴백 파싱 (실제 DOM) ==")
    recs = iris.parse_list(IRIS_SHELL)
    for r in recs:
        print("   %s | %s / %s | %s" % (r["ancm_id"], r["ministry"], r["agency"], r["title"][:40]))
    check("실제 목록에서 항목 추출", len(recs) >= 3, "-> %d건" % len(recs))
    check("onclick에서 ancmId 회수", recs and all(r["ancm_id"].isdigit() for r in recs))
    check("TEST 공고 제외", all("TEST" not in r["title"] for r in recs))
    check("부처 > 전문기관 분리", recs and recs[0]["ministry"] and recs[0]["agency"],
          "-> %s / %s" % (recs[0]["ministry"], recs[0]["agency"]) if recs else "")
    check("공고번호 파싱", recs and recs[0]["ancm_no"], "-> %r" % (recs[0]["ancm_no"] if recs else None))
    check("공고일자 파싱", recs and recs[0]["posted"].startswith("2026-"),
          "-> %s" % (recs[0]["posted"] if recs else None))

    print("\n== NTIS 목록 파싱 (실제 DOM) ==")
    nrecs = ntis.parse_list(NTIS_LIST)
    for r in nrecs:
        print("   %s | %s | %s ~ %s | %s" % (r["ancm_id"], r["ministry"],
              r["start"] or "?", r["deadline"] or "?", r["title"][:36]))
    check("fn_view 링크에서 행 추출", len(nrecs) >= 3, "-> %d건" % len(nrecs))
    check("id 접두어", nrecs and nrecs[0]["ancm_id"].startswith("n"))
    check("부처명 셀 파싱", nrecs and nrecs[0]["ministry"] == "산업통상부",
          "-> %r" % (nrecs[0]["ministry"] if nrecs else None))
    check("접수일/마감일 파싱", nrecs and nrecs[0]["start"] and nrecs[0]["deadline"],
          "-> %s ~ %s" % (nrecs[0]["start"], nrecs[0]["deadline"]) if nrecs else "")

    print("\n== 접수기간 추출 ==")
    start, deadline = period_from_text(DETAIL_BODY)
    check("접수기간 라벨 기준 추출", (start, deadline) == ("2026-08-11", "2026-09-10"),
          "-> %s ~ %s" % (start, deadline))
    check("날짜 정규화", find_dates("2026. 08. 11.")[0] == "2026-08-11")
    check("날짜 중복 제거", find_dates("2026.08.11 ~ 2026.08.11") == ["2026-08-11"])
    check("공고번호에 부처명 접두 허용",
          iris.ANCM_NO.search("공고번호 :우주항공청 공고 제2026-0095호 공고일자") is not None)

    print("\n== 사전 필터 ==")
    energy = {"title": "2026년도 2차 에너지수요관리핵심기술개발사업", "body": "에너지저장 소재 개발"}
    forest = {"title": "산림 병해충 방제 실증", "body": "산림 방제 약제 살포"}
    check("관련 공고 통과", normalize.passes_prefilter(energy))
    check("무관 공고 차단", not normalize.passes_prefilter(forest))

    print("\n== 정규화와 중복 제거 ==")
    a = dict(api_recs[0], ancm_id="023398",
             title="AI 응용제품 신속 상용화 지원사업 2차 신규지원 대상과제 공고",
             ministry="산업통상부", agency="한국산업기술기획평가원",
             source="https://www.iris.go.kr/contents/retrieveBsnsAncmView.do?ancmId=023398",
             body="AI 응용제품 센서 상용화", deadline="2026-09-03", start="2026-08-11")
    b = {"src": "ntis", "ancm_id": "n999", "title": "AI 응용제품 신속 상용화 지원사업 2차 신규지원 대상과제 공고",
         "ministry": "산업통상부", "agency": "", "ancm_no": "", "posted": "2026-08-04",
         "kind": "", "source": "x", "body": "센서", "deadline": "2026-09-03", "start": "2026-08-11"}
    items = normalize.normalize([a, b])
    check("IRIS/NTIS 중복 병합", len(items) == 1, "-> %d건" % len(items))
    check("IRIS 우선 채택", items and items[0]["_meta"]["src"] == "iris")
    check("스키마 필드 완비",
          items and all(k in items[0] for k in
                        ["id", "title", "start", "deadline", "fit", "axes", "flags", "source"]))

    print("\n== 마감일 없을 때 폴백 ==")
    noDate = {"src": "iris", "ancm_id": "1", "title": "인쇄전자 소재 공고", "ministry": "", "agency": "",
              "ancm_no": "", "posted": "", "kind": "", "source": "", "body": "인쇄전자"}
    out = normalize.normalize([noDate])
    check("마감일 추정 플래그", out and "마감일 추정치" in out[0]["flags"],
          "-> %s" % (out[0]["flags"] if out else None))

    print("\n== 레거시 수기 항목 병합 ==")
    import copy
    import tempfile

    from pipeline import build

    tmp = pathlib.Path(tempfile.mkdtemp())
    saved = (build.OPPS, build.ARCHIVE, build.OVERRIDES, build.TEMPLATE, build.OUTPUT)
    build.OPPS = tmp / "opportunities.json"
    build.ARCHIVE = tmp / "archive.json"
    build.OVERRIDES = tmp / "overrides.json"
    build.TEMPLATE = tmp / "template.html"
    build.OUTPUT = tmp / "index.html"
    try:
        legacy = {
            "id": "ai-commercialization",
            "title": "AI 응용제품 신속 상용화 지원사업 2차",
            "ministry": "산업통상부", "agency": "", "category": "산업기술",
            "start": "2026-08-11", "deadline": "2026-09-03",
            "fit": 76, "role": "기업 연계 지원", "axes": {}, "flags": [],
            "summary": "", "rationale": "", "action": "주관 가능 기업 1곳 선별",
            "source": "https://www.iris.go.kr/contents/retrieveBsnsAncmView.do?ancmId=023398",
            "_meta": {"src": "", "legacy": True,
                      "first_seen": "2026-08-01", "crawled_at": "2026-08-01"},
        }
        build.OPPS.write_text(json.dumps([legacy], ensure_ascii=False), encoding="utf-8")

        fresh = copy.deepcopy(items[0])  # iris-023398, 미채점 상태
        merged = build.merge_with_existing([fresh])
        check("레거시 흡수로 1건 유지", len(merged) == 1, "-> %d건" % len(merged))
        check("크롤러 id 채택", merged and merged[0]["id"] == "iris-023398")
        check("수기 fit 승계", merged and merged[0]["fit"] == 76)
        check("수기 action 승계", merged and merged[0]["action"] == "주관 가능 기업 1곳 선별")
        check("curated 고정 플래그", merged and merged[0]["_meta"].get("curated") is True)

        # 다음 실행: 캐시된 LLM 점수가 와도 curated 값이 유지되어야 함
        build.OPPS.write_text(json.dumps(merged, ensure_ascii=False), encoding="utf-8")
        rescored = copy.deepcopy(items[0])
        rescored["fit"] = 55
        rescored["action"] = "LLM이 새로 쓴 액션"
        merged2 = build.merge_with_existing([rescored])
        check("curated 항목은 LLM 재채점이 못 덮음",
              merged2 and merged2[0]["fit"] == 76 and merged2[0]["action"] == "주관 가능 기업 1곳 선별")
    finally:
        build.OPPS, build.ARCHIVE, build.OVERRIDES, build.TEMPLATE, build.OUTPUT = saved

    print("\n" + ("모든 테스트 통과" if not fails else "실패 %d건: %s" % (len(fails), fails)))
    return 0 if not fails else 1


if __name__ == "__main__":
    raise SystemExit(run())
