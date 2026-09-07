# -*- coding: utf-8 -*-
"""
PPEL+ 벚꽃 단편 v4 (Blender) 개념 검증 렌더: 샷 1~2 '꽃잎 눈높이' 프레임.

목적: 꽃잎 메시/반투명 재질/지오메트리 노드 산포/역광 매크로 카메라가
Blender Python(bpy)만으로 재현되는지 확인한다. 이 파일은 단독 실행용이다.

실행 (Blender 4.5 LTS 이상 또는 pip bpy 5.x):
  blender -b -P petal_ground_poc.py -- --out /path/render.png --samples 128 --scale 100
  python  petal_ground_poc.py -- --out /path/render.png --samples 128 --scale 100

--scale 은 해상도 퍼센트(1280x720 기준). 빠른 확인은 --scale 25 --samples 16.
"""
import argparse
import math
import random
import sys

import bpy
from mathutils import Vector

# ----------------------------------------------------------------------------
# 인자
# ----------------------------------------------------------------------------
argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
ap = argparse.ArgumentParser()
ap.add_argument("--out", default="/tmp/petal_ground_poc.png")
ap.add_argument("--samples", type=int, default=128)
ap.add_argument("--scale", type=int, default=100)
ap.add_argument("--seed", type=int, default=7)
ap.add_argument("--no-broom", action="store_true")
args = ap.parse_args(argv)
random.seed(args.seed)

# ----------------------------------------------------------------------------
# 빈 씬
# ----------------------------------------------------------------------------
bpy.ops.wm.read_factory_settings(use_empty=True)
scene = bpy.context.scene
scene.unit_settings.system = "METRIC"
scene.unit_settings.scale_length = 1.0

# ----------------------------------------------------------------------------
# 꽃잎 메시: 왕벚꽃 꽃잎(끝이 살짝 갈라진 도란형)을 매개변수 격자로 생성
# ----------------------------------------------------------------------------
PETAL_L = 0.014   # 길이 14 mm
PETAL_W = 0.011   # 최대 폭 11 mm
NOTCH_D = 0.0022  # 끝 갈라짐 깊이 2.2 mm


def petal_half_width(t):
    """t: 0(기부) -> 1(끝). 기부는 가늘고 0.6 부근이 가장 넓다."""
    a = 0.30 * PETAL_W * 0.5           # 끝 쪽 갈라짐 양끝 반폭
    base = 0.05 * PETAL_W * 0.5        # 기부 최소 반폭(퇴화 방지)
    return base + a * t + (0.5 * PETAL_W - a) * math.sin(math.pi * t ** 0.8)


def build_petal(name="Petal", nu=14, nv=44):
    verts, faces, uvs = [], [], []
    for j in range(nv + 1):
        t = j / nv
        hw = petal_half_width(t)
        for i in range(nu + 1):
            u = -1.0 + 2.0 * i / nu
            x = u * hw
            y = PETAL_L * t - NOTCH_D * max(0.0, 1.0 - abs(u)) ** 2 * t ** 10
            # 폭 방향 오목함 + 길이 방향 살짝 뒤로 젖혀짐
            z = 0.10 * PETAL_L * (u ** 2) * (hw / (0.5 * PETAL_W)) + 0.05 * PETAL_L * t ** 2
            verts.append((x, y, z))
            uvs.append(((u + 1) / 2, t))
    for j in range(nv):
        for i in range(nu):
            a = j * (nu + 1) + i
            faces.append((a, a + 1, a + nu + 2, a + nu + 1))
    mesh = bpy.data.meshes.new(name)
    mesh.from_pydata(verts, [], faces)
    mesh.update()
    uv_layer = mesh.uv_layers.new(name="UVMap")
    for poly in mesh.polygons:
        for li in poly.loop_indices:
            vi = mesh.loops[li].vertex_index
            uv_layer.data[li].uv = uvs[vi]
    for poly in mesh.polygons:
        poly.use_smooth = True
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.collection.objects.link(obj)
    # 원점을 꽃잎 중심 근처로
    for v in mesh.vertices:
        v.co.y -= PETAL_L * 0.5
    return obj


# ----------------------------------------------------------------------------
# 재질
# ----------------------------------------------------------------------------
def petal_material():
    m = bpy.data.materials.new("PetalTranslucent")
    m.use_nodes = True
    nt = m.node_tree
    nt.nodes.clear()
    out = nt.nodes.new("ShaderNodeOutputMaterial")
    mix = nt.nodes.new("ShaderNodeMixShader")
    principled = nt.nodes.new("ShaderNodeBsdfPrincipled")
    translucent = nt.nodes.new("ShaderNodeBsdfTranslucent")
    texco = nt.nodes.new("ShaderNodeTexCoord")
    sep = nt.nodes.new("ShaderNodeSeparateXYZ")
    ramp = nt.nodes.new("ShaderNodeValToRGB")
    objinfo = nt.nodes.new("ShaderNodeObjectInfo")
    hue = nt.nodes.new("ShaderNodeHueSaturation")
    wave = nt.nodes.new("ShaderNodeTexWave")
    noise = nt.nodes.new("ShaderNodeTexNoise")
    mapping = nt.nodes.new("ShaderNodeMapping")
    veins_ramp = nt.nodes.new("ShaderNodeValToRGB")
    mixcol = nt.nodes.new("ShaderNodeMix")
    bump = nt.nodes.new("ShaderNodeBump")
    darken = nt.nodes.new("ShaderNodeMix")

    # 기부(진한 분홍) -> 끝(거의 흰색) 그라데이션
    ramp.color_ramp.elements[0].position = 0.0
    ramp.color_ramp.elements[0].color = (0.88, 0.30, 0.48, 1.0)
    ramp.color_ramp.elements[1].position = 1.0
    ramp.color_ramp.elements[1].color = (0.99, 0.93, 0.95, 1.0)
    e = ramp.color_ramp.elements.new(0.35)
    e.color = (0.97, 0.72, 0.80, 1.0)

    # 인스턴스별 색 편차
    hue.inputs["Hue"].default_value = 0.5
    hue.inputs["Saturation"].default_value = 1.0
    hue.inputs["Value"].default_value = 1.0

    # 잎맥: 길이 방향으로 달리는 얇은 띠
    mapping.inputs["Scale"].default_value = (9.0, 1.0, 1.0)
    wave.wave_type = "BANDS"
    wave.bands_direction = "X"
    wave.inputs["Scale"].default_value = 1.0
    wave.inputs["Distortion"].default_value = 7.0
    wave.inputs["Detail"].default_value = 3.0
    wave.inputs["Detail Scale"].default_value = 1.6
    noise.inputs["Scale"].default_value = 6.0
    noise.inputs["Detail"].default_value = 3.0
    veins_ramp.color_ramp.elements[0].position = 0.58
    veins_ramp.color_ramp.elements[0].color = (0, 0, 0, 1)
    veins_ramp.color_ramp.elements[1].position = 0.70
    veins_ramp.color_ramp.elements[1].color = (1, 1, 1, 1)

    mixcol.data_type = "RGBA"
    mixcol.blend_type = "MULTIPLY"
    mixcol.inputs["Factor"].default_value = 0.42
    mixcol.inputs[7].default_value = (0.78, 0.45, 0.58, 1.0)  # B 입력(RGBA)

    darken.data_type = "RGBA"
    darken.blend_type = "MULTIPLY"
    darken.inputs["Factor"].default_value = 1.0

    bump.inputs["Strength"].default_value = 0.15
    bump.inputs["Distance"].default_value = 0.0004

    principled.inputs["Roughness"].default_value = 0.42
    principled.inputs["Sheen Weight"].default_value = 0.35
    principled.inputs["Subsurface Weight"].default_value = 0.25
    principled.inputs["Subsurface Radius"].default_value = (0.004, 0.002, 0.002)
    principled.inputs["Subsurface Scale"].default_value = 0.002
    mix.inputs["Fac"].default_value = 0.68

    L = nt.links.new
    L(texco.outputs["UV"], sep.inputs["Vector"])
    L(sep.outputs["Y"], ramp.inputs["Fac"])
    L(ramp.outputs["Color"], hue.inputs["Color"])
    L(objinfo.outputs["Random"], hue.inputs["Hue"])
    L(texco.outputs["UV"], mapping.inputs["Vector"])
    L(mapping.outputs["Vector"], wave.inputs["Vector"])
    L(texco.outputs["UV"], noise.inputs["Vector"])
    L(noise.outputs["Fac"], wave.inputs["Phase Offset"])
    L(wave.outputs["Fac"], veins_ramp.inputs["Fac"])
    L(veins_ramp.outputs["Color"], mixcol.inputs["Factor"])
    L(hue.outputs["Color"], mixcol.inputs[6])   # A 입력(RGBA)
    L(mixcol.outputs[2], principled.inputs["Base Color"])
    L(mixcol.outputs[2], translucent.inputs["Color"])
    L(veins_ramp.outputs["Color"], bump.inputs["Height"])
    L(bump.outputs["Normal"], principled.inputs["Normal"])
    L(principled.outputs["BSDF"], mix.inputs[1])
    L(translucent.outputs["BSDF"], mix.inputs[2])
    L(mix.outputs["Shader"], out.inputs["Surface"])
    # Hue 노드의 Hue 입력은 0.5가 무변화. Random(0~1)을 0.46~0.54로 좁힌다.
    maprange = nt.nodes.new("ShaderNodeMapRange")
    maprange.inputs["From Min"].default_value = 0.0
    maprange.inputs["From Max"].default_value = 1.0
    maprange.inputs["To Min"].default_value = 0.47
    maprange.inputs["To Max"].default_value = 0.53
    L(objinfo.outputs["Random"], maprange.inputs["Value"])
    L(maprange.outputs["Result"], hue.inputs["Hue"])
    return m


def ground_material():
    m = bpy.data.materials.new("Pavement")
    m.use_nodes = True
    nt = m.node_tree
    p = nt.nodes["Principled BSDF"]
    noise = nt.nodes.new("ShaderNodeTexNoise")
    noise.inputs["Scale"].default_value = 180.0
    noise.inputs["Detail"].default_value = 6.0
    noise.inputs["Roughness"].default_value = 0.7
    ramp = nt.nodes.new("ShaderNodeValToRGB")
    ramp.color_ramp.elements[0].color = (0.05, 0.05, 0.05, 1)
    ramp.color_ramp.elements[1].color = (0.20, 0.19, 0.17, 1)
    bump = nt.nodes.new("ShaderNodeBump")
    bump.inputs["Strength"].default_value = 0.6
    bump.inputs["Distance"].default_value = 0.002
    L = nt.links.new
    L(noise.outputs["Fac"], ramp.inputs["Fac"])
    L(ramp.outputs["Color"], p.inputs["Base Color"])
    L(noise.outputs["Fac"], bump.inputs["Height"])
    L(bump.outputs["Normal"], p.inputs["Normal"])
    p.inputs["Roughness"].default_value = 0.8
    return m


def straw_material():
    m = bpy.data.materials.new("Straw")
    m.use_nodes = True
    p = m.node_tree.nodes["Principled BSDF"]
    p.inputs["Base Color"].default_value = (0.62, 0.45, 0.20, 1)
    p.inputs["Roughness"].default_value = 0.65
    return m


def emissive_material(name, color, strength):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    nt = m.node_tree
    nt.nodes.clear()
    out = nt.nodes.new("ShaderNodeOutputMaterial")
    em = nt.nodes.new("ShaderNodeEmission")
    em.inputs["Color"].default_value = (*color, 1.0)
    em.inputs["Strength"].default_value = strength
    nt.links.new(em.outputs["Emission"], out.inputs["Surface"])
    return m


# ----------------------------------------------------------------------------
# 지오메트리 노드 산포: 지면(빽빽) + 공중 층(드문드문)
# ----------------------------------------------------------------------------
def scatter_modifier(target, petal, density, seed, tilt, scale_min, scale_max, name):
    """target 메시의 면 위에 petal 오브젝트를 무작위 회전/크기로 인스턴싱한다."""
    tree = bpy.data.node_groups.new(name, "GeometryNodeTree")
    tree.interface.new_socket("Geometry", in_out="INPUT", socket_type="NodeSocketGeometry")
    tree.interface.new_socket("Geometry", in_out="OUTPUT", socket_type="NodeSocketGeometry")
    n_in = tree.nodes.new("NodeGroupInput")
    n_out = tree.nodes.new("NodeGroupOutput")
    dist = tree.nodes.new("GeometryNodeDistributePointsOnFaces")
    dist.distribute_method = "RANDOM"
    dist.inputs["Density"].default_value = density
    dist.inputs["Seed"].default_value = seed
    rot = tree.nodes.new("FunctionNodeRandomValue")
    rot.data_type = "FLOAT_VECTOR"
    rot.inputs[0].default_value = (-tilt, -tilt, 0.0)
    rot.inputs[1].default_value = (tilt, tilt, math.tau)
    rot.inputs[8].default_value = seed + 1
    scl = tree.nodes.new("FunctionNodeRandomValue")
    scl.data_type = "FLOAT"
    scl.inputs[2].default_value = scale_min
    scl.inputs[3].default_value = scale_max
    scl.inputs[8].default_value = seed + 2
    info = tree.nodes.new("GeometryNodeObjectInfo")
    info.inputs["Object"].default_value = petal
    info.inputs["As Instance"].default_value = True
    inst = tree.nodes.new("GeometryNodeInstanceOnPoints")
    L = tree.links.new
    L(n_in.outputs[0], dist.inputs["Mesh"])
    L(dist.outputs["Points"], inst.inputs["Points"])
    L(info.outputs["Geometry"], inst.inputs["Instance"])
    L(rot.outputs[0], inst.inputs["Rotation"])
    L(scl.outputs[1], inst.inputs["Scale"])
    L(inst.outputs["Instances"], n_out.inputs[0])
    mod = target.modifiers.new(name, "NODES")
    mod.node_group = tree
    return mod


def make_plane(name, size_x, size_y, loc):
    mesh = bpy.data.meshes.new(name)
    hx, hy = size_x / 2, size_y / 2
    mesh.from_pydata(
        [(-hx, -hy, 0), (hx, -hy, 0), (hx, hy, 0), (-hx, hy, 0)], [], [(0, 1, 2, 3)]
    )
    mesh.update()
    obj = bpy.data.objects.new(name, mesh)
    obj.location = loc
    bpy.context.collection.objects.link(obj)
    return obj


def make_air_layers(name, size, heights):
    verts, faces = [], []
    h = size / 2
    for k, z in enumerate(heights):
        b = len(verts)
        verts += [(-h, -h, z), (h, -h, z), (h, h, z), (-h, h, z)]
        faces.append((b, b + 1, b + 2, b + 3))
    mesh = bpy.data.meshes.new(name)
    mesh.from_pydata(verts, [], faces)
    mesh.update()
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.collection.objects.link(obj)
    return obj


# ----------------------------------------------------------------------------
# 빗자루 머리(짚 다발) : 왼쪽에서 들어오는 '위협'. 모션 블러용 2프레임 키.
# ----------------------------------------------------------------------------
def make_broom(location, direction_x=0.06):
    coll = bpy.data.collections.new("BroomHead")
    scene.collection.children.link(coll)
    mat = straw_material()
    curve = bpy.data.curves.new("Bristles", "CURVE")
    curve.dimensions = "3D"
    curve.bevel_depth = 0.0009
    curve.bevel_resolution = 2
    curve.fill_mode = "FULL"
    for _ in range(700):
        sp = curve.splines.new("BEZIER")
        sp.bezier_points.add(2)
        x0 = random.uniform(-0.015, 0.015)   # 두께(진행 방향)
        y0 = random.uniform(-0.09, 0.09)     # 폭(진행 방향에 수직)
        top = 0.16 + random.uniform(-0.01, 0.01)
        bend = random.uniform(0.0, 0.03)
        pts = [
            (x0, y0, top),
            (x0 + bend * 0.5, y0 + random.uniform(-0.005, 0.005), top * 0.5),
            (x0 + bend + random.uniform(-0.01, 0.01), y0 + random.uniform(-0.01, 0.01), random.uniform(0.0, 0.008)),
        ]
        for bp, co in zip(sp.bezier_points, pts):
            bp.co = co
            bp.handle_left_type = bp.handle_right_type = "AUTO"
    obj = bpy.data.objects.new("BroomHead", curve)
    obj.data.materials.append(mat)
    coll.objects.link(obj)
    obj.location = location
    obj.rotation_euler = (0.0, math.radians(-38.0), 0.0)  # 손잡이는 왼쪽 화면 밖으로 기울어짐
    obj.keyframe_insert("location", frame=1)
    obj.location = (location[0] + direction_x, location[1], location[2])
    obj.keyframe_insert("location", frame=2)
    return obj


# ----------------------------------------------------------------------------
# 씬 조립
# ----------------------------------------------------------------------------
petal = build_petal("Petal")
petal.data.materials.append(petal_material())
petal.hide_render = True  # 인스턴스 원본은 숨김
petal.location = (0, 0, -1.0)

ground = make_plane("Ground", 4.0, 4.0, (0, 1.0, 0))
ground.data.materials.append(ground_material())

carpet = make_plane("PetalCarpetZone", 1.6, 1.9, (0.0, 0.98, 0.0005))  # 렌즈 앞 3 cm는 비워 둔다
carpet.display_type = "WIRE"
carpet.hide_render = False
scatter_modifier(carpet, petal, density=9000.0, seed=args.seed, tilt=0.35,
                 scale_min=0.85, scale_max=1.15, name="GroundScatter")
# 카펫 자체 면은 렌더에서 보이지 않게: 노드 출력이 인스턴스만 내보내므로 원 면은 사라진다.

air = make_air_layers("AirLayers", 1.0, [0.02, 0.05, 0.09, 0.14, 0.2, 0.3, 0.42, 0.6])
air.location = (0.0, 0.62, 0.0)
scatter_modifier(air, petal, density=60.0, seed=args.seed + 10, tilt=math.pi,
                 scale_min=0.9, scale_max=1.1, name="AirScatter")

# 주인공 꽃잎: 렌즈 앞 6 cm, 역광을 받으며 떨어지는 중
hero = build_petal("HeroPetal")
hero.data.materials.append(petal.data.materials[0])
hero.location = (0.009, 0.078, 0.021)
hero.rotation_euler = (math.radians(58.0), math.radians(-18.0), math.radians(24.0))
hero.scale = (1.08, 1.08, 1.08)

if not args.no_broom:
    make_broom((-0.07, 0.15, 0.0), direction_x=0.02)

# 배경 보케용 발광 구 (벚나무 캐노피 느낌)
pink = emissive_material("BokehPink", (1.0, 0.62, 0.74), 9.0)
white = emissive_material("BokehWhite", (1.0, 0.94, 0.96), 12.0)
for i in range(70):
    bpy.ops.mesh.primitive_uv_sphere_add(
        radius=random.uniform(0.025, 0.07), segments=12, ring_count=8,
        location=(random.uniform(-1.6, 1.6), random.uniform(1.6, 3.2), random.uniform(0.15, 1.6)),
    )
    s = bpy.context.active_object
    s.data.materials.append(pink if random.random() < 0.7 else white)

# 조명: 낮은 역광 태양 + 분홍/하늘 그라데이션 월드
sun_data = bpy.data.lights.new("Sun", "SUN")
sun_data.energy = 3.2
sun_data.angle = math.radians(1.2)
sun_data.color = (1.0, 0.93, 0.85)
sun = bpy.data.objects.new("Sun", sun_data)
bpy.context.collection.objects.link(sun)
sun.rotation_euler = (math.radians(-64.0), 0.0, math.radians(18.0))

world = bpy.data.worlds.new("SpringWorld")
scene.world = world
world.use_nodes = True
wn = world.node_tree
wn.nodes.clear()
w_out = wn.nodes.new("ShaderNodeOutputWorld")
w_bg = wn.nodes.new("ShaderNodeBackground")
w_grad = wn.nodes.new("ShaderNodeTexGradient")
w_ramp = wn.nodes.new("ShaderNodeValToRGB")
w_co = wn.nodes.new("ShaderNodeTexCoord")
w_map = wn.nodes.new("ShaderNodeMapping")
w_map.inputs["Rotation"].default_value = (0.0, math.radians(90.0), 0.0)
w_ramp.color_ramp.elements[0].position = 0.45
w_ramp.color_ramp.elements[0].color = (0.95, 0.74, 0.80, 1)   # 지평선 분홍
w_ramp.color_ramp.elements[1].position = 0.75
w_ramp.color_ramp.elements[1].color = (0.62, 0.78, 0.98, 1)   # 봄 하늘
w_bg.inputs["Strength"].default_value = 0.7
wn.links.new(w_co.outputs["Generated"], w_map.inputs["Vector"])
wn.links.new(w_map.outputs["Vector"], w_grad.inputs["Vector"])
wn.links.new(w_grad.outputs["Fac"], w_ramp.inputs["Fac"])
wn.links.new(w_ramp.outputs["Color"], w_bg.inputs["Color"])
wn.links.new(w_bg.outputs["Background"], w_out.inputs["Surface"])

# 카메라: 지면 12 mm 높이, 50 mm, f/2.8, 주인공 꽃잎에 초점
cam_data = bpy.data.cameras.new("Cam")
cam_data.lens = 50.0
cam_data.sensor_width = 36.0
cam_data.dof.use_dof = True
cam_data.dof.aperture_fstop = 4.0
cam_data.clip_start = 0.002   # 기본 0.1 m이면 8 cm 앞 주인공 꽃잎이 잘린다
cam_data.dof.focus_object = hero
cam = bpy.data.objects.new("Cam", cam_data)
bpy.context.collection.objects.link(cam)
cam.location = (0.0, -0.02, 0.012)
cam.rotation_euler = (math.radians(91.0), 0.0, 0.0)  # 지면에서 살짝 올려다본다
scene.camera = cam

# ----------------------------------------------------------------------------
# 렌더 설정
# ----------------------------------------------------------------------------
scene.render.engine = "CYCLES"
scene.cycles.device = "CPU"
scene.cycles.samples = args.samples
scene.cycles.use_adaptive_sampling = True
scene.cycles.adaptive_threshold = 0.02
scene.cycles.use_denoising = True
scene.cycles.denoiser = "OPENIMAGEDENOISE"
scene.cycles.max_bounces = 6
scene.cycles.transmission_bounces = 4
scene.cycles.transparent_max_bounces = 8
scene.render.use_motion_blur = not args.no_broom
scene.render.motion_blur_shutter = 0.6
scene.render.resolution_x = 1280
scene.render.resolution_y = 720
scene.render.resolution_percentage = args.scale
scene.render.image_settings.file_format = "PNG"
scene.render.image_settings.color_mode = "RGB"
scene.view_settings.view_transform = "AgX"
scene.view_settings.look = "AgX - Medium High Contrast"
scene.view_settings.exposure = -0.35
scene.render.film_transparent = False
scene.frame_set(1)
scene.render.filepath = args.out
bpy.ops.render.render(write_still=True)
print("PoC 렌더 저장:", args.out)
