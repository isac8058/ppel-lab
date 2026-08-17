"""파서 단위 테스트. 실제 사이트 접근 없이 로직만 검증함.

샘플 HTML은 2026-08-14 시점 IRIS 목록 화면의 텍스트 구조를 재현한 것이며,
DOM 형태를 두 가지(href 방식, onclick 방식)로 나누어 폴백 경로까지 확인함.
"""

from crawlers import iris, ntis
from crawlers.common import find_dates, period_from_text
from pipeline import normalize

SAMPLE_HREF = """
<ul class="board-list">
  <li>
    <span class="dept">우주항공청 &gt; 우주항공청</span>
    <strong><a href="/contents/retrieveBsnsAncmView.do?ancmId=023610&amp;ancmPrg=ancmIng">
      2026년도 신규프로젝트 탐색연구 재공고(다중 궤도 위성 기반 우주환경 상시 감시체계 구축 기획연구)</a></strong>
    <div class="info"><em>공고번호 :</em>우주항공청 공고 제2026-0095호
      <em>공고일자 :</em>2026-08-07 <em>공고상태 :</em> 공고접수중 <em>공모유형 :</em>지정공모</div>
    <span class="state">접수중</span>
  </li>
  <li>
    <span class="dept">산업통상부 &gt; 한국산업기술기획평가원</span>
    <strong><a href="/contents/retrieveBsnsAncmView.do?ancmId=023398&amp;ancmPrg=ancmIng">
      AI 응용제품 신속 상용화 지원사업 2차 신규지원 대상과제 공고</a></strong>
    <div class="info"><em>공고번호 :</em>산업통상부 공고 제2026-536호
      <em>공고일자 :</em>2026-08-04 <em>공고상태 :</em> 공고접수중 <em>공모유형 :</em>품목지정공모</div>
    <span class="state">접수중</span>
  </li>
  <li>
    <span class="dept">과학기술정보통신부 &gt; 한국과학기술기획평가원</span>
    <strong><a href="/contents/retrieveBsnsAncmView.do?ancmId=099999&amp;ancmPrg=ancmIng">
      (TEST) KISTEP 통합공고 테스트 입니다.</a></strong>
    <div class="info"><em>공고번호 :</em>IT_2026_001
      <em>공고일자 :</em>2026-07-27 <em>공고상태 :</em> 공고접수중 <em>공모유형 :</em>자유공모</div>
    <span class="state">접수중</span>
  </li>
</ul>
"""

SAMPLE_ONCLICK = """
<ul class="board-list">
  <li>
    <span class="dept">기후에너지환경부 &gt; 한국에너지기술평가원</span>
    <strong><a href="javascript:void(0);" onclick="fn_view('023450');">
      2026년도 2차 에너지수요관리핵심기술개발사업 신규지원대상 연구개발과제 공고</a></strong>
    <div class="info"><em>공고번호 :</em>기후에너지환경부 공고 제2026-719호
      <em>공고일자 :</em>2026-07-24 <em>공고상태 :</em> 공고접수중 <em>공모유형 :</em>품목지정공모</div>
    <span class="state">접수중</span>
  </li>
</ul>
"""

SAMPLE_NTIS = """
<table class="tbl"><tbody>
<tr>
  <td>1</td><td>산업통상부</td>
  <td><a href="/rndgate/eg/un/ra/view.do?roRndUid=1204730">2026년도 첨단소재공정고도화 및 기술역량확보기술개발사업 신규지원 대상과제 공고</a></td>
  <td>2026-08-05</td><td>2026-09-04</td>
</tr>
<tr>
  <td>2</td><td>과학기술정보통신부</td>
  <td><a href="/rndgate/eg/un/ra/view.do?roRndUid=1204731">2026년 한-중국 에너지국제공동RD 신규지원 대상과제 공고</a></td>
  <td>2026-08-01</td><td>2026-08-29</td>
</tr>
</tbody></table>
"""

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

    print("\n== IRIS 목록 파싱 (href 방식) ==")
    recs = iris.parse_list(SAMPLE_HREF)
    for r in recs:
        print("   %s | %s / %s | %s" % (r["ancm_id"], r["ministry"], r["agency"], r["title"][:44]))
    check("항목 2건 추출, TEST 공고 제외", len(recs) == 2, "-> %d건" % len(recs))
    check("ancmId 정확", [r["ancm_id"] for r in recs] == ["023610", "023398"])
    check("부처/전문기관 분리", recs[1]["ministry"] == "산업통상부" and recs[1]["agency"] == "한국산업기술기획평가원")
    check("공고일자 파싱", recs[0]["posted"] == "2026-08-07", "-> %s" % recs[0]["posted"])
    check("상세 URL 생성", recs[0]["source"].endswith("ancmId=023610&ancmPrg=ancmIng"))

    print("\n== IRIS 목록 파싱 (onclick 폴백) ==")
    recs2 = iris.parse_list(SAMPLE_ONCLICK)
    for r in recs2:
        print("   %s | %s" % (r["ancm_id"], r["title"][:50]))
    check("onclick에서 ID 회수", len(recs2) == 1 and recs2[0]["ancm_id"] == "023450")

    print("\n== NTIS 목록 파싱 ==")
    nrecs = ntis.parse_list(SAMPLE_NTIS)
    for r in nrecs:
        print("   %s | %s" % (r["ancm_id"], r["title"][:50]))
    check("행 2건 추출", len(nrecs) == 2)
    check("id 접두어", nrecs[0]["ancm_id"] == "n1204730")

    print("\n== 접수기간 추출 ==")
    start, deadline = period_from_text(DETAIL_BODY)
    check("접수기간 라벨 기준 추출", (start, deadline) == ("2026-08-11", "2026-09-10"),
          "-> %s ~ %s" % (start, deadline))
    check("날짜 정규화", find_dates("2026. 08. 11.")[0] == "2026-08-11")
    check("날짜 중복 제거", find_dates("2026.08.11 ~ 2026.08.11") == ["2026-08-11"])
    check("공고번호에 부처명 접두 허용", recs[0]["ancm_no"] == "우주항공청 공고 제2026-0095호",
          "-> %r" % recs[0]["ancm_no"])

    print("\n== 사전 필터 ==")
    energy = {"title": "2026년도 2차 에너지수요관리핵심기술개발사업", "body": "에너지저장 소재 개발"}
    forest = {"title": "산림 병해충 방제 실증", "body": "산림 방제 약제 살포"}
    check("관련 공고 통과", normalize.passes_prefilter(energy))
    check("무관 공고 차단", not normalize.passes_prefilter(forest))

    print("\n== 정규화와 중복 제거 ==")
    a = dict(recs[1], body="AI 응용제품 센서 상용화", deadline="2026-09-03", start="2026-08-11")
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
    import json
    import pathlib
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
