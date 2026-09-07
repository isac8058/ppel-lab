# 벚꽃 단편 v4: Blender 리메이크 (구상 단계)

상태: **구상안과 개념 검증 렌더 1장만 있다. 영상은 아직 없다.** 홈페이지는 계속 v3(잠깐만요!)를 재생한다.

v3에서 확정된 이야기(꽃잎을 구출하는 연구원, 쓸어버리는 미화원, 꽃잎이 센서의 한 층이 되어 한 번·두 번 탭을 구별)를 Astra가 Blender로 다시 만든다. 생성 영상의 인물 흔들림과 720p 한계를 결정론적 3D 렌더로 넘어서는 것이 목표다.

| 파일 | 내용 |
|---|---|
| `CLAUDE_BLENDER_CONCEPT.md` | 훅 설계 7개, 14컷 샷 리스트, 자막 큐, 사운드, Blender 제작 설계도, 과학 락, 통합 사양, 대안, 결정 항목 |
| `storyboard.html` | 단일 HTML 스토리보드. 14컷 스케치와 30초 타임라인, 사이트와 같은 하단 자막 패널로 큐 타이밍을 재생 |
| `shotlist.json` | 샷 리스트와 자막 큐의 기계 판독용 사본(Blender 씬 생성과 FFmpeg 조립에서 참조) |
| `blender/petal_ground_poc.py` | 컷 1~2 프레임을 빈 씬에서 생성하고 Cycles로 렌더하는 단독 스크립트 |
| `poc/petal-ground-poc.png`, `poc/render.log` | 개념 검증 렌더 결과와 소요 시간 기록 |

## 개념 검증 실행

```text
blender -b -P Video/research/v4/blender/petal_ground_poc.py -- --out /tmp/poc.png --samples 128 --scale 100
```

Blender 없이도 `pip install bpy` 뒤 `python Video/research/v4/blender/petal_ground_poc.py -- --out /tmp/poc.png`로 같은 결과가 나온다. `--scale 30 --samples 16`이면 몇 초 안에 구도만 확인할 수 있다.

## 제작 원칙 (v3 계승)

- 화면 안 글자 0(계측기 파형만 예외). 자막은 홈페이지 하단 패널 전용이며 영상에 굽지 않는다.
- 꽃잎은 소자의 한 층이고 신호는 접촉과 분리에서 나온다. 계측기와 화면은 콘센트에 꽂힌 별도 전원을 쓴다.
- 30.000초, 24 fps, 720프레임, 마지막 1초는 논문 카드. 반응 정지나 장면 반복으로 길이를 채우지 않는다.
- 얼굴을 보여주지 않는다. 파란 니트릴 장갑(연구원)과 빨간 점박이 코팅장갑(미화원)이 두 인물을 대신한다.
