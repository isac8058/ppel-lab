"""Claude API로 공고별 6축 적합도와 판단 문구를 생성함.

같은 공고를 두 번 채점하지 않도록 캐시를 둠. 캐시 키는 공고 id.
API 키가 없으면 채점을 건너뛰고 미분류 상태로 통과시킴.
"""

import json
import os
import pathlib
import re
import time

import requests
import yaml

ROOT = pathlib.Path(__file__).resolve().parent.parent
PROFILE = yaml.safe_load((ROOT / "config" / "profile.yml").read_text(encoding="utf-8"))
CACHE_PATH = ROOT / "data" / "score_cache.json"

API_URL = "https://api.anthropic.com/v1/messages"
MODEL = os.environ.get("RADAR_MODEL", "claude-sonnet-5")

CATEGORIES = ["국제공동연구", "산업기술", "의료기기", "소재·부품", "에너지",
              "기초연구", "인력·인프라", "지역·기업연계"]

SYSTEM = """너는 대학 연구실의 정부 R&D 공고 선별 담당이다.
공고 하나를 받아 연구실 역량과의 적합도를 판정하고 JSON만 출력한다.
설명, 서론, 코드펜스를 절대 붙이지 않는다.

판정 원칙:
- 낙관하지 않는다. 지원 자격에서 탈락하면 축 점수가 높아도 fit을 크게 낮춘다.
- 기업 주관이 필수인 과제, 연구비 없는 연수 프로그램, 지역이 다른 과제는 flags에 반드시 적는다.
- action은 오늘 실제로 할 수 있는 한 가지 행동만 쓴다. 30자 이내.
- rationale은 왜 맞는지 또는 왜 애매한지를 한 문장으로 쓴다. 60자 이내.
- summary는 공고 자체의 내용 요약이다. 45자 이내.
- 문장 끝은 함으로 끝낸다. 따옴표와 줄표는 쓰지 않는다."""

USER_TMPL = """[연구실 역량]
{capabilities}

[역량 축]
{axes}

[분류 후보]
{categories}

[공고]
제목: {title}
소관: {ministry} / {agency}
접수: {start} ~ {deadline}
본문 발췌:
{body}

아래 JSON 스키마로만 답한다.
{{"fit": 0-100 정수,
 "category": 분류 후보 중 하나,
 "role": 연구책임자 또는 공동연구기관 또는 참여연구원 또는 기업 연계 지원 또는 기획 참여 중 하나,
 "axes": {{축이름: 0-100 정수, ... 6개 모두}},
 "flags": [탈락 위험이나 전제조건 문자열, 없으면 빈 배열],
 "summary": "...",
 "rationale": "...",
 "action": "..."}}"""


def _load_cache():
    if CACHE_PATH.exists():
        try:
            return json.loads(CACHE_PATH.read_text(encoding="utf-8"))
        except Exception:
            return {}
    return {}


def _save_cache(cache):
    CACHE_PATH.parent.mkdir(parents=True, exist_ok=True)
    CACHE_PATH.write_text(json.dumps(cache, ensure_ascii=False, indent=1), encoding="utf-8")


def _extract_json(text):
    text = re.sub(r"^```(?:json)?|```$", "", text.strip(), flags=re.M).strip()
    start, end = text.find("{"), text.rfind("}")
    if start == -1 or end == -1:
        return None
    try:
        return json.loads(text[start:end + 1])
    except Exception:
        return None


def _output_schema():
    """축 이름을 profile.yml에서 읽어 채점 JSON 스키마를 구성."""
    axes_props = {axis: {"type": "integer"} for axis in PROFILE["axes"]}
    return {
        "type": "object",
        "properties": {
            "fit": {"type": "integer"},
            "category": {"type": "string", "enum": CATEGORIES + ["미분류"]},
            "role": {"type": "string"},
            "axes": {
                "type": "object",
                "properties": axes_props,
                "required": list(axes_props),
                "additionalProperties": False,
            },
            "flags": {"type": "array", "items": {"type": "string"}},
            "summary": {"type": "string"},
            "rationale": {"type": "string"},
            "action": {"type": "string"},
        },
        "required": ["fit", "category", "role", "axes", "flags",
                     "summary", "rationale", "action"],
        "additionalProperties": False,
    }


def _call(api_key, item):
    payload = {
        "model": MODEL,
        "max_tokens": 1500,
        # 채점은 단순 구조화 작업이라 사고 토큰을 아낌. 켜두면 max_tokens를 사고가 잠식함
        "thinking": {"type": "disabled"},
        "output_config": {"format": {"type": "json_schema", "schema": _output_schema()}},
        "system": SYSTEM,
        "messages": [{
            "role": "user",
            "content": USER_TMPL.format(
                capabilities=PROFILE["capabilities"].strip(),
                axes=", ".join(PROFILE["axes"]),
                categories=", ".join(CATEGORIES),
                title=item["title"],
                ministry=item["ministry"],
                agency=item["agency"],
                start=item["start"],
                deadline=item["deadline"],
                body=item["_meta"].get("body", "")[:2500],
            ),
        }],
    }
    headers = {
        "x-api-key": api_key,
        "anthropic-version": "2023-06-01",
        "content-type": "application/json",
    }
    for attempt in range(3):
        try:
            r = requests.post(API_URL, headers=headers, json=payload, timeout=90)
            if r.status_code == 200:
                blocks = r.json().get("content", [])
                text = "".join(b.get("text", "") for b in blocks if b.get("type") == "text")
                parsed = _extract_json(text)
                if parsed:
                    return parsed
            elif r.status_code in (429, 529):
                time.sleep(6 * (attempt + 1))
                continue
            else:
                print("  [score] HTTP %s %s" % (r.status_code, r.text[:160]))
        except Exception as exc:
            print("  [score] %r" % exc)
        time.sleep(3 * (attempt + 1))
    return None


def _apply(item, result):
    axes = {}
    for axis in PROFILE["axes"]:
        try:
            axes[axis] = max(0, min(100, int(result.get("axes", {}).get(axis, 0))))
        except Exception:
            axes[axis] = 0
    item["fit"] = max(0, min(100, int(result.get("fit", 0) or 0)))
    item["category"] = result.get("category") or "미분류"
    item["role"] = result.get("role") or "미정"
    item["axes"] = axes
    incoming = [str(f) for f in (result.get("flags") or [])]
    item["flags"] = list(dict.fromkeys(item.get("flags", []) + incoming))
    item["summary"] = result.get("summary") or ""
    item["rationale"] = result.get("rationale") or ""
    item["action"] = result.get("action") or ""
    item["_meta"]["scored_at"] = time.strftime("%Y-%m-%d")
    return item


def score_all(items, limit=40):
    api_key = os.environ.get("ANTHROPIC_API_KEY", "").strip()
    cache = _load_cache()
    if not api_key:
        print("[score] ANTHROPIC_API_KEY 없음. 채점 생략하고 캐시만 적용함")

    calls = 0
    for item in items:
        cached = cache.get(item["id"])
        if cached:
            _apply(item, cached)
            continue
        if not api_key or calls >= limit:
            continue
        result = _call(api_key, item)
        calls += 1
        if result:
            cache[item["id"]] = result
            _apply(item, result)
            print("  [score] %3d  %s" % (item["fit"], item["title"][:44]))
        else:
            print("  [score] 실패  %s" % item["title"][:44])
        time.sleep(1.0)

    _save_cache(cache)
    print("[score] 신규 채점 %d건, 캐시 %d건" % (calls, len(cache)))
    return items
