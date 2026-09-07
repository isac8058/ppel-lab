# -*- coding: utf-8 -*-
"""
v4 스토리보드 빌더.

샷 리스트(SHOTS)와 자막 큐(CUES)를 한 곳에 두고
  - storyboard.html : 단일 파일 스토리보드(14컷 스케치, 30초 타임라인, 하단 자막 패널 플레이어)
  - shotlist.json   : 같은 데이터의 기계 판독용 사본
을 생성한다.

실행:  python Video/research/v4/tools/build_storyboard.py [--poc path/to/poc.png]
"""
import argparse
import base64
import io
import json
import math
import os
import random
from datetime import date

HERE = os.path.dirname(os.path.abspath(__file__))
OUT_DIR = os.path.dirname(HERE)

FPS = 24
DURATION = 30.0

# ----------------------------------------------------------------------------
# 데이터: 샷 리스트
# ----------------------------------------------------------------------------
SHOTS = [
    dict(n=1, t0=0.0, t1=1.5, place="벚나무 길, 지면", title="정적",
         action="초매크로. 꽃잎 한 장이 슬로모로 낙하해 지면의 꽃잎 카펫에 닿는다. 배경은 분홍 보케.",
         camera="50 mm f/4, 카메라 높이 12 mm, 살짝 올려다봄",
         sound="바람, 피아노 한 음", caption="", engine="Cycles", act=1,
         blender="낙하 꽃잎은 키프레임 + 노이즈 모디파이어(또는 클로스), 보케는 발광 구, 카펫은 지오메트리 노드 산포",
         hook="정적의 아름다움", sketch="s1"),
    dict(n=2, t0=1.5, t1=2.1, place="동일", title="파열",
         action="빗자루 머리가 왼쪽에서 렌즈로 돌진, 짚이 화면을 채우고 꽃잎이 튄다. 카메라도 밀려 흔들린다.",
         camera="같은 매크로 카메라 + 셰이크", sound="거친 쓸림. 1.8초부터 화면 밖 절규 잠깐만요!",
         caption="잠깐만요! (1.8~3.0)", engine="EEVEE", act=1,
         blender="꽃잎 200장 리지드 바디(컨벡스 헐) + 패시브 콜라이더 빗자루, 모션 블러 셔터 0.6",
         hook="패턴 인터럽트", sketch="s2"),
    dict(n=3, t0=2.1, t1=4.6, place="동일", title="다이빙 낚아채기",
         action="꽃잎 더미가 쓰레받기 턱으로 밀려가는 순간 오른쪽에서 흰 소매와 파란 장갑 손이 프레임 인. 2.8~4.0 슬로모: 손가락이 턱 1 cm 위에서 꽃잎을 움켜쥔다. 앞쪽 왼편엔 멈춘 작업화와 빗자루.",
         camera="로우 와이드 망원 85 mm", sound="심장박동 한 번, 슬로모 스팅, 정적",
         caption="(잠깐만요! 유지)", engine="EEVEE", act=1,
         blender="리지드 바디 베이크 → 키프레임 변환, NLA에서 2.8~4.0 구간 5배 스케일. 소매 클로스 시뮬. 슬로모 구간 모션 블러 오프",
         hook="작은 것에 거는 큰 헌신 · 포스터 프레임 3.4초", sketch="s3"),
    dict(n=4, t0=4.6, t1=5.6, place="동일", title="착지",
         action="실시간 복귀. 주먹이 보도 위를 미끄러져 카메라 앞을 지나고 흙먼지가 퍼진다. 쓰레받기가 덜컹.",
         camera="지면 고정, 주먹이 렌즈 앞을 스침", sound="쿵, 드르륵, 덜컹", caption="", engine="EEVEE", act=1,
         blender="먼지는 파티클 + 볼륨 퍼프, 속도 램프", hook=None, sketch="s4"),
    dict(n=5, t0=5.6, t1=8.4, place="동일", title="감정",
         action="쓰레받기 위 클로즈업. 점박이 장갑이 손잡이를 쥐고, 파란 장갑이 펼쳐지며 꽃잎 두 장. 핀셋이 한 장을 태양 쪽으로 들어올린다: 잎맥이 빛나는 초매크로.",
         camera="매크로, 역광", sound="속삭임 이거… 최상급이에요.", caption="이거… 최상급이에요. (5.8~8.2)",
         engine="Cycles", act=1,
         blender="반투명 꽃잎 재질, 브러시드 메탈 핀셋, 손 리그 포즈 3개", hook="이건 AI 생성이 아니다 신호", sketch="s5"),
    dict(n=6, t0=8.4, t1=10.0, place="길 → 실험실", title="봉인",
         action="꽃잎이 지퍼백에 떨어지고 지퍼 슬라이더가 화면을 가로지르며 장면을 닦아낸다. 지나간 자리는 어두운 실험실 벤치.",
         camera="정면, 슬라이더가 와이프 마스크", sound="지퍼 지익, 실험실 웅", caption="", engine="EEVEE", act=2,
         blender="두 샷을 렌더한 뒤 컴포지터에서 슬라이더 위치 마스크로 알파 오버", hook=None, sketch="s6"),
    dict(n=7, t0=10.0, t1=14.0, place="실험실", title="조립",
         action="검은 벤치, 링라이트. 분해도로 떠 있는 층들 사이로 핀셋이 꽃잎을 아래 전극 위에 놓는다. 층이 하나씩 내려와 닫히고 완성 소자에 리드 두 줄.",
         camera="느린 궤도(Follow Path)", sound="층마다 부드러운 클릭(박자)", caption="버려질 꽃잎을 센서의 한 층으로. (10.5~13.5)",
         engine="EEVEE", act=2, blender="층 오브젝트 키프레임 + 이징, 궤도 카메라", hook="조립 ASMR", sketch="s7"),
    dict(n=8, t0=14.0, t1=16.5, place="실험실", title="연결",
         action="리드가 벤치톱 계측기로, 계측기에서 콘센트로 가는 전원선이 또렷히 보인다. 화면은 평평한 선. 장갑 손가락이 내려와 소자 위에서 멈추고 미세하게 떨린다.",
         camera="벤치 높이 측면", sound="음악이 한 음으로 멈춘다", caption="", engine="EEVEE", act=2,
         blender="계측기 화면은 파형 PNG 720장 이미지 시퀀스(글자 없음), 손가락 떨림 노이즈 모디파이어", hook=None, sketch="s8"),
    dict(n=9, t0=16.5, t1=18.5, place="실험실", title="한 번 탭",
         action="손끝이 닿는 순간 소자 단면으로 컷: 꽃잎 층이 위층과 닿고 떨어진다. 리드를 따라 빛 펄스가 흐르고 화면에 양음 이상성 스파이크 하나.",
         camera="단면 매크로 → 화면", sound="톡 → 삡", caption="", engine="EEVEE", act=3,
         blender="단면 컷어웨이 모델, 접촉·분리 키프레임, 리드 이미션 그라데이션", hook="페이오프", sketch="s9"),
    dict(n=10, t0=18.5, t1=21.0, place="실험실", title="두 번 탭",
         action="손가락이 0.25초 간격으로 두 번 두드린다. 스파이크 둘. 파란 장갑이 화면 밖으로 확 빠진다(주먹 불끈).",
         camera="리버스 앵글", sound="톡톡 → 삡삡, 됐다!", caption="됐다! (19.6~21.0)", engine="EEVEE", act=3,
         blender="같은 세트", hook=None, sketch="s10"),
    dict(n=11, t0=21.0, t1=24.5, place="실험실", title="분류",
         action="화면의 파형이 빛나는 리본이 되어 공중으로 떠오르고, 점들로 흩어져 두 무리로 모인다. 사이에 부드러운 경계면. 뒤로 꽃잎이 흘러 지나간다.",
         camera="화면에서 공중으로 틸트 업", sound="유리질 아르페지오",
         caption="한 번·두 번 탭의 신호를 머신러닝으로 구별합니다. (21.0~25.0, 무대사)", engine="EEVEE", act=3,
         blender="지오메트리 노드: 커브 → 포인트, 위치 믹스 팩터 키프레임, 블룸", hook=None, sketch="s11"),
    dict(n=12, t0=24.5, t1=27.5, place="실험실", title="재회",
         action="문이 열려 빛이 벤치를 가로지른다. 점박이 장갑이 흠 없는 꽃잎이 소복한 긴 손잡이 쓰레받기를 벤치 위로 밀어 넣는다. 파란 장갑 두 손이 공손히 받는다.",
         camera="벤치 높이, 문 쪽에서 빛", sound="문 끼익, 코믹 바순", caption="", engine="EEVEE", act=3,
         blender="에어리어 라이트 키프레임 라이트 스윕, 쓰레받기 위 꽃잎 지오메트리 노드 산포", hook="콜백과 관계 반전", sketch="s12"),
    dict(n=13, t0=27.5, t1=29.0, place="실험실", title="정리",
         action="벤치 와이드. 파란 장갑과 점박이 장갑이 나란히 핀셋으로 꽃잎을 고른다. 28.0부터 화면이 왼쪽으로 줄어들고 오른쪽에 논문 카드 패널.",
         camera="와이드 고정", sound="음악 해소", caption="논문 보기 · PPEL+ (28.0~30.0)", engine="FFmpeg", act=4,
         blender="카드 패널은 FFmpeg 합성(v3 방식)", hook=None, sketch="s13"),
    dict(n=14, t0=29.0, t1=30.0, place="카드", title="엔드 카드",
         action="From petals to signals. Nano Energy 2026, DOI 10.1016/j.nanoen.2025.111687",
         camera="정지", sound="페이드 아웃", caption="(계속)", engine="FFmpeg", act=4,
         blender="v3 엔드 카드 재사용", hook=None, sketch="s14"),
]

CUES = [
    dict(start=1.8, end=3.0, ko="잠깐만요!", en="WAIT!", kind="dialogue"),
    dict(start=5.8, end=8.2, ko="이거… 최상급이에요.", en="These… are top grade.", kind="dialogue"),
    dict(start=10.5, end=13.5, ko="버려질 꽃잎을 센서의 한 층으로.", en="Discarded petals become a layer in a sensor.", kind="science"),
    dict(start=19.6, end=21.0, ko="됐다!", en="It works!", kind="dialogue"),
    dict(start=21.0, end=25.0, ko="한 번·두 번 탭의 신호를 머신러닝으로 구별합니다.",
         en="Machine learning distinguishes single- and double-tap signals.", kind="science"),
    dict(start=28.0, end=30.0, ko="논문 보기 · PPEL+", en="Read the paper · PPEL+", kind="card"),
]

ACTS = [
    dict(n=1, name="위기", t0=0.0, t1=8.4, color="#E9648F"),
    dict(n=2, name="변신", t0=8.4, t1=16.5, color="#1E3AFF"),
    dict(n=3, name="페이오프", t0=16.5, t1=27.5, color="#00B79C"),
    dict(n=4, name="카드", t0=27.5, t1=30.0, color="#5B6478"),
]

SOUND = [
    (0.0, "바람 + 피아노 한 음"), (1.5, "빗자루 쓸림(첫 큰 소리)"), (1.8, "잠깐만요!"),
    (2.8, "슬로모 스웰"), (4.6, "쿵, 드르륵"), (5.8, "속삭임"), (8.4, "지퍼"),
    (10.0, "피치카토 + 클릭 4회"), (14.0, "한 음 정지"), (16.5, "톡 → 삡"),
    (18.5, "톡톡 → 삡삡"), (19.6, "됐다!"), (21.0, "유리질 아르페지오"),
    (24.5, "문 끼익, 바순"), (27.5, "해소, 페이드"),
]

# ----------------------------------------------------------------------------
# SVG 스케치 프리미티브 (viewBox 320x180)
# ----------------------------------------------------------------------------
PINK = "#F2B8C9"
PINK_D = "#E9648F"
GLOVE = "#2F7BE0"
WORK = "#F1E6C8"
DOT = "#D93B3B"
STRAW = "#C9A25E"
METAL = "#A6B0BE"
LAB = "#0E1525"
CYAN = "#00E6C6"
BLUE = "#1E3AFF"


def petal(x, y, rot=0, s=1.0, fill=PINK, stroke=PINK_D, op=1.0):
    return (f'<path d="M0,0 C-6,-4 -7,-12 -3,-16 L0,-13.5 L3,-16 C7,-12 6,-4 0,0 Z" '
            f'transform="translate({x},{y}) rotate({rot}) scale({s})" fill="{fill}" stroke="{stroke}" '
            f'stroke-width="{0.8 / max(s, 0.3):.2f}" opacity="{op}"/>')


def petals_random(n, x0, x1, y0, y1, seed, smin=0.6, smax=1.1, op=1.0):
    rnd = random.Random(seed)
    return "".join(petal(rnd.uniform(x0, x1), rnd.uniform(y0, y1), rnd.uniform(0, 360),
                         rnd.uniform(smin, smax), op=op) for _ in range(n))


def bokeh(seed=3, n=14):
    rnd = random.Random(seed)
    out = []
    for _ in range(n):
        r = rnd.uniform(8, 26)
        out.append(f'<circle cx="{rnd.uniform(0, 320):.0f}" cy="{rnd.uniform(0, 110):.0f}" r="{r:.0f}" '
                   f'fill="{PINK if rnd.random() < 0.7 else "#FFF3F6"}" opacity="{rnd.uniform(0.25, 0.55):.2f}"/>')
    return "".join(out)


def sky(top="#FBE7EE", bottom="#F6C9D6"):
    return (f'<defs><linearGradient id="skyg" x1="0" y1="0" x2="0" y2="1">'
            f'<stop offset="0" stop-color="{top}"/><stop offset="1" stop-color="{bottom}"/></linearGradient></defs>'
            f'<rect width="320" height="180" fill="url(#skyg)"/>')


def ground(y=125, color="#6F6A63"):
    return f'<rect x="0" y="{y}" width="320" height="{180 - y}" fill="{color}"/>'


def broom(x, y, angle=-35, spread=40, n=18, scale=1.0):
    rnd = random.Random(11)
    lines = []
    for i in range(n):
        dx = -spread / 2 + spread * i / (n - 1) + rnd.uniform(-2, 2)
        lines.append(f'<line x1="{dx:.1f}" y1="0" x2="{dx * 1.25:.1f}" y2="{55 + rnd.uniform(-5, 5):.1f}" '
                     f'stroke="{STRAW}" stroke-width="2.2" stroke-linecap="round"/>')
    return (f'<g transform="translate({x},{y}) rotate({angle}) scale({scale})">'
            f'<line x1="0" y1="-140" x2="0" y2="0" stroke="#8B6B3E" stroke-width="7" stroke-linecap="round"/>'
            f'<rect x="-{spread / 2 + 4}" y="-8" width="{spread + 8}" height="14" rx="4" fill="#7A5A33"/>'
            + "".join(lines) + '</g>')


def dustpan(x, y, scale=1.0, flip=False):
    sx = -1 if flip else 1
    return (f'<g transform="translate({x},{y}) scale({sx * scale},{scale})">'
            f'<polygon points="0,0 70,0 62,-26 8,-26" fill="{METAL}" stroke="#6B7684" stroke-width="1.5"/>'
            f'<polygon points="8,-26 62,-26 56,-40 14,-40" fill="#C3CBD6" stroke="#6B7684" stroke-width="1.5"/>'
            f'<line x1="35" y1="-40" x2="35" y2="-150" stroke="#6B7684" stroke-width="5" stroke-linecap="round"/></g>')


def glove(x, y, rot=0, scale=1.0, color=GLOVE, sleeve="#FFFFFF", dots=False, open_hand=False):
    rnd = random.Random(5)
    fingers = []
    for i in range(4):
        fx = -14 + i * 9.5
        fl = 26 if open_hand else 14
        fingers.append(f'<rect x="{fx}" y="{-fl}" width="8" height="{fl + 8}" rx="4" fill="{color}" stroke="#1B2A44" stroke-width="0.8"/>')
    thumb = f'<rect x="-30" y="2" width="9" height="20" rx="4.5" transform="rotate(-35 -26 2)" fill="{color}" stroke="#1B2A44" stroke-width="0.8"/>'
    palm = f'<rect x="-20" y="0" width="42" height="34" rx="9" fill="{color}" stroke="#1B2A44" stroke-width="0.8"/>'
    sl = f'<rect x="-24" y="30" width="50" height="70" rx="6" fill="{sleeve}" stroke="#B8C0CC" stroke-width="0.8"/>'
    d = ""
    if dots:
        d = "".join(f'<circle cx="{rnd.uniform(-16, 18):.1f}" cy="{rnd.uniform(4, 30):.1f}" r="1.6" fill="{DOT}"/>' for _ in range(14))
    return f'<g transform="translate({x},{y}) rotate({rot}) scale({scale})">{sl}{palm}{thumb}{"".join(fingers)}{d}</g>'


def tweezers(x, y, rot=0, scale=1.0):
    return (f'<g transform="translate({x},{y}) rotate({rot}) scale({scale})">'
            f'<path d="M0,0 L-5,-70 L-9,-74" fill="none" stroke="{METAL}" stroke-width="3" stroke-linecap="round"/>'
            f'<path d="M0,0 L5,-70 L9,-74" fill="none" stroke="{METAL}" stroke-width="3" stroke-linecap="round"/></g>')


def lab_bg(light_sweep=False):
    s = f'<rect width="320" height="180" fill="{LAB}"/>'
    s += '<rect x="0" y="120" width="320" height="60" fill="#151D2E"/>'
    s += '<line x1="0" y1="120" x2="320" y2="120" stroke="#2A3550" stroke-width="1"/>'
    if light_sweep:
        s += ('<polygon points="0,180 0,40 120,120 60,180" fill="#FFE9B5" opacity="0.22"/>')
    return s


def spike_path(x, y, amp=18, w=12):
    return f'M{x},{y} L{x + w * 0.3:.1f},{y - amp} L{x + w * 0.65:.1f},{y + amp * 0.65:.1f} L{x + w},{y}'


def instrument(x, y, trace="flat", scale=1.0, with_cable=True):
    sx, sy = 92, 96
    tr = f'M8,54 L{sx - 8},54'
    if trace == "one":
        tr = f'M8,54 L34,54 {spike_path(34, 54)} L{sx - 8},54'
    elif trace == "two":
        tr = f'M8,54 L26,54 {spike_path(26, 54)} L44,54 {spike_path(44, 54)} L{sx - 8},54'
    cable = ""
    if with_cable:
        cable = (f'<path d="M{sx / 2},{sy} C{sx / 2},{sy + 30} {sx + 60},{sy + 10} {sx + 70},{sy + 40}" fill="none" stroke="#333B4D" stroke-width="3"/>'
                 f'<rect x="{sx + 64}" y="{sy + 36}" width="14" height="18" rx="2" fill="#D9DEE7"/>'
                 f'<circle cx="{sx + 68}" cy="{sy + 45}" r="1.6" fill="#333"/><circle cx="{sx + 74}" cy="{sy + 45}" r="1.6" fill="#333"/>')
    return (f'<g transform="translate({x},{y}) scale({scale})">{cable}'
            f'<rect x="0" y="0" width="{sx}" height="{sy}" rx="6" fill="#2B3446" stroke="#3E4A63" stroke-width="1.5"/>'
            f'<rect x="8" y="10" width="{sx - 16}" height="72" rx="3" fill="#0A1A18"/>'
            f'<path d="{tr}" fill="none" stroke="{CYAN}" stroke-width="2" stroke-linejoin="round"/>'
            f'<circle cx="{sx - 14}" cy="{sy - 8}" r="3" fill="#00B79C"/></g>')


def stack(x, y, exploded=True, scale=1.0, cut=False):
    layers = [("#D7E3F2", 0.75), ("#E3B04B", 1.0), (PINK, 1.0), ("#C3CBD6", 0.9), ("#D7E3F2", 0.75)]
    gap = 22 if exploded else 6
    out = []
    for i, (c, op) in enumerate(layers):
        yy = -i * gap
        w = 90 if not cut else 60
        out.append(f'<polygon points="0,{yy} {w},{yy} {w + 30},{yy - 16} 30,{yy - 16}" fill="{c}" opacity="{op}" stroke="#5B6478" stroke-width="0.8"/>')
        if i == 2:
            out.append(petal(w / 2 + 12, yy - 4, 20, 0.8))
    leads = f'<line x1="{90 if not cut else 60}" y1="-10" x2="140" y2="-10" stroke="{METAL}" stroke-width="1.5"/><line x1="{90 if not cut else 60}" y1="-4" x2="140" y2="-4" stroke="{METAL}" stroke-width="1.5"/>'
    return f'<g transform="translate({x},{y}) scale({scale})">{"".join(out)}{leads}</g>'


def zipbag(x, y, slider_x=0.5):
    return (f'<g transform="translate({x},{y})">'
            f'<rect x="0" y="0" width="110" height="130" rx="6" fill="#FFFFFF" opacity="0.55" stroke="#B8C0CC" stroke-width="1.2"/>'
            f'<line x1="0" y1="12" x2="110" y2="12" stroke="#8892A6" stroke-width="3"/>'
            f'<rect x="{110 * slider_x - 6}" y="5" width="12" height="14" rx="2" fill="#5B6478"/>'
            + petal(55, 80, 15, 1.4) + '</g>')


def clusters():
    rnd = random.Random(21)
    out = []
    for _ in range(26):
        out.append(f'<circle cx="{95 + rnd.gauss(0, 18):.1f}" cy="{80 + rnd.gauss(0, 14):.1f}" r="2.4" fill="{CYAN}" opacity="0.9"/>')
    for _ in range(26):
        out.append(f'<circle cx="{225 + rnd.gauss(0, 18):.1f}" cy="{95 + rnd.gauss(0, 14):.1f}" r="2.4" fill="#7FA0FF" opacity="0.9"/>')
    out.append('<line x1="160" y1="20" x2="160" y2="160" stroke="#FFFFFF" stroke-width="1" stroke-dasharray="4 4" opacity="0.5"/>')
    return "".join(out)


def caption_mark(text):
    return (f'<rect x="0" y="160" width="320" height="20" fill="#172226"/>'
            f'<text x="160" y="174" text-anchor="middle" font-size="9" fill="#FFFFFF" font-family="system-ui,sans-serif">{text}</text>')


def sketch(key):
    if key == "s1":
        return (sky() + bokeh(3) + ground(128, "#4A4744") + petals_random(26, -10, 330, 122, 150, 1, 0.7, 1.2, 0.85)
                + '<circle cx="250" cy="42" r="26" fill="#FFF7E6" opacity="0.8"/>'
                + petal(150, 96, 35, 2.6, PINK, PINK_D))
    if key == "s2":
        return (sky() + bokeh(4) + ground(128, "#4A4744") + petals_random(24, -10, 330, 122, 150, 2, 0.7, 1.2, 0.85)
                + broom(70, 60, -40, 90, 30, 1.6)
                + petals_random(12, 90, 200, 40, 120, 9, 0.8, 1.4)
                + '<line x1="200" y1="60" x2="250" y2="60" stroke="#FFFFFF" stroke-width="2" opacity="0.7"/>'
                + '<line x1="190" y1="80" x2="260" y2="80" stroke="#FFFFFF" stroke-width="2" opacity="0.7"/>')
    if key == "s3":
        return (sky() + bokeh(5, 10) + ground(130, "#4A4744") + petals_random(20, -10, 330, 126, 150, 3, 0.6, 1.0, 0.8)
                + dustpan(20, 130, 1.0) + '<rect x="0" y="95" width="28" height="40" fill="#2E2E2E"/>'
                + broom(12, 40, -12, 30, 12, 0.9)
                + petals_random(7, 70, 100, 118, 126, 4, 0.8, 1.1)
                + glove(140, 110, 100, 1.0, GLOVE, "#FFFFFF", False, True)
                + '<path d="M60,70 C120,50 180,55 240,70" fill="none" stroke="#FFFFFF" stroke-width="2" stroke-dasharray="6 5" opacity="0.8"/>'
                + petals_random(6, 60, 150, 60, 105, 8, 0.7, 1.0, 0.9))
    if key == "s4":
        return (sky() + bokeh(6, 8) + ground(120, "#4A4744")
                + '<ellipse cx="170" cy="130" rx="90" ry="22" fill="#B9AE9E" opacity="0.7"/>'
                + '<ellipse cx="230" cy="122" rx="55" ry="14" fill="#CFC5B6" opacity="0.6"/>'
                + glove(120, 92, -80, 1.15, GLOVE, "#FFFFFF")
                + '<line x1="20" y1="118" x2="90" y2="118" stroke="#FFFFFF" stroke-width="2" opacity="0.8"/>'
                + '<line x1="30" y1="108" x2="80" y2="108" stroke="#FFFFFF" stroke-width="2" opacity="0.8"/>'
                + dustpan(285, 128, 0.7, True))
    if key == "s5":
        return (sky("#FFF0D8", "#F9D0DD") + '<circle cx="200" cy="56" r="34" fill="#FFF7E6" opacity="0.95"/>'
                + '<circle cx="200" cy="56" r="52" fill="#FFF7E6" opacity="0.35"/>'
                + tweezers(200, 150, 0, 1.15)
                + petal(200, 70, 180, 3.2, "#F8D5E0", PINK_D)
                + '<path d="M200,22 L200,66" stroke="#E9648F" stroke-width="0.8" opacity="0.7"/>'
                + '<path d="M200,40 L190,28 M200,40 L210,28 M200,52 L188,44 M200,52 L212,44" stroke="#E9648F" stroke-width="0.7" opacity="0.6"/>'
                + glove(255, 120, 20, 1.0, GLOVE, "#FFFFFF", False, True)
                + glove(50, 150, -10, 1.0, WORK, "#8C929B", True, False)
                + dustpan(20, 150, 0.8))
    if key == "s6":
        return (sky() + bokeh(7, 8) + f'<rect x="0" y="0" width="150" height="180" fill="{LAB}"/>'
                + '<rect x="0" y="120" width="150" height="60" fill="#151D2E"/>'
                + zipbag(105, 25, 0.42)
                + '<line x1="150" y1="0" x2="150" y2="180" stroke="#5B6478" stroke-width="2"/>'
                + '<path d="M150,90 L120,90" stroke="#FFFFFF" stroke-width="2" opacity="0.7"/>'
                + '<path d="M128,84 L120,90 L128,96" fill="none" stroke="#FFFFFF" stroke-width="2" opacity="0.7"/>')
    if key == "s7":
        return (lab_bg() + '<ellipse cx="160" cy="30" rx="110" ry="14" fill="#FFFFFF" opacity="0.08"/>'
                + stack(90, 128, True, 1.0) + tweezers(150, 70, 30, 0.8)
                + '<path d="M60,40 C120,20 200,25 260,60" fill="none" stroke="#FFFFFF" stroke-width="1" stroke-dasharray="3 4" opacity="0.5"/>')
    if key == "s8":
        return (lab_bg() + instrument(180, 20, "flat", 0.95) + stack(40, 128, False, 0.75)
                + glove(110, 40, 175, 0.9, GLOVE, "#FFFFFF")
                + '<path d="M105,95 L90,120" stroke="#FFFFFF" stroke-width="1" stroke-dasharray="3 3" opacity="0.6"/>'
                + '<path d="M97,96 L98,92 M100,96 L103,92" stroke="#FFFFFF" stroke-width="1" opacity="0.7"/>')
    if key == "s9":
        return (lab_bg() + instrument(200, 20, "one", 0.9, False)
                + stack(30, 140, False, 0.9, True)
                + '<rect x="30" y="86" width="60" height="6" fill="#D7E3F2" opacity="0.9"/>'
                + '<path d="M60,84 L60,74 M56,78 L60,74 L64,78" stroke="#FFFFFF" stroke-width="1.2" fill="none" opacity="0.8"/>'
                + f'<path d="M120,128 C150,128 170,90 200,74" fill="none" stroke="{CYAN}" stroke-width="2.5" opacity="0.9"/>'
                + f'<circle cx="150" cy="118" r="4" fill="{CYAN}"/>'
                + glove(75, 30, 178, 0.75, GLOVE, "#FFFFFF"))
    if key == "s10":
        return (lab_bg() + instrument(160, 24, "two", 1.05) + stack(30, 135, False, 0.7)
                + glove(75, 20, 165, 0.8, GLOVE, "#FFFFFF")
                + '<path d="M40,60 L20,30" stroke="#FFFFFF" stroke-width="2" opacity="0.8"/>'
                + '<path d="M20,30 L18,42 M20,30 L32,32" stroke="#FFFFFF" stroke-width="2" opacity="0.8" fill="none"/>')
    if key == "s11":
        return (lab_bg() + f'<path d="M20,150 C80,150 100,60 140,50 S220,60 300,40" fill="none" stroke="{CYAN}" stroke-width="2" opacity="0.35"/>'
                + clusters() + petals_random(5, 20, 300, 20, 60, 12, 0.5, 0.8, 0.5))
    if key == "s12":
        return (lab_bg(True) + dustpan(150, 128, 1.1, True) + petals_random(30, 80, 150, 92, 124, 13, 0.6, 1.0)
                + glove(215, 70, 75, 0.95, WORK, "#8C929B", True, False)
                + glove(60, 96, -20, 0.9, GLOVE, "#FFFFFF", False, True)
                + glove(105, 105, 25, 0.9, GLOVE, "#FFFFFF", False, True))
    if key == "s13":
        return (lab_bg() + f'<rect x="210" y="0" width="110" height="180" fill="#172226"/>'
                + '<rect x="222" y="40" width="18" height="2" fill="#EDDBB0"/>'
                + '<text x="222" y="62" font-size="7" fill="#EDDBB0" font-family="system-ui,sans-serif" font-weight="700">PPEL+ RESEARCH SHORT</text>'
                + '<text x="222" y="86" font-size="11" fill="#FFFAF0" font-family="system-ui,sans-serif" font-weight="700">From petals</text>'
                + '<text x="222" y="100" font-size="11" fill="#FFFAF0" font-family="system-ui,sans-serif" font-weight="700">to signals.</text>'
                + '<text x="222" y="120" font-size="7" fill="#DBCDD0" font-family="system-ui,sans-serif">Nano Energy · 2026</text>'
                + '<text x="222" y="146" font-size="7" fill="#EDDBB0" font-family="system-ui,sans-serif" font-weight="700">READ THE PAPER →</text>'
                + petals_random(14, 30, 190, 110, 130, 14, 0.5, 0.9)
                + glove(60, 60, 170, 0.7, GLOVE, "#FFFFFF") + glove(140, 60, 190, 0.7, WORK, "#8C929B", True)
                + tweezers(75, 110, 200, 0.5) + tweezers(125, 112, 160, 0.5))
    if key == "s14":
        return ('<rect width="320" height="180" fill="#172226"/>'
                + '<text x="30" y="46" font-size="8" fill="#EDDBB0" font-family="system-ui,sans-serif" font-weight="700">PPEL+</text>'
                + '<text x="30" y="82" font-size="19" fill="#FFFAF0" font-family="system-ui,sans-serif" font-weight="700">From petals to signals.</text>'
                + '<text x="30" y="104" font-size="8" fill="#DBCDD0" font-family="system-ui,sans-serif">Nano Energy · 2026</text>'
                + '<text x="30" y="118" font-size="7" fill="#DBCDD0" font-family="system-ui,sans-serif">10.1016/j.nanoen.2025.111687</text>'
                + '<text x="30" y="150" font-size="8" fill="#EDDBB0" font-family="system-ui,sans-serif" font-weight="700">READ THE PAPER →</text>')
    return sky()


def svg(key, cls="sk"):
    return (f'<svg class="{cls}" viewBox="0 0 320 180" role="img" aria-label="컷 스케치" preserveAspectRatio="xMidYMid slice">'
            + sketch(key) + '</svg>')


# ----------------------------------------------------------------------------
# HTML 조립
# ----------------------------------------------------------------------------
def esc(s):
    return (s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;"))


def embed_image(path):
    if not path or not os.path.exists(path):
        return None
    try:
        from PIL import Image
        im = Image.open(path).convert("RGB")
        buf = io.BytesIO()
        im.save(buf, format="JPEG", quality=86, optimize=True, progressive=True)
        return "data:image/jpeg;base64," + base64.b64encode(buf.getvalue()).decode("ascii")
    except Exception:
        with open(path, "rb") as f:
            return "data:image/png;base64," + base64.b64encode(f.read()).decode("ascii")


def timeline_svg():
    W, H = 960, 215
    L, R = 40, 920
    px = lambda t: L + (R - L) * t / DURATION
    out = [f'<svg viewBox="0 0 {W} {H}" class="tl" role="img" aria-label="30초 타임라인">']
    # 막
    for a in ACTS:
        out.append(f'<rect x="{px(a["t0"]):.1f}" y="22" width="{px(a["t1"]) - px(a["t0"]):.1f}" height="16" fill="{a["color"]}" opacity="0.85" rx="2"/>')
        out.append(f'<text x="{(px(a["t0"]) + px(a["t1"])) / 2:.1f}" y="14" text-anchor="middle" class="tl-act">{a["n"]}막 {a["name"]}</text>')
    # 컷 경계
    for s in SHOTS:
        x0, x1 = px(s["t0"]), px(s["t1"])
        fill = "#EEF2F8" if s["n"] % 2 else "#DCE3ED"
        if s["engine"] == "Cycles":
            fill = "#FBE3EC"
        out.append(f'<rect x="{x0:.1f}" y="44" width="{x1 - x0:.1f}" height="26" fill="{fill}" stroke="#FFFFFF" stroke-width="1"/>')
        if x1 - x0 > 14:
            out.append(f'<text x="{(x0 + x1) / 2:.1f}" y="61" text-anchor="middle" class="tl-shot">{s["n"]}</text>')
    # 자막 큐
    for c in CUES:
        color = {"dialogue": "#3A4358", "science": "#1E3AFF", "card": "#5B6478"}[c["kind"]]
        out.append(f'<rect x="{px(c["start"]):.1f}" y="78" width="{px(c["end"]) - px(c["start"]):.1f}" height="10" rx="2" fill="{color}" opacity="0.9"/>')
    out.append('<text x="40" y="104" class="tl-label">자막 큐 · 회색 대사, 파랑 과학 자막(무대사 구간)</text>')
    # 훅 마커
    hooks = [(s["t0"], s["hook"]) for s in SHOTS if s["hook"]]
    for i, (t, name) in enumerate(hooks):
        x = px(t)
        y = (126, 150, 174)[i % 3]
        out.append(f'<line x1="{x:.1f}" y1="38" x2="{x:.1f}" y2="{y - 10}" stroke="#E9648F" stroke-width="1" stroke-dasharray="2 3"/>')
        out.append(f'<polygon points="{x:.1f},{y - 10} {x + 5:.1f},{y - 4} {x:.1f},{y + 2} {x - 5:.1f},{y - 4}" fill="#E9648F"/>')
        anchor = "start" if t < 26 else "end"
        out.append(f'<text x="{x + (8 if anchor == "start" else -8):.1f}" y="{y}" text-anchor="{anchor}" class="tl-hook">{esc(name.split(" · ")[0])}</text>')
    # 눈금
    for t in range(0, 31, 5):
        out.append(f'<line x1="{px(t):.1f}" y1="40" x2="{px(t):.1f}" y2="44" stroke="#3A4358"/>')
        out.append(f'<text x="{px(t):.1f}" y="208" text-anchor="middle" class="tl-tick">{t}s</text>')
    out.append('</svg>')
    return "".join(out)


def shot_card(s):
    dur = s["t1"] - s["t0"]
    f0, f1 = round(s["t0"] * FPS), round(s["t1"] * FPS) - 1
    hook = f'<div class="hook">훅 · {esc(s["hook"])}</div>' if s["hook"] else ""
    cap = f'<div class="row"><span class="k">자막</span><span>{esc(s["caption"])}</span></div>' if s["caption"] else ""
    return f'''
<article class="card" id="shot-{s["n"]}" data-n="{s["n"]}">
  <div class="thumb">{svg(s["sketch"])}<span class="num">{s["n"]:02d}</span><span class="eng eng-{s["engine"].lower()}">{s["engine"]}</span></div>
  <div class="meta">
    <div class="time"><b>{s["t0"]:.1f}~{s["t1"]:.1f}s</b> · {dur:.1f}s · f{f0}~{f1} · {esc(s["place"])}</div>
    <h3>{esc(s["title"])}</h3>
    {hook}
    <p class="action">{esc(s["action"])}</p>
    <div class="row"><span class="k">카메라</span><span>{esc(s["camera"])}</span></div>
    <div class="row"><span class="k">사운드</span><span>{esc(s["sound"])}</span></div>
    {cap}
    <div class="row"><span class="k">Blender</span><span>{esc(s["blender"])}</span></div>
  </div>
</article>'''


def build_html(poc_data_uri):
    shots_js = json.dumps([dict(n=s["n"], t0=s["t0"], t1=s["t1"], title=s["title"], sketch=s["sketch"]) for s in SHOTS], ensure_ascii=False)
    cues_js = json.dumps(CUES, ensure_ascii=False)
    sketches_js = json.dumps({s["sketch"]: svg(s["sketch"], "stage-svg") for s in SHOTS}, ensure_ascii=False)
    poc_block = ""
    if poc_data_uri:
        poc_block = f'''
<figure class="poc">
  <img src="{poc_data_uri}" alt="개념 검증 렌더: 지면 12 mm 높이에서 본 벚꽃잎, 왼쪽에서 들어오는 빗자루, 분홍 보케" width="1280" height="720"/>
  <figcaption>개념 검증 렌더 1장. 컷 1~2의 프레임을 blender/petal_ground_poc.py 한 파일로 생성해 Cycles(CPU, 128 샘플)로 렌더했다. 끝이 갈라진 왕벚꽃 꽃잎, 기부 분홍에서 끝 흰색으로 가는 그라데이션, 지면 카펫의 심도 흐림, 왼쪽의 빗자루, 분홍 보케가 모두 스크립트로 재현된다.</figcaption>
</figure>'''
    cue_rows = "".join(f'<tr><td class="mono">{c["start"]:.1f}</td><td class="mono">{c["end"]:.1f}</td><td>{esc(c["ko"])}</td><td>{esc(c["en"])}</td><td><span class="pill pill-{c["kind"]}">{ {"dialogue": "대사", "science": "과학", "card": "카드"}[c["kind"]] }</span></td></tr>' for c in CUES)
    sound_rows = "".join(f'<li><span class="mono">{t:>4.1f}s</span> {esc(n)}</li>' for t, n in SOUND)
    cards = "".join(shot_card(s) for s in SHOTS)
    today = date.today().isoformat()
    return f'''<title>벚꽃 단편 v4 스토리보드</title>
<style>
:root{{--ink:#0A0F1E;--soft:#3A4358;--trace:#5B6478;--line:#DCE3ED;--surface:#FFFFFF;--surface2:#EEF2F8;--blue:#1E3AFF;--cyan:#00B79C;--pink:#E9648F;--film:#172226;--maxw:1180px}}
*{{box-sizing:border-box}}
body{{margin:0;background:#F7F8FB;color:var(--ink);font-family:"Pretendard","Inter",system-ui,-apple-system,"Malgun Gothic",sans-serif;line-height:1.6;font-size:15px}}
.wrap{{max-width:var(--maxw);margin:0 auto;padding:0 20px}}
header.top{{background:#070B16;color:#E9EEF8;padding:44px 0 34px}}
header.top .eyebrow{{font-family:"IBM Plex Mono",ui-monospace,monospace;font-size:12px;letter-spacing:.22em;text-transform:uppercase;color:#8597C2}}
header.top h1{{font-size:clamp(26px,3.4vw,40px);line-height:1.15;margin:10px 0 8px;letter-spacing:-.02em}}
header.top h1 small{{display:block;font-size:.5em;font-weight:500;color:#A6B0C4;margin-top:6px}}
header.top p.lead{{max-width:820px;color:#C8D0E0;margin:0 0 18px}}
.badges{{display:flex;gap:8px;flex-wrap:wrap}}
.badges span{{font-family:"IBM Plex Mono",ui-monospace,monospace;font-size:12px;border:1px solid #2A3550;border-radius:20px;padding:4px 10px;color:#C8D0E0}}
section{{padding:34px 0;border-top:1px solid var(--line)}}
section h2{{font-size:22px;margin:0 0 6px;letter-spacing:-.01em}}
section p.sub{{margin:0 0 18px;color:var(--soft)}}
.poc{{margin:26px 0 0;background:#0E1525;border-radius:14px;overflow:hidden;border:1px solid #1E293E}}
.poc img{{display:block;width:100%;height:auto}}
.poc figcaption{{padding:12px 16px;font-size:13px;color:#A6B0C4}}
.tl{{width:100%;height:auto;display:block;background:var(--surface);border:1px solid var(--line);border-radius:12px;padding:10px}}
.tl-act{{font-size:11px;font-weight:700;fill:#3A4358}}
.tl-shot{{font-size:11px;fill:#0A0F1E;font-family:ui-monospace,monospace}}
.tl-label{{font-size:11px;fill:#5B6478}}
.tl-hook{{font-size:11px;fill:#0A0F1E;font-weight:600}}
.tl-tick{{font-size:11px;fill:#5B6478;font-family:ui-monospace,monospace}}
.legend{{display:flex;gap:14px;flex-wrap:wrap;font-size:12px;color:var(--soft);margin-top:10px}}
.legend i{{display:inline-block;width:12px;height:12px;border-radius:3px;vertical-align:-2px;margin-right:5px}}
.hooks{{display:grid;grid-template-columns:repeat(auto-fit,minmax(250px,1fr));gap:12px;margin-top:18px}}
.hooks div{{background:var(--surface);border:1px solid var(--line);border-radius:12px;padding:14px 16px}}
.hooks b{{display:block;font-family:ui-monospace,monospace;font-size:12px;color:var(--pink);margin-bottom:4px}}
.hooks strong{{display:block;margin-bottom:4px}}
.hooks small{{color:var(--soft)}}
.player{{background:var(--film);border-radius:16px;overflow:hidden;box-shadow:0 2px 8px rgba(10,15,30,.06),0 30px 60px -28px rgba(10,15,30,.28)}}
.stage{{position:relative;aspect-ratio:16/9;background:#223036;overflow:hidden}}
.stage svg{{position:absolute;inset:0;width:100%;height:100%}}
.stage .shotlabel{{position:absolute;left:14px;top:12px;background:rgba(7,11,22,.7);color:#fff;font-family:ui-monospace,monospace;font-size:12px;padding:4px 9px;border-radius:14px}}
.stage .poster{{position:absolute;right:14px;top:12px;background:rgba(233,100,143,.9);color:#fff;font-size:11px;padding:4px 9px;border-radius:14px;letter-spacing:.06em}}
.subpanel{{display:flex;align-items:center;gap:12px;min-height:82px;padding:12px 16px;background:var(--film);color:#fff}}
.subpanel p{{flex:1;margin:0;font-size:clamp(14px,1.25vw,18px);font-weight:500;line-height:1.5;text-align:center;white-space:pre-line}}
.subpanel .en{{display:block;font-size:.78em;color:#A6B0C4;font-weight:400}}
.controls{{display:flex;align-items:center;gap:12px;padding:10px 14px 14px;background:var(--film);color:#C8D0E0;font-family:ui-monospace,monospace;font-size:13px}}
.controls button{{border:1px solid #ffffff45;border-radius:8px;background:transparent;color:#fff;font:inherit;padding:6px 14px;cursor:pointer}}
.controls button:hover{{border-color:#fff}}
.bar{{position:relative;flex:1;height:14px;background:#223036;border-radius:7px;overflow:hidden;cursor:pointer}}
.bar .seg{{position:absolute;top:0;bottom:0;opacity:.55}}
.bar .head{{position:absolute;top:0;bottom:0;width:2px;background:#fff}}
.cards{{display:grid;grid-template-columns:repeat(auto-fill,minmax(340px,1fr));gap:18px}}
.card{{background:var(--surface);border:1px solid var(--line);border-radius:14px;overflow:hidden;cursor:pointer;transition:box-shadow .2s}}
.card:hover,.card.active{{box-shadow:0 0 0 2px var(--blue)}}
.thumb{{position:relative;aspect-ratio:16/9;background:#223036}}
.thumb svg{{position:absolute;inset:0;width:100%;height:100%}}
.thumb .num{{position:absolute;left:10px;top:10px;background:rgba(7,11,22,.75);color:#fff;font-family:ui-monospace,monospace;font-size:12px;padding:2px 8px;border-radius:12px}}
.thumb .eng{{position:absolute;right:10px;top:10px;font-family:ui-monospace,monospace;font-size:11px;padding:2px 8px;border-radius:12px;color:#fff;background:#3A4358}}
.eng-cycles{{background:#C26386!important}}.eng-eevee{{background:#1E3AFF!important}}.eng-ffmpeg{{background:#5B6478!important}}
.meta{{padding:14px 16px 16px}}
.meta .time{{font-size:12px;color:var(--trace);font-family:ui-monospace,monospace}}
.meta h3{{margin:4px 0 6px;font-size:18px}}
.meta .hook{{display:inline-block;font-size:11px;color:var(--pink);border:1px solid #F4B6C8;border-radius:12px;padding:1px 8px;margin-bottom:8px}}
.meta .action{{margin:0 0 10px;color:var(--ink)}}
.meta .row{{display:grid;grid-template-columns:64px 1fr;gap:8px;font-size:13px;color:var(--soft);padding:3px 0;border-top:1px dashed var(--line)}}
.meta .k{{font-weight:700;color:var(--trace);font-size:12px}}
table{{width:100%;border-collapse:collapse;background:var(--surface);border:1px solid var(--line);border-radius:12px;overflow:hidden;font-size:14px}}
th,td{{padding:9px 12px;text-align:left;border-bottom:1px solid var(--line);vertical-align:top}}
th{{background:var(--surface2);font-size:12px;letter-spacing:.04em;color:var(--soft)}}
.mono{{font-family:ui-monospace,monospace;font-size:13px}}
.pill{{font-size:11px;border-radius:12px;padding:1px 8px;color:#fff;background:#3A4358}}
.pill-science{{background:var(--blue)}}.pill-card{{background:#5B6478}}
.two{{display:grid;grid-template-columns:1fr 1fr;gap:22px}}
@media(max-width:820px){{.two{{grid-template-columns:1fr}}}}
.box{{background:var(--surface);border:1px solid var(--line);border-radius:14px;padding:16px 18px}}
.box h3{{margin:0 0 8px;font-size:16px}}
.box ul,.box ol{{margin:0;padding-left:18px}}
.box li{{margin:4px 0}}
.box li .mono{{color:var(--trace);margin-right:6px}}
.tablewrap{{overflow-x:auto}}
footer{{padding:28px 0 48px;color:var(--trace);font-size:13px;border-top:1px solid var(--line)}}
footer a{{color:var(--blue)}}
</style>

<header class="top"><div class="wrap">
  <div class="eyebrow">PPEL+ Research Short · v4 Storyboard</div>
  <h1>잠깐만요! Blender 리메이크<small>벚꽃잎 TENG 제스처 인식(Nano Energy 2026)을 30초로 소개하는 홈페이지 단편의 고화질 재제작 구상안</small></h1>
  <p class="lead">빗자루에 쓸려 가던 벚꽃잎 한 장이 센서의 한 층이 되어 손끝의 탭을 신호로 바꾼다. 카메라는 시작부터 끝까지 꽃잎의 눈높이에 있고, 인물은 얼굴 없이 두 종류의 장갑으로만 연기한다.</p>
  <div class="badges"><span>30.000 s</span><span>24 fps · 720 frames</span><span>14 cuts</span><span>1920×1080</span><span>Cycles 2컷 + EEVEE 10컷 + FFmpeg 2컷</span><span>화면 안 글자 0</span></div>
  {poc_block}
</div></header>

<section><div class="wrap">
  <h2>1. 30초 타임라인과 훅 7개</h2>
  <p class="sub">분홍 칸은 Cycles 매크로 컷. 마름모는 시청자의 시선을 다시 붙잡는 지점이다. 3초마다 하나씩, 같은 장치는 두 번 쓰지 않는다.</p>
  {timeline_svg()}
  <div class="legend"><span><i style="background:#E9648F"></i>1막 위기</span><span><i style="background:#1E3AFF"></i>2막 변신</span><span><i style="background:#00B79C"></i>3막 페이오프</span><span><i style="background:#5B6478"></i>카드</span><span><i style="background:#FBE3EC;border:1px solid #E9648F"></i>Cycles 컷</span></div>
  <div class="hooks">
    <div><b>0.0~1.5s</b><strong>정적의 아름다움</strong><small>역광 꽃잎 한 장의 초매크로 낙하. 바람과 피아노 한 음. 시청자가 마음을 놓는 구간.</small></div>
    <div><b>1.5s</b><strong>패턴 인터럽트</strong><small>빗자루가 렌즈로 돌진해 정적을 깨뜨린다. 거친 쓸림이 영상의 첫 큰 소리다.</small></div>
    <div><b>1.8~4.6s</b><strong>작은 것에 거는 큰 헌신</strong><small>절규 잠깐만요! 뒤에 장갑 손이 수평으로 날아들어 쓰레받기 턱 1 cm 위에서 꽃잎을 움켜쥔다. 약 3.4초가 포스터 프레임.</small></div>
    <div><b>5.6~8.4s</b><strong>이건 AI 생성이 아니다 신호</strong><small>핀셋에 들린 꽃잎을 태양에 비춘 초매크로. 잎맥과 끝 갈라짐이 선명하다. 여기서 화질을 평가받는다.</small></div>
    <div><b>10.0~14.0s</b><strong>조립 ASMR</strong><small>떠 있던 층이 박자에 맞춰 하나씩 내려와 닫힌다. 정밀함은 사람을 끝까지 보게 만든다.</small></div>
    <div><b>16.5~21.0s</b><strong>페이오프</strong><small>한 번 닿자 스파이크 하나, 두 번 닿자 둘. 시청자가 규칙을 스스로 알아챈다.</small></div>
    <div><b>24.5~27.5s</b><strong>콜백과 관계 반전</strong><small>꽃잎을 쓸어버리던 미화원이 흠 없는 꽃잎이 소복한 쓰레받기를 헌상한다.</small></div>
  </div>
</div></section>

<section><div class="wrap">
  <h2>2. 스토리보드 플레이어</h2>
  <p class="sub">홈페이지와 같은 하단 자막 패널로 큐 타이밍을 재생해 본다. 스케치는 구도 메모이며 최종 화면이 아니다. 재생 버튼을 누르거나 아래 카드를 클릭하면 해당 컷으로 이동한다.</p>
  <div class="player">
    <div class="stage" id="stage"><span class="shotlabel" id="shotlabel">01 · 정적</span><span class="poster" id="posterTag" hidden>POSTER FRAME</span></div>
    <div class="subpanel"><p id="sub"> </p></div>
    <div class="controls">
      <button id="play" type="button">재생</button>
      <span id="clock">00.0 / 30.0</span>
      <div class="bar" id="bar"><div class="head" id="head" style="left:0"></div></div>
      <span id="frame">f0</span>
    </div>
  </div>
</div></section>

<section><div class="wrap">
  <h2>3. 샷 리스트 14컷</h2>
  <p class="sub">모든 자막은 화면 밖 하단 패널 전용이다. 화면 안 글자는 계측기 화면의 파형만 예외로 둔다.</p>
  <div class="cards" id="cards">{cards}</div>
</div></section>

<section><div class="wrap">
  <h2>4. 자막 큐와 사운드 큐</h2>
  <div class="two">
    <div class="tablewrap"><table><thead><tr><th>시작</th><th>끝</th><th>KO</th><th>EN</th><th>종류</th></tr></thead><tbody>{cue_rows}</tbody></table></div>
    <div class="box"><h3>사운드 큐 (120 BPM, 1박 0.5초)</h3><ul>{sound_rows}</ul></div>
  </div>
</div></section>

<section><div class="wrap">
  <h2>5. Blender 제작 설계도 요약</h2>
  <div class="two">
    <div class="box"><h3>공통 사양</h3><ul>
      <li>Blender 4.5 LTS 이상. 씬은 bpy 스크립트로 생성해 저장소에 남기고 GUI는 확인용.</li>
      <li>1920×1080, 24 fps, 정확히 720프레임. 시안은 960×540.</li>
      <li>컷 1, 5는 Cycles(반투명 꽃잎, 매크로 심도). 나머지는 EEVEE. 색 관리는 AgX로 통일.</li>
      <li>모션 블러는 실시간 컷만, 슬로모 구간은 오프. 매크로 컷 심도 f/4 내외.</li>
      <li>컴포지터: 미세 그레인, 비네트, 실험실 블룸. 어떤 경로로도 화면 안 글자를 넣지 않는다.</li>
    </ul></div>
    <div class="box"><h3>에셋</h3><ul>
      <li>꽃잎 메시와 반투명 재질, 지오메트리 노드 산포, 짚 빗자루: 개념 검증 스크립트에 구현 완료.</li>
      <li>장갑 손 2종: MakeHuman 또는 Blender Studio Human Base Meshes(CC0) 팔 + Rigify. 파란 니트릴, 빨간 점박이 코팅장갑.</li>
      <li>긴 손잡이 쓰레받기, 5층 소자 스택(단면 모델 별도), 벤치톱 계측기(콘센트까지 보이는 전원선), 파형 PNG 720장.</li>
      <li>야외는 지면 텍스처와 분홍 보케 발광 구만. 나무 모델 불필요.</li>
    </ul></div>
    <div class="box"><h3>제작 순서와 승인 지점</h3><ol>
      <li>회색 박스 애니매틱 + 임시 음성 + 자막 큐로 30초 확인. <b>승인 1</b></li>
      <li>히어로 에셋: 꽃잎, 장갑 손 2종, 빗자루, 쓰레받기, 소자.</li>
      <li>히어로 컷 스틸: 3(포스터), 5(뷔티샷), 7(조립), 9~10(탭). <b>승인 2</b></li>
      <li>나머지 컷과 컴포지팅.</li>
      <li>음성 녹음, 음악, 효과음, 믹스(-16 LUFS).</li>
      <li>PNG 시퀀스 → FFmpeg 조립 → 포스터 → VTT → edit-plan.json.</li>
      <li>QA와 홈페이지 통합(벚꽃 카드 1장, 노트 문구, 빌드 스탬프).</li>
    </ol></div>
    <div class="box"><h3>과학 표현 락</h3><ul>
      <li>꽃잎은 소자의 한 층. 꽃잎이 전기를 만들어 실험실이나 화면을 켠다고 읽히는 컷 없음.</li>
      <li>신호는 접촉과 분리에서 나온다. 컷 9의 단면이 그것만 보여준다.</li>
      <li>머신러닝은 한 번과 두 번 탭을 구별한다. 확장 주장 없음.</li>
      <li>계측기와 화면은 콘센트에 꽂힌 별도 전원.</li>
      <li>성능 수치와 공정 세부는 논문 링크로 이관. 소자 제작 컷은 연출이며 실험 촬영물이 아니라고 표기.</li>
    </ul></div>
  </div>
</div></section>

<footer><div class="wrap">전체 문서: <a href="CLAUDE_BLENDER_CONCEPT.md">CLAUDE_BLENDER_CONCEPT.md</a> · 기계 판독용 <a href="shotlist.json">shotlist.json</a> · 개념 검증 <a href="blender/petal_ground_poc.py">blender/petal_ground_poc.py</a> · 이 페이지는 tools/build_storyboard.py가 생성했다 ({today}).</div></footer>

<script>
(function(){{
  const SHOTS={shots_js};
  const CUES={cues_js};
  const SK={sketches_js};
  const DUR={DURATION}, FPS={FPS}, POSTER_T=3.4;
  const stage=document.getElementById('stage'), sub=document.getElementById('sub'), clock=document.getElementById('clock');
  const head=document.getElementById('head'), bar=document.getElementById('bar'), playBtn=document.getElementById('play');
  const frameEl=document.getElementById('frame'), label=document.getElementById('shotlabel'), posterTag=document.getElementById('posterTag');
  const ACTS=[[0,8.4,'#E9648F'],[8.4,16.5,'#1E3AFF'],[16.5,27.5,'#00B79C'],[27.5,30,'#5B6478']];
  ACTS.forEach(a=>{{const d=document.createElement('div');d.className='seg';d.style.left=(a[0]/DUR*100)+'%';d.style.width=((a[1]-a[0])/DUR*100)+'%';d.style.background=a[2];bar.insertBefore(d,head);}});
  let t=0, playing=false, timer=null, last=0, cur=-1, svgEl=null;
  function shotAt(x){{for(const s of SHOTS){{if(x>=s.t0&&x<s.t1)return s;}}return SHOTS[SHOTS.length-1];}}
  function render(){{
    const s=shotAt(t);
    if(s.n!==cur){{cur=s.n;if(svgEl)svgEl.remove();const w=document.createElement('div');w.innerHTML=SK[s.sketch];svgEl=w.firstChild;stage.appendChild(svgEl);
      label.textContent=String(s.n).padStart(2,'0')+' · '+s.title;
      document.querySelectorAll('.card').forEach(c=>c.classList.toggle('active',+c.dataset.n===s.n));}}
    posterTag.hidden=!(t>=POSTER_T-0.35&&t<=POSTER_T+0.35);
    const c=CUES.find(q=>t>=q.start&&t<q.end);
    sub.innerHTML=c?(c.ko.replace(/</g,'&lt;')+'<span class="en">'+c.en.replace(/</g,'&lt;')+'</span>'):' ';
    clock.textContent=t.toFixed(1).padStart(4,'0')+' / 30.0';
    frameEl.textContent='f'+Math.min(719,Math.floor(t*FPS));
    head.style.left=(t/DUR*100)+'%';
  }}
  function tick(){{const now=performance.now();t+=(now-last)/1000;last=now;if(t>=DUR){{t=DUR-0.001;render();stop();t=0;return;}}render();}}
  function start(){{if(playing)return;playing=true;playBtn.textContent='일시정지';last=performance.now();timer=setInterval(tick,1000/30);}}
  function stop(){{playing=false;playBtn.textContent='재생';if(timer){{clearInterval(timer);timer=null;}}}}
  playBtn.addEventListener('click',()=>playing?stop():start());
  bar.addEventListener('click',e=>{{const r=bar.getBoundingClientRect();t=Math.max(0,Math.min(DUR-0.001,(e.clientX-r.left)/r.width*DUR));render();}});
  document.querySelectorAll('.card').forEach(c=>c.addEventListener('click',()=>{{const s=SHOTS.find(x=>x.n===+c.dataset.n);t=s.t0;render();document.querySelector('.player').scrollIntoView({{block:'nearest'}});}}));
  render();
}})();
</script>
'''


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--poc", default=os.path.join(OUT_DIR, "poc", "petal-ground-poc.png"))
    a = ap.parse_args()
    data = dict(
        title="잠깐만요! Blender 리메이크",
        status="concept",
        durationSeconds=DURATION, fps=FPS, frames=int(DURATION * FPS), width=1920, height=1080,
        posterTimeSeconds=3.4,
        acts=ACTS,
        shots=[dict(n=s["n"], start=s["t0"], end=s["t1"], frameStart=round(s["t0"] * FPS), frameEnd=round(s["t1"] * FPS) - 1,
                    place=s["place"], title=s["title"], action=s["action"], camera=s["camera"], sound=s["sound"],
                    caption=s["caption"], engine=s["engine"], act=s["act"], blender=s["blender"], hook=s["hook"]) for s in SHOTS],
        captions=dict(placement="existing below-picture subtitle panel", cues=CUES),
        soundCues=[dict(time=t, cue=n) for t, n in SOUND],
        paperCard=dict(start=28.0, end=30.0, journal="Nano Energy", year=2026, doi="10.1016/j.nanoen.2025.111687"),
        scienceLock=[
            "꽃잎은 소자의 한 층이다. 꽃잎이 전기를 만들어 실험실이나 화면을 켠다고 읽히는 컷은 없다.",
            "신호는 접촉과 분리에서 나온다.",
            "머신러닝은 한 번과 두 번 탭을 구별한다. 확장 주장은 없다.",
            "계측기와 화면은 콘센트에 꽂힌 별도 전원을 쓴다.",
            "화면 안 글자 0(계측기 파형만 예외). 자막은 하단 패널 전용이며 영상에 굽지 않는다.",
        ],
    )
    with open(os.path.join(OUT_DIR, "shotlist.json"), "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
        f.write("\n")
    html = build_html(embed_image(a.poc))
    with open(os.path.join(OUT_DIR, "storyboard.html"), "w", encoding="utf-8") as f:
        f.write(html)
    total = sum(s["t1"] - s["t0"] for s in SHOTS)
    assert abs(total - DURATION) < 1e-6, total
    for x, y in zip(SHOTS, SHOTS[1:]):
        assert abs(x["t1"] - y["t0"]) < 1e-6, (x["n"], y["n"])
    print("storyboard.html / shotlist.json 생성 완료, 총 길이", total, "초")


if __name__ == "__main__":
    main()
