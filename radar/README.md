# 정부 R&D 공고 레이더 수집 파이프라인

IRIS와 NTIS 공고를 매일 자동 수집하고, 연구실 역량 기준으로 6축 채점한 뒤,
레이더 HTML을 다시 빌드함. 수기로 조정한 값은 자동 수집이 절대 덮지 않음.

이 디렉토리는 ppel-lab 레포의 하위 프로젝트이며, 빌드 결과는
`radar/index.html` 로 생성되어 main 브랜치 커밋과 함께
https://isac8058.github.io/ppel-lab/radar/ 로 배포됨.
레포 루트의 `index.html`(연구실 홈페이지)은 건드리지 않음.

크롤러 도입 전에 수기로 큐레이션한 8건은 `data/opportunities.json` 에
시드로 들어 있음(`_meta.legacy`). 크롤러가 같은 공고를 수집하면 source의
ancmId 또는 제목으로 매칭해 수기 판단값(fit, action 등)을 물려주고
레거시 항목을 흡수하므로 중복 노출되지 않고, 물려받은 값은 `_meta.curated`
로 고정되어 이후 LLM 채점이 덮지 않음.

## 확인된 실제 구조 (2026-08-17)

GitHub Actions 진단 실행이 저장한 원본 HTML로 확정한 구조.
`tests/fixtures/` 에 실제 목록 발췌를 넣어 회귀 테스트로 고정함.

**IRIS** — 목록 화면은 검색 폼 + 1페이지 서버 렌더링을 담은 셸이고,
목록 데이터는 별도 JSON API가 제공함.

- 목록 API: `POST /contents/retrieveBsnsAncmBtinSituList.do` (폼 필드 그대로 전송)
- 응답 키: `listBsnsAncmBtinSitu[]` 안에 `ancmId`, `ancmTl`, `blngGovdSeNm`,
  `sorgnNm`, `ancmNo`, `ancmDe`, `pbofrTpSeNmLst`, 페이징은 `paginationInfo`
- 셸의 상세 링크: `f_bsnsAncmBtinSituListForm_view('023457','ancmIng')`
- 크롤러는 API를 1차 경로로 쓰고, 실패하면 셸 HTML 파싱으로 폴백함

**NTIS** — 목록은 서버 렌더링 표이고 셀에 `data-title` 이 붙음
(순번/현황/공고명/부처명/접수일/마감일/D-day). 상세 링크는
`fn_view('1268336')` onclick으로만 uid를 넘기며, 상세는 폼 POST로 열림.
목록에 접수일·마감일이 있어 상세 조회는 채점용 본문 확보 용도임.

구조가 또 바뀌면 진단 모드로 원본을 받아 확인함.

```bash
cd radar
pip install -r requirements.txt
python run.py --probe
```

출력에서 `[iris probe] API 총 N건`과 `수집 레코드: N건`이 0이 아닌지 확인함.
0이면 `data/raw/`(Actions 아티팩트)에 저장된 원본 HTML을 열어 실제 구조를
확인한 뒤 `crawlers/iris.py` 의 API 키 이름이나 폴백 셀렉터를 조정함.

진단이 정상이면 채점 없이 한 번 더 돌려 수집 품질을 봄.

```bash
python run.py --no-score
```

## 정상 운영

```bash
export ANTHROPIC_API_KEY=sk-ant-...
python run.py
```

실행 순서는 수집, 사전 필터, 중복 제거, 채점, 병합, 아카이브, HTML 빌드임.

## 구조

```
run.py                    엔트리포인트
crawlers/common.py        HTTP 세션, 재시도, 날짜 파싱, KST 기준일
crawlers/iris.py          IRIS 목록 JSON API + 셸 폴백, 상세
crawlers/ntis.py          NTIS 국가R&D통합공고 표 파싱, 상세
pipeline/normalize.py     스키마 정규화, 사전 필터, 중복 제거
pipeline/score.py         Claude API 6축 채점, 캐시
pipeline/build.py         수기 조정 병합, 아카이브, HTML 빌드
config/profile.yml        연구실 역량과 필터 키워드. 여기만 고치면 됨
template.html             레이더 HTML 원본
index.html                빌드 결과. 이것을 배포함
data/opportunities.json   활성 공고
data/archive.json         마감 공고 누적. 차년도 재도전 근거
data/overrides.json       수기 조정. 자동 수집보다 우선함
data/score_cache.json     채점 캐시. 같은 공고를 두 번 채점하지 않음
```

## 수기 조정이 자동 수집을 이기는 구조

LLM 채점은 보조 수단이며 최종 판단은 사람이 함.
`data/overrides.json` 에 공고 id를 키로 두고 고칠 필드만 적으면
이후 모든 실행에서 그 값이 유지됨.

```json
{
  "iris-023398": {
    "fit": 82,
    "role": "공동연구기관",
    "internalDeadline": "2026-08-27",
    "action": "주관 가능 기업 1곳 선별"
  }
}
```

보호 필드는 `fit`, `axes`, `flags`, `role`, `category`, `summary`,
`rationale`, `action`, `start`, `deadline`, `internalDeadline` 임.

## 비용 관리

`config/profile.yml` 의 `include_keywords` 로 1차 걸러낸 공고만 LLM에 보냄.
IRIS 접수중 20건대에서 관련 공고는 보통 5건 내외이며,
한 번 채점한 공고는 캐시되므로 매일 실행해도 신규분만 호출됨.
`--limit` 으로 1회 채점 상한을 둘 수 있음.

## GitHub Actions

레포 루트의 `.github/workflows/radar.yml` 이 매일 07:00 KST에 실행함.
수집 결과를 main에 커밋하면 기존 GitHub Pages 배포(main 브랜치 기준)가
그대로 반영하므로 Pages 설정을 바꿀 필요 없음. 워크플로 파일 안의
`permissions: contents: write` 로 커밋 권한도 해결되므로 저장소 설정 변경 불필요.

준비 사항
- 저장소 Settings > Secrets and variables > Actions 에 `ANTHROPIC_API_KEY` 등록 (이것 하나면 됨)

수동 실행 시 Run workflow 화면에서 진단 모드와 채점 생략을 선택할 수 있음.
진단 모드는 커밋을 건너뜀. 채점 모델은 워크플로의 `RADAR_MODEL` 환경변수로
바꿀 수 있음(기본 claude-sonnet-5).

## 안전장치

- 수집 결과가 0건이면 기존 데이터를 건드리지 않고 종료함
- 한쪽 소스가 실패해도 다른 소스는 계속 수집함
- 목록에서 사라진 공고도 마감 전이면 유지함
- 마감일을 못 뽑은 공고는 30일 뒤로 추정하고 마감일 추정치 플래그를 붙임
- 원본 HTML은 7일간 아티팩트로 보관되어 구조 변경 진단에 쓰임

## 테스트

```bash
python test_parsers.py
```

네트워크 없이 파서 로직만 검증함. 실제 원본 HTML 발췌(tests/fixtures/)로
IRIS JSON API 파싱, IRIS 셸 폴백 파싱, NTIS 표 파싱, 접수기간 추출,
사전 필터, 중복 제거, 레거시 수기 항목 병합, 마감일 폴백을 확인함.

## 아직 붙지 않은 소스

전북대 산학협력단 공지사항, 전북테크노파크, 한국탄소산업진흥원,
전북국방벤처센터는 게시판 URL이 확정되지 않아 제외되어 있음.
전북대 R&D공고 페이지는 NTIS 미러라 중복이므로 의도적으로 넣지 않음.
