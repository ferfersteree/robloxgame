"""
SpearHunt V67: новые клипы игрока (R15), собранные в Blender.

Запуск без окна:
  Blender -b -P r15_anims.py -- roundtrip     # проверка перевода осей на готовых позах игры
  Blender -b -P r15_anims.py -- build         # новые позы, .blend, превью, PoseData.luau

Формат игры (Shared/PoseData.luau): для каждого сустава три угла в градусах,
Transform = CFrame.fromEulerAnglesYXZ(rx, ry, rz); поле root = смещение корня в студах.
Оси: Roblox X вправо, Y вверх, Z назад (персонаж смотрит в -Z).
Blender: X вправо, Y назад (персонаж смотрит в -Y), Z вверх.
"""
import bpy, bmesh, math, os, re, sys, json
from mathutils import Matrix, Vector, Quaternion

HERE = os.path.dirname(os.path.abspath(__file__))
V61 = os.path.dirname(HERE)
REPO = os.path.dirname(os.path.dirname(V61))
# основа: PoseData.luau игры (V66, ветка donate-eggs); можно подменить переменной POSEDATA_SRC
POSEDATA_SRC = os.environ.get("POSEDATA_SRC") or os.path.join(REPO, "source", "ReplicatedStorage", "Shared", "PoseData.luau")
PREVIEWS = os.path.join(V61, "previews")
BLEND = os.path.join(HERE, "R15_NewAnimations.blend")
# пишет отдельный файл: в scripts/ лежит итоговый PoseData (там ещё новые позы броска ×100 hover/hover2)
OUT_LUAU = os.path.join(HERE, "PoseData_with_new_clips.luau")

JOINTS = ["Root", "Waist", "Neck", "LeftShoulder", "LeftElbow", "LeftWrist",
          "RightShoulder", "RightElbow", "RightWrist", "LeftHip", "LeftKnee", "LeftAnkle",
          "RightHip", "RightKnee", "RightAnkle"]

# Roblox (x, y, z) -> Blender (x, z, y). Матрица симметрична и равна своей обратной.
P = Matrix(((1, 0, 0), (0, 0, 1), (0, 1, 0)))


def rb(v):
    """вектор Roblox -> вектор Blender"""
    return Vector((v[0], v[2], v[1]))


# ---------------------------------------------------------------- скелет R15 (грубые пропорции в студах)
# имя: (голова, хвост, родитель)
BONES = {
    "Root": ((0, 2.2, 0), (0, 2.8, 0), None),
    "Waist": ((0, 2.8, 0), (0, 4.2, 0), "Root"),
    "Neck": ((0, 4.2, 0), (0, 5.4, 0), "Waist"),
    "LeftShoulder": ((-1.5, 3.9, 0), (-1.5, 2.9, 0), "Waist"),
    "LeftElbow": ((-1.5, 2.9, 0), (-1.5, 2.0, 0), "LeftShoulder"),
    "LeftWrist": ((-1.5, 2.0, 0), (-1.5, 1.5, 0), "LeftElbow"),
    "RightShoulder": ((1.5, 3.9, 0), (1.5, 2.9, 0), "Waist"),
    "RightElbow": ((1.5, 2.9, 0), (1.5, 2.0, 0), "RightShoulder"),
    "RightWrist": ((1.5, 2.0, 0), (1.5, 1.5, 0), "RightElbow"),
    "LeftHip": ((-0.5, 2.2, 0), (-0.5, 1.2, 0), "Root"),
    "LeftKnee": ((-0.5, 1.2, 0), (-0.5, 0.3, 0), "LeftHip"),
    "LeftAnkle": ((-0.5, 0.3, 0), (-0.5, 0.0, 0), "LeftKnee"),
    "RightHip": ((0.5, 2.2, 0), (0.5, 1.2, 0), "Root"),
    "RightKnee": ((0.5, 1.2, 0), (0.5, 0.3, 0), "RightHip"),
    "RightAnkle": ((0.5, 0.3, 0), (0.5, 0.0, 0), "RightKnee"),
}

# части для превью: имя: (центр, размер, кость, цвет)
SKIN = (0.96, 0.80, 0.45, 1)
BLUE = (0.10, 0.35, 0.75, 1)
BLUE_L = (0.25, 0.55, 0.95, 1)
GREEN = (0.30, 0.65, 0.25, 1)
GREEN_L = (0.50, 0.85, 0.40, 1)
PARTS = {
    "LowerTorso": ((0, 2.5, 0), (2, 0.6, 1), "Root", BLUE),
    "UpperTorso": ((0, 3.5, 0), (2, 1.4, 1), "Waist", BLUE),
    "Head": ((0, 4.85, 0), (1.2, 1.3, 1.2), "Neck", SKIN),
    "Nose": ((0, 4.8, -0.7), (0.25, 0.25, 0.25), "Neck", (0.9, 0.3, 0.2, 1)),
    "L_UpperArm": ((-1.5, 3.4, 0), (1, 1, 1), "LeftShoulder", SKIN),
    "L_LowerArm": ((-1.5, 2.45, 0), (0.95, 0.9, 0.95), "LeftElbow", SKIN),
    "L_Hand": ((-1.5, 1.75, 0), (0.9, 0.5, 0.9), "LeftWrist", (0.25, 0.25, 0.25, 1)),
    "R_UpperArm": ((1.5, 3.4, 0), (1, 1, 1), "RightShoulder", SKIN),
    "R_LowerArm": ((1.5, 2.45, 0), (0.95, 0.9, 0.95), "RightElbow", SKIN),
    "R_Hand": ((1.5, 1.75, 0), (0.9, 0.5, 0.9), "RightWrist", (0.9, 0.2, 0.2, 1)),
    "L_UpperLeg": ((-0.5, 1.7, 0), (1, 1, 1), "LeftHip", GREEN_L),
    "L_LowerLeg": ((-0.5, 0.75, 0), (0.95, 0.9, 0.95), "LeftKnee", GREEN_L),
    "L_Foot": ((-0.5, 0.15, -0.1), (1, 0.3, 1.2), "LeftAnkle", GREEN_L),
    "R_UpperLeg": ((0.5, 1.7, 0), (1, 1, 1), "RightHip", GREEN),
    "R_LowerLeg": ((0.5, 0.75, 0), (0.95, 0.9, 0.95), "RightKnee", GREEN),
    "R_Foot": ((0.5, 0.15, -0.1), (1, 0.3, 1.2), "RightAnkle", GREEN),
}
# реквизит только для превью (в игру не попадает)
PROPS = {
    "PotionBottle": ((1.5, 1.2, -0.1), (0.4, 0.6, 0.4), "RightWrist", (0.95, 0.15, 0.55, 1)),
    "PotionCork": ((1.5, 0.85, -0.1), (0.22, 0.15, 0.22), "RightWrist", (0.5, 0.35, 0.2, 1)),
}

rest3 = {}  # 3x3 матрица покоя каждой кости в пространстве арматуры


def clear_scene():
    bpy.ops.wm.read_factory_settings(use_empty=True)


def make_material(name, color):
    m = bpy.data.materials.new(name)
    m.diffuse_color = color
    return m


def build_rig(with_props=True):
    clear_scene()
    arm_data = bpy.data.armatures.new("R15")
    arm = bpy.data.objects.new("R15_Rig", arm_data)
    bpy.context.scene.collection.objects.link(arm)
    bpy.context.view_layer.objects.active = arm
    bpy.ops.object.mode_set(mode="EDIT")
    for name, (h, t, parent) in BONES.items():
        eb = arm_data.edit_bones.new(name)
        eb.head, eb.tail = rb(h), rb(t)
        eb.roll = 0
        if parent:
            eb.parent = arm_data.edit_bones[parent]
            eb.use_connect = False
    bpy.ops.object.mode_set(mode="OBJECT")
    for name in BONES:
        rest3[name] = arm_data.bones[name].matrix_local.to_3x3().copy()
    for pb in arm.pose.bones:
        pb.rotation_mode = "QUATERNION"
    parts = dict(PARTS)
    if with_props:
        parts.update(PROPS)
    for pname, (c, size, bone, color) in parts.items():
        bm = bmesh.new()
        bmesh.ops.create_cube(bm, size=1.0)
        for v in bm.verts:
            v.co = Vector((v.co.x * size[0], v.co.z * size[2], v.co.y * size[1])) + rb(c)
        me = bpy.data.meshes.new(pname)
        bm.to_mesh(me)
        bm.free()
        ob = bpy.data.objects.new(pname, me)
        bpy.context.scene.collection.objects.link(ob)
        ob.data.materials.append(make_material(pname, color))
        vg = ob.vertex_groups.new(name=bone)
        vg.add(list(range(len(me.vertices))), 1.0, "REPLACE")
        mod = ob.modifiers.new("Armature", "ARMATURE")
        mod.object = arm
        ob.parent = arm
    # пол
    floor = bpy.data.objects.new("Floor", bpy.data.meshes.new("Floor"))
    bm = bmesh.new()
    bmesh.ops.create_grid(bm, x_segments=1, y_segments=1, size=6)
    bm.to_mesh(floor.data)
    bm.free()
    floor.data.materials.append(make_material("Floor", (0.35, 0.35, 0.38, 1)))
    bpy.context.scene.collection.objects.link(floor)
    return arm


# ---------------------------------------------------------------- перевод углов
def roblox_euler_to_matrix(x, y, z):
    """CFrame.fromEulerAnglesYXZ(x, y, z) = Ry * Rx * Rz (градусы -> матрица Roblox)"""
    return (Matrix.Rotation(math.radians(y), 3, "Y") @ Matrix.Rotation(math.radians(x), 3, "X")
            @ Matrix.Rotation(math.radians(z), 3, "Z"))


def matrix_to_roblox_euler(R):
    """обратное: матрица Roblox -> (x, y, z) градусы для fromEulerAnglesYXZ"""
    x = math.asin(max(-1.0, min(1.0, -R[1][2])))
    if abs(R[1][2]) < 0.99999:
        y = math.atan2(R[0][2], R[2][2])
        z = math.atan2(R[1][0], R[1][1])
    else:
        y = math.atan2(-R[2][0], R[0][0])
        z = 0.0
    return (math.degrees(x), math.degrees(y), math.degrees(z))


def apply_pose(arm, pose):
    """pose: {сустав: [x, y, z], root: [x, y, z]} в формате PoseData"""
    for j in JOINTS:
        a = pose.get(j, (0, 0, 0))
        D_r = roblox_euler_to_matrix(*a)
        D_b = P @ D_r @ P
        R = rest3[j]
        basis = R.transposed() @ D_b @ R
        pb = arm.pose.bones[j]
        pb.rotation_quaternion = basis.to_quaternion()
        if j == "Root":
            t = pose.get("root", (0, 0, 0))
            pb.location = R.transposed() @ rb(t)
        else:
            pb.location = (0, 0, 0)
    bpy.context.view_layer.update()


def read_pose(arm):
    out = {}
    for j in JOINTS:
        pb = arm.pose.bones[j]
        R = rest3[j]
        basis = pb.rotation_quaternion.to_matrix()
        D_b = R @ basis @ R.transposed()
        D_r = P @ D_b @ P
        out[j] = matrix_to_roblox_euler(D_r)
        if j == "Root":
            t = P @ (R @ pb.location)
            out["root"] = (t[0], t[1], t[2])
    return out


# ---------------------------------------------------------------- чтение PoseData.luau
def parse_poses(path):
    txt = open(path, encoding="utf-8").read()
    body = txt[txt.index("\tposes = {"):]
    poses, cur = {}, None
    for line in body.splitlines()[1:]:
        m = re.match(r"^\t\t(\w+) = \{\s*$", line)
        if m:
            cur = {}
            poses[m.group(1)] = cur
            continue
        m = re.match(r"^\t\t\t(\w+) = \{\s*(-?[\d.]+),\s*(-?[\d.]+),\s*(-?[\d.]+)\s*\},?\s*$", line)
        if m and cur is not None:
            cur[m.group(1)] = [float(m.group(2)), float(m.group(3)), float(m.group(4))]
    return poses


# ---------------------------------------------------------------- превью
def setup_render():
    sc = bpy.context.scene
    sc.render.engine = "BLENDER_WORKBENCH"
    sc.display.shading.light = "STUDIO"
    sc.display.shading.color_type = "MATERIAL"
    sc.display.shading.show_cavity = False
    sc.render.resolution_x = sc.render.resolution_y = 360
    sc.render.film_transparent = False
    world = bpy.data.worlds.new("W")
    world.color = (0.62, 0.72, 0.85)
    sc.world = world
    tgt = bpy.data.objects.new("Target", None)
    tgt.location = (0, 0, 2.6)
    sc.collection.objects.link(tgt)
    cams = {}
    for name, loc in (("front", (0, -11, 3.0)), ("three_quarter", (7, -9, 4.2)), ("side", (11, 0, 3.0))):
        cd = bpy.data.cameras.new(name)
        cd.lens = 50
        co = bpy.data.objects.new(name, cd)
        co.location = loc
        sc.collection.objects.link(co)
        tc = co.constraints.new("TRACK_TO")
        tc.target = tgt
        tc.track_axis = "TRACK_NEGATIVE_Z"
        tc.up_axis = "UP_Y"
        cams[name] = co
    return cams


def render_pose(cams, view, path):
    sc = bpy.context.scene
    sc.camera = cams[view]
    sc.render.filepath = path
    bpy.ops.render.render(write_still=True)


# ---------------------------------------------------------------- новые клипы
# Все углы: градусы для fromEulerAnglesYXZ. Имена новых поз не пересекаются с PoseData.
def mirror(pose):
    """зеркало лево/право: меняем стороны, Y и Z меняют знак"""
    out = {}
    for k, v in pose.items():
        if k == "root":
            out[k] = [-v[0], v[1], v[2]]
            continue
        if k.startswith("Left"):
            nk = "Right" + k[4:]
        elif k.startswith("Right"):
            nk = "Left" + k[5:]
        else:
            nk = k
        out[nk] = [v[0], -v[1], -v[2]]
    return out


NEW_POSES = {}
NEW_CLIPS = {}


def define():
    # --- нейтральная стойка (начало и конец новых клипов)
    NEW_POSES["neutral"] = {
        "LeftShoulder": [0, 0, -6], "RightShoulder": [0, 0, 6],
        "LeftElbow": [8, 0, 0], "RightElbow": [8, 0, 0],
        "LeftHip": [0, 0, -2], "RightHip": [0, 0, 2],
        "root": [0, 0, 0],
    }
    # --- Wave: приветствие NPC (V53 диалоги)
    base = {"Neck": [-4, 18, 0], "Waist": [0, -8, 0],
            "LeftShoulder": [0, 0, -8], "LeftElbow": [8, 0, 0],
            "LeftHip": [0, 0, -3], "RightHip": [0, 0, 3],
            "RightShoulder": [-18, 0, 138], "root": [0, 0, 0]}
    NEW_POSES["waveUp"] = dict(base, RightElbow=[0, 0, 0], RightWrist=[0, 0, 0])
    NEW_POSES["waveL"] = dict(base, RightElbow=[0, 0, -30], RightWrist=[0, 0, -12])
    NEW_POSES["waveR"] = dict(base, RightElbow=[0, 0, 24], RightWrist=[0, 0, 12])
    NEW_CLIPS["Wave"] = {
        "keys": [(0, "neutral"), (0.25, "waveUp"), (0.5, "waveL"), (0.75, "waveR"), (1.0, "waveL"),
                 (1.25, "waveR"), (1.5, "waveL"), (1.85, "waveUp"), (2.2, "neutral")],
        "loop": False,
    }
    # --- DrinkPotion: зелья (V48)
    NEW_POSES["sipRaise"] = {
        "RightShoulder": [60, -20, 10], "RightElbow": [100, 0, 0], "RightWrist": [-20, 0, 0],
        "LeftShoulder": [0, 0, -8], "LeftElbow": [8, 0, 0],
        "Neck": [4, 0, 0], "Waist": [2, 0, 0], "LeftHip": [0, 0, -3], "RightHip": [0, 0, 3],
        "root": [0, 0, 0]}
    NEW_POSES["sipTilt"] = {
        "RightShoulder": [64, -22, 10], "RightElbow": [118, 0, 0], "RightWrist": [-30, 0, 0],
        "LeftShoulder": [0, 0, -8], "LeftElbow": [8, 0, 0],
        "Neck": [28, 0, 0], "Waist": [8, 0, 0], "LeftHip": [0, 0, -3], "RightHip": [0, 0, 3],
        "root": [0, 0, 0]}
    NEW_POSES["sipGulp"] = dict(NEW_POSES["sipTilt"], Neck=[22, 0, 0], root=[0, 0.05, 0])
    NEW_POSES["sipAhh"] = {
        "RightShoulder": [20, -10, 10], "RightElbow": [30, 0, 0],
        "LeftShoulder": [0, 0, -8], "LeftElbow": [8, 0, 0],
        "Neck": [-6, 0, 0], "Waist": [-4, 0, 0], "LeftHip": [0, 0, -3], "RightHip": [0, 0, 3],
        "root": [0, 0, 0]}
    NEW_CLIPS["DrinkPotion"] = {
        "keys": [(0, "neutral"), (0.4, "sipRaise"), (0.8, "sipTilt"), (1.3, "sipGulp"),
                 (1.7, "sipTilt"), (2.1, "sipAhh"), (2.6, "neutral")],
        "loop": False,
    }
    # --- EggReact: реакция на открытие яйца
    NEW_POSES["eggStartle"] = {
        "RightShoulder": [50, -40, 18], "RightElbow": [125, 0, 0], "RightWrist": [10, 0, 0],
        "LeftShoulder": [50, 40, -18], "LeftElbow": [125, 0, 0], "LeftWrist": [10, 0, 0],
        "Neck": [16, 0, 0], "Waist": [10, 0, 0],
        "LeftHip": [8, 0, -4], "RightHip": [8, 0, 4], "LeftKnee": [-12, 0, 0], "RightKnee": [-12, 0, 0],
        "root": [0, 0.4, 0.1]}
    NEW_POSES["eggLand"] = dict(NEW_POSES["eggStartle"], Neck=[8, 0, 0], Waist=[0, 0, 0],
                                LeftHip=[28, 0, -6], RightHip=[28, 0, 6],
                                LeftKnee=[-50, 0, 0], RightKnee=[-50, 0, 0],
                                LeftAnkle=[22, 0, 0], RightAnkle=[22, 0, 0],
                                root=[0, -0.3, 0])
    NEW_POSES["eggSqueal"] = {
        "RightShoulder": [30, -55, 22], "RightElbow": [135, 0, 0], "RightWrist": [0, 0, 0],
        "LeftShoulder": [30, 55, -22], "LeftElbow": [135, 0, 0], "LeftWrist": [0, 0, 0],
        "Neck": [-6, 0, 12], "Waist": [-8, 0, -4],
        "LeftHip": [10, 0, -4], "RightHip": [10, 0, 4], "LeftKnee": [-20, 0, 0], "RightKnee": [-20, 0, 0],
        "root": [0, -0.08, 0]}
    NEW_POSES["eggSquealB"] = dict(mirror(NEW_POSES["eggSqueal"]), root=[0, 0.12, 0])
    NEW_CLIPS["EggReact"] = {
        "keys": [(0, "neutral"), (0.18, "eggStartle"), (0.42, "eggLand"), (0.75, "eggSqueal"),
                 (1.0, "eggSquealB"), (1.25, "eggSqueal"), (1.5, "eggSquealB"), (2.0, "neutral")],
        "loop": False,
    }
    # --- Victory: Legendary и выше после раскрытия куста (петля)
    NEW_POSES["heroA"] = {
        "RightShoulder": [0, 0, 168], "RightElbow": [0, 0, 0], "RightWrist": [0, 0, 0],
        "LeftShoulder": [0, 0, -38], "LeftElbow": [0, 0, 88], "LeftWrist": [0, 0, 0],
        "Neck": [14, -12, 0], "Waist": [10, 8, -3],
        "LeftHip": [0, 0, -12], "RightHip": [0, 0, 12],
        "LeftKnee": [-4, 0, 0], "RightKnee": [-4, 0, 0],
        "root": [0, 0, 0]}
    NEW_POSES["heroB"] = dict(NEW_POSES["heroA"],
                              RightShoulder=[0, 0, 156], Neck=[18, -12, 0], Waist=[12, 8, -3],
                              LeftKnee=[-12, 0, 0], RightKnee=[-12, 0, 0], root=[0, 0.14, 0])
    NEW_CLIPS["Victory"] = {
        "keys": [(0, "heroA"), (0.7, "heroB"), (1.4, "heroA")],
        "loop": True,
    }


def fmt_num(x):
    r = round(x, 2)
    if r == int(r):
        return str(int(r))
    return ("%.2f" % r).rstrip("0").rstrip(".")


def lua_pose(name, pose):
    lines = ["\t\t%s = {" % name]
    for k in sorted(pose.keys(), key=lambda s: (s == "root", s)):
        v = pose[k]
        if all(abs(c) < 1e-6 for c in v) and k != "root":
            continue
        lines.append("\t\t\t%s = {%s, %s, %s}," % (k, fmt_num(v[0]), fmt_num(v[1]), fmt_num(v[2])))
    lines.append("\t\t},")
    return "\n".join(lines)


def lua_clip(name, clip):
    keys = ", ".join("{%s, \"%s\"}" % (fmt_num(t), p) for t, p in clip["keys"])
    lines = ["\t\t%s = {" % name, "\t\t\tkeys = {%s}," % keys]
    if clip.get("loop"):
        lines.append("\t\t\tloop = true,")
    lines.append("\t\t},")
    return "\n".join(lines)


def merged_posedata():
    src = open(POSEDATA_SRC, encoding="utf-8").read()
    taken = [n for n in list(NEW_POSES) + list(NEW_CLIPS) if re.search(r"^\t\t%s = \{" % n, src, re.M)]
    if taken:
        raise SystemExit("в %s уже есть %s: возьмите исходный PoseData без новых клипов (POSEDATA_SRC)" % (POSEDATA_SRC, taken))
    clips_new = "\n".join(lua_clip(n, c) for n, c in sorted(NEW_CLIPS.items())) + "\n"
    poses_new = "\n".join(lua_pose(n, p) for n, p in NEW_POSES.items()) + "\n"
    marker_clips = "\t},\n\tposes = {"
    assert src.count(marker_clips) == 1
    src = src.replace(marker_clips, clips_new + marker_clips)
    assert src.rstrip().endswith("\t},\n}")
    tail = src.rstrip()
    tail = tail[:-len("\t},\n}")] + poses_new + "\t},\n}\n"
    return tail


# ---------------------------------------------------------------- команды
def cmd_roundtrip():
    arm = build_rig(with_props=False)
    poses = parse_poses(POSEDATA_SRC)
    print("поз в PoseData:", len(poses))
    worst = 0.0
    worst_name = ""
    for name, pose in poses.items():
        apply_pose(arm, pose)
        back = read_pose(arm)
        err = 0.0
        for j in JOINTS:
            a = pose.get(j, (0, 0, 0))
            Ma, Mb = roblox_euler_to_matrix(*a), roblox_euler_to_matrix(*back[j])
            err = max(err, max(abs(Ma[i][k] - Mb[i][k]) for i in range(3) for k in range(3)))
        r0 = pose.get("root", (0, 0, 0))
        r1 = back["root"]
        err = max(err, max(abs(r0[i] - r1[i]) for i in range(3)))
        if err > worst:
            worst, worst_name = err, name
    print("наибольшая ошибка матриц после круга Roblox->Blender->Roblox: %.2e (поза %s)" % (worst, worst_name))
    cams = setup_render()
    os.makedirs(os.path.join(PREVIEWS, "_roundtrip"), exist_ok=True)
    for name in ("aim", "cheer", "watch", "release"):
        apply_pose(arm, poses[name])
        render_pose(cams, "three_quarter", os.path.join(PREVIEWS, "_roundtrip", name + ".png"))
    print("превью старых поз:", os.path.join(PREVIEWS, "_roundtrip"))


def setup_timeline(arm, cams):
    """все клипы подряд на одной шкале (NLA), метки с именами клипов, бутылка видна только в DrinkPotion"""
    sc = bpy.context.scene
    anim = arm.animation_data
    anim.action = None
    track = anim.nla_tracks.new()
    track.name = "Clips"
    gap = 20
    start = 1
    for cname in ("Wave", "DrinkPotion", "EggReact", "Victory"):
        act = bpy.data.actions[cname]
        strip = track.strips.new(cname, start, act)
        if NEW_CLIPS[cname].get("loop"):
            strip.repeat = 3
        length = strip.frame_end - strip.frame_start
        sc.timeline_markers.new(cname, frame=start)
        if cname == "DrinkPotion":
            potion_range = (start, start + length)
        start = int(start + length + gap)
    sc.frame_start, sc.frame_end = 1, start
    sc.frame_set(1)
    for pname in PROPS:
        ob = bpy.data.objects[pname]
        for f, hidden in ((1, True), (potion_range[0] - 1, True), (potion_range[0], False),
                          (potion_range[1] + 5, False), (potion_range[1] + 6, True)):
            ob.hide_viewport = ob.hide_render = hidden
            ob.keyframe_insert("hide_viewport", frame=f)
            ob.keyframe_insert("hide_render", frame=f)
    sc.camera = cams["three_quarter"]
    # при открытии: вид через камеру, цвета материалов, проигрывание по кругу
    for screen in bpy.data.screens:
        for area in screen.areas:
            if area.type == "VIEW_3D":
                for space in area.spaces:
                    if space.type == "VIEW_3D":
                        space.shading.type = "SOLID"
                        space.shading.color_type = "MATERIAL"
                        space.overlay.show_bones = False
                        if space.region_3d:
                            space.region_3d.view_perspective = "CAMERA"


def cmd_build():
    define()
    arm = build_rig(with_props=True)
    cams = setup_render()
    os.makedirs(PREVIEWS, exist_ok=True)
    # Blender-действия: по одному на клип, 30 кадров в секунду
    sc = bpy.context.scene
    sc.render.fps = 30
    anim = arm.animation_data_create()
    # хранение клипов как действий
    for cname, clip in NEW_CLIPS.items():
        act = bpy.data.actions.new(cname)
        anim.action = act
        for t, pname in clip["keys"]:
            apply_pose(arm, NEW_POSES[pname])
            f = 1 + round(t * 30)
            for pb in arm.pose.bones:
                pb.keyframe_insert("rotation_quaternion", frame=f)
                if pb.name == "Root":
                    pb.keyframe_insert("location", frame=f)
        act.use_fake_user = True
    anim.action = None
    # превью поз
    for pname, pose in NEW_POSES.items():
        apply_pose(arm, pose)
        render_pose(cams, "three_quarter", os.path.join(PREVIEWS, "pose_%s_34.png" % pname))
        render_pose(cams, "front", os.path.join(PREVIEWS, "pose_%s_front.png" % pname))
    # итог: PoseData.luau с добавками
    os.makedirs(os.path.dirname(OUT_LUAU), exist_ok=True)
    open(OUT_LUAU, "w", encoding="utf-8").write(merged_posedata())
    # JSON для проверки без Blender
    json.dump({"poses": NEW_POSES, "clips": {k: {"keys": v["keys"], "loop": v.get("loop", False)}
                                            for k, v in NEW_CLIPS.items()}},
              open(os.path.join(HERE, "new_anims.json"), "w"), indent=1)
    apply_pose(arm, NEW_POSES["neutral"])
    setup_timeline(arm, cams)
    bpy.ops.wm.save_as_mainfile(filepath=BLEND)
    print("готово:", BLEND, OUT_LUAU)


def smooth(u):
    u = max(0.0, min(1.0, u))
    return u * u * (3 - 2 * u)


def wrap(d):
    return (d + 180) % 360 - 180


def eval_clip(clip, t):
    """как evalClip в Client/Animator.luau: углы смешиваются по smoothstep между соседними ключами"""
    keys = clip["keys"]
    dur = keys[-1][0]
    if clip.get("loop"):
        t = t % max(dur, 1e-3)
    else:
        t = min(t, dur)
    for (ta, pa), (tb, pb) in zip(keys, keys[1:]):
        if t <= tb:
            u = smooth((t - ta) / max(tb - ta, 1e-3))
            A, B = NEW_POSES[pa], NEW_POSES[pb]
            break
    else:
        A = B = NEW_POSES[keys[-1][1]]
        u = 0
    out = {}
    for j in JOINTS + ["root"]:
        va, vb = A.get(j, (0, 0, 0)), B.get(j, (0, 0, 0))
        out[j] = [va[i] + (vb[i] - va[i]) * u for i in range(3)]
    return out


def cmd_gif():
    """кадры клипов так, как их проиграет игра (smoothstep + сглаживание 1-exp(-dt*20)), затем ffmpeg -> GIF"""
    define()
    arm = build_rig(with_props=True)
    cams = setup_render()
    fps = 30
    dt = 1.0 / fps
    a = 1 - math.exp(-dt * 20)
    for cname, clip in NEW_CLIPS.items():
        dur = clip["keys"][-1][0]
        total = dur * 2 if clip.get("loop") else dur + 0.5
        frames_dir = os.path.join(PREVIEWS, "_frames", cname)
        os.makedirs(frames_dir, exist_ok=True)
        for f in os.listdir(frames_dir):
            os.remove(os.path.join(frames_dir, f))
        cur = None
        n = int(round(total * fps))
        for i in range(n):
            target = eval_clip(clip, i * dt)
            if cur is None:
                cur = {k: list(v) for k, v in target.items()}
            else:
                for j in JOINTS:
                    for c in range(3):
                        cur[j][c] += wrap(target[j][c] - cur[j][c]) * a
                for c in range(3):
                    cur["root"][c] += (target["root"][c] - cur["root"][c]) * a
            apply_pose(arm, cur)
            render_pose(cams, "three_quarter", os.path.join(frames_dir, "f%04d.png" % i))
        print("кадров", cname, n)


if __name__ == "__main__":
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    {"roundtrip": cmd_roundtrip, "build": cmd_build, "gif": cmd_gif}[argv[0] if argv else "build"]()
