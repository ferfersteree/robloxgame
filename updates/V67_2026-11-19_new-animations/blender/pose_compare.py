"""
Сравнение поз R15 в Blender: рисует каждую позу из JSON (вид 3/4 и сбоку) в превью.

  Blender -b -P pose_compare.py -- poses.json out_dir

poses.json: {"имя": {"Сустав": [x, y, z], ..., "root": [x, y, z]}, ...} в формате PoseData.luau.
Скелет, оси и рендер те же, что в r15_anims.py.
"""
import json, os, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import r15_anims as R  # noqa: E402


def main():
    argv = sys.argv[sys.argv.index("--") + 1:]
    poses = json.load(open(argv[0]))
    out = argv[1]
    os.makedirs(out, exist_ok=True)
    arm = R.build_rig(with_props=False)
    cams = R.setup_render()
    for name, pose in poses.items():
        # позы в прыжке: корень опускаем в кадр (форма тела не меняется, высота прыжка не видна)
        pose = dict(pose)
        r = pose.get("root", [0, 0, 0])
        pose["root"] = [r[0], min(r[1], 0.8), r[2]]
        R.apply_pose(arm, pose)
        for view in ("three_quarter", "side"):
            R.render_pose(cams, view, os.path.join(out, "%s_%s.png" % (name, view)))
    print("готово:", out)


main()
