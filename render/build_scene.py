"""Build scene.json for render_walkaround.py from a STEVE design export.

Usage: python3 build_scene.py <steve_source_dir> <bodies_mesh_dir> <out.json>

steve_source_dir holds main.py, params.py, ergo.py and components/*.py of the S3 Rally Pod
(cad/pod in this repo).
bodies_mesh_dir is the unzipped bodies_mesh export (manifest.json + bodies/*.stl).
The STEVE source runs against stub classes that only record what it declares:
instance -> component, per-body colours, poses and the rally_stage animation.
"""

import json
import os
import sys
import types


class Face:
    def __init__(self, name):
        self.name = name


class Component:
    def __init__(self, cid, name=None):
        self.id = cid
        self.default = "#808080"
        self.colors = {}

    def material(self, _mat, bodies=None, color=None, **_kw):
        if color is None:
            return
        if bodies is None:
            self.default = color
        else:
            for body in bodies:
                self.colors[body] = color

    def face(self, name):
        return Face(name)

    def __getattr__(self, _name):
        return lambda *a, **k: None


class Design:
    def __init__(self, name):
        self.instances = {}
        self.poses = {}
        self.animations = {}

    def add(self, comp, name=None, at=None, **_kw):
        self.instances[name or comp.id] = comp

    def pose(self, name, **values):
        self.poses[name] = values

    def animation(self, name, keys, loop=False):
        self.animations[name] = {"keys": keys, "loop": loop}

    def __getattr__(self, _name):
        return lambda *a, **k: None


# Motion chain, outermost first. Instances not listed stay on the ground. Each crank and link is its
# own stage ("crank:fl", "link:fl"): the renderer solves them exactly from the floor pose.
CHAIN = {
    "surge": ["sled", "drive_fl", "drive_fr", "drive_rl", "drive_rr"],
    "heave": ["heave_car"],
    "roll": ["ujoint"],
    "pitch": [
        "deck", "seat_d", "seat_c", "mount_driver", "mount_codriver", "driver", "codriver", "wheel", "dash",
        "pedals", "footrest", "tunnel", "dogbox", "dog_cap", "lever", "knob", "handbrake", "hb_lever", "button_box",
    ],
}
ACTUATOR_STAGES = {p + "_" + n: p + ":" + n for n in ("fl", "fr", "rl", "rr") for p in ("crank", "link")}


def main():
    src, mesh_dir, out = sys.argv[1:4]
    stub = types.ModuleType("steve")
    stub.Component = Component
    stub.Design = Design
    sys.modules["steve"] = stub
    cq = types.ModuleType("cadquery")
    cq.Solid = types.SimpleNamespace(makeTorus=lambda *a, **k: None)
    cq.Vector = lambda *a: a
    sys.modules["cadquery"] = cq
    sys.path.insert(0, src)
    scope = {"__name__": "steve_main"}
    with open(os.path.join(src, "main.py")) as fh:
        exec(compile(fh.read(), "main.py", "exec"), scope)
    design = scope["design"]

    group = dict(ACTUATOR_STAGES)
    for stage, names in CHAIN.items():
        for name in names:
            group[name] = stage

    with open(os.path.join(mesh_dir, "manifest.json")) as fh:
        manifest = json.load(fh)
    items = []
    for item in manifest["items"]:
        comp = design.instances[item["instance"]]
        items.append({
            "file": os.path.join(mesh_dir, item["file"]),
            "instance": item["instance"],
            "body": item["body"],
            "material": item["material"],
            "color": comp.colors.get(item["body"], comp.default),
            "stage": group.get(item["instance"], "ground"),
        })
    ergo = sys.modules["ergo"]
    params = sys.modules["params"]
    motion = sys.modules["motion"]
    actuators = []
    for name, x, y in motion.ACTUATORS:
        side = 1 if y > 0 else -1
        actuators.append({"name": name, "axis": motion.crank_axis(x, y), "tip": motion.crank_tip(x, y),
                          "pin": motion.top_pin(x, y), "plane_y": y + side * motion.CRANK_DY})
    eyes = {"driver": ergo.posture(params.driver_pct, "driver")["eye"]}
    if ergo.rally:
        eyes["codriver"] = ergo.posture(params.codriver_pct, "codriver")["eye"]
    scene = {"items": items, "poses": design.poses, "animations": design.animations, "eyes": eyes,
             "pedals": ergo.HEEL, "wheel": [ergo.WHEEL_X_HOME, ergo.DRIVER_Y, ergo.WHEEL_Z],
             "pivot": [params.pivot_x, 0, params.pivot_z], "crank_r": params.crank_r,
             "link_len": params.link_len, "actuators": actuators}
    with open(out, "w") as fh:
        json.dump(scene, fh, indent=1)
    print(len(items), "bodies,", len(design.poses), "poses ->", out)


if __name__ == "__main__":
    main()
