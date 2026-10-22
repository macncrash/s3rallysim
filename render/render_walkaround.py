"""Blender walkaround of the S3 Rally Pod, driven by the STEVE rally_stage animation.

Usage:
  blender -b -P render_walkaround.py -- <scene.json> <out.mp4>            # full 60 s video
  blender -b -P render_walkaround.py -- <scene.json> <out_dir> --stills   # one PNG per shot

scene.json comes from build_scene.py. Millimetres in, metres in Blender, Z up as in STEVE.
The occupants' eye views ride the moving floor, so the fixed screens move in them as they would
for the real crew.
The floor stack nests like the STEVE joints: surge -> heave -> pitch (Y, the crosshead's pin) -> roll (X, the
floor's pin), both about the universal joint; the yaw restraint's block rides the carriage, lifted with the floor's
tail pin. The four cranks and links are solved exactly every frame from the floor pose
(STEVE's own animation gears them with small-angle ratios). Screens, shell and doors stay put.
"""

import json
import math
import os
import sys

import bpy
from mathutils import Vector

argv = sys.argv[sys.argv.index("--") + 1:]
SCENE_JSON, OUT = argv[0], argv[1]
STILLS = "--stills" in argv

FPS = 24
SECONDS = 60
MM = 0.001

# Shots: name, start s, end s, camera, lens mm, hidden object-name prefixes.
# camera: ("orbit", radius, height, deg_from, deg_to), ("path", (from, to), (from, to)) in metres,
# or ("pov", who) at that occupant's eye, riding the moving floor.
HEAD = ("helmet", "visor", "chin", "boom_mic", "mic_capsule", "neck", "tether")
WALLS = ("shell.", "door", "window_", "bezel_")
COCKPIT = ("deck.", "driver.", "codriver.", "seat_", "mount_", "dash.", "wheel.", "pedals.", "footrest.", "tunnel.",
           "dogbox.", "dog_cap.", "lever.", "knob.", "handbrake.", "hb_lever.", "button_box.")
SHOTS = [
    ("orbit", 0, 9, ("orbit", 4.6, 2.1, 210, 330), 28, ()),
    ("driver_eye", 9, 18, ("pov", "driver"), 18, tuple("driver." + h for h in HEAD)),
    ("codriver_eye", 18, 26, ("pov", "codriver"), 18, tuple("codriver." + h for h in HEAD)),
    ("cutaway", 26, 35, ("path", ((1.9, -2.2, 1.9), (0.05, 0.0, 0.85)), ((2.2, -1.5, 1.6), (0.05, 0.0, 0.8))), 26,
     WALLS + ("windscreen", "mirror")),
    ("leg_room", 35, 43, ("path", ((0.1, 2.6, 0.95), (0.1, 0.3, 0.8)), ((0.3, 2.6, 0.9), (0.1, 0.3, 0.75))), 30,
     ("shell.wall_", "shell.post_fl", "shell.post_bl", "shell.jamb_a_l", "shell.jamb_b_l", "shell.header_l",
      "shell.rail_l", "shell.roof_l", "shell.step_", "shell.knuckle", "door.", "window_l", "bezel_l")),
    ("footwell", 43, 47, ("path", ((0.74, 0.02, 1.0), (0.42, 0.33, 0.62)), ((0.74, -0.05, 1.02), (0.42, 0.3, 0.6))),
     16, ()),
    # The motion platform with the floor and cockpit lifted away: drives, cranks, links, centre post.
    ("platform", 47, 55, ("path", ((1.5, -1.8, 0.85), (-0.35, 0.0, 0.2)), ((1.3, 1.9, 0.75), (-0.35, 0.0, 0.2))), 26,
     WALLS + ("windscreen", "mirror") + COCKPIT),
    ("finale", 55, 60, ("orbit", 5.0, 2.3, -30, 30), 28, ()),
]


def srgb(hex_color):
    h = hex_color.lstrip("#")
    out = []
    for i in (0, 2, 4):
        c = int(h[i:i + 2], 16) / 255
        out.append(c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4)
    return (*out, 1.0)


def make_material(key, color, kind):
    mat = bpy.data.materials.get(key)
    if mat:
        return mat
    mat = bpy.data.materials.new(key)
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes["Principled BSDF"]
    bsdf.inputs["Base Color"].default_value = srgb(color)
    if kind.startswith("glass") and not kind.startswith("glass-fibre"):
        # Game screens: lit panels, they also light the cockpit.
        bsdf.inputs["Emission Color"].default_value = srgb("#7fc4c8")
        bsdf.inputs["Emission Strength"].default_value = 2.5
        bsdf.inputs["Roughness"].default_value = 0.2
    elif kind.startswith("aluminum") or kind.startswith("steel"):
        bsdf.inputs["Metallic"].default_value = 0.7
        bsdf.inputs["Roughness"].default_value = 0.38
    else:
        bsdf.inputs["Roughness"].default_value = 0.55
    return mat


def smooth(x):
    x = max(0.0, min(1.0, x))
    return x * x * (3 - 2 * x)


def stage_values(t, keys, poses):
    duration = keys[-1][1]
    t = t % duration
    for (pa, ta), (pb, tb) in zip(keys, keys[1:]):
        if ta <= t <= tb:
            u = smooth((t - ta) / (tb - ta))
            a, b = poses[pa], poses[pb]
            names = ("surge_drive", "roll_drive", "pitch_drive", "heave_drive")
            return {n: a.get(n, 0) + (b.get(n, 0) - a.get(n, 0)) * u for n in names}
    return {"surge_drive": 0, "roll_drive": 0, "pitch_drive": 0, "heave_drive": 0}


def floor_point(p, pivot, heave, pitch_deg, roll_deg):
    """A floor point (mm) relative to the surge carriage for a floor pose: roll inside pitch, then heave."""
    a, r = math.radians(pitch_deg), math.radians(roll_deg)
    dx, dy, dz = p[0] - pivot[0], p[1], p[2] - pivot[2]
    y1 = dy * math.cos(r) - dz * math.sin(r)
    z1 = dy * math.sin(r) + dz * math.cos(r)
    x2 = dx * math.cos(a) + z1 * math.sin(a)
    z2 = -dx * math.sin(a) + z1 * math.cos(a)
    return (x2 + pivot[0], y1, z2 + pivot[2] + heave)


def solve_actuator(act, pivot, r, length, v):
    """Crank angle (rad, about +Y, + lowers the tip) and the link's tilt from upright (rad, same sense)."""
    pin = floor_point(act["pin"], pivot, v["heave_drive"], v["pitch_drive"], v["roll_drive"])
    ax = act["axis"]
    ddx, ddz = pin[0] - ax[0], pin[2] - ax[2]
    d = math.hypot(ddx, ddz)
    c = max(-1.0, min(1.0, (r * r + d * d - length * length) / (2 * r * d)))
    tip_ang = math.atan2(ddz, ddx) - math.acos(c)  # tip direction, counter-clockwise from +X in X-Z
    tip = (ax[0] + r * math.cos(tip_ang), ax[2] + r * math.sin(tip_ang))
    tilt = math.atan2(pin[0] - tip[0], pin[2] - tip[1])  # from +Z toward +X
    return -tip_ang, tilt


def look(cam, origin, target):
    cam.location = origin
    # Compatible with the last key so interpolation never spins through +-180 deg.
    quat = (Vector(target) - Vector(origin)).to_track_quat("-Z", "Y")
    cam.rotation_euler = quat.to_euler("XYZ", cam.rotation_euler)


def main():
    with open(SCENE_JSON) as fh:
        data = json.load(fh)

    bpy.ops.wm.read_factory_settings(use_empty=True)
    scene = bpy.context.scene
    scene.render.fps = FPS
    scene.frame_start = 1
    scene.frame_end = FPS * SECONDS
    scene.render.resolution_x = 1280
    scene.render.resolution_y = 720
    for engine in ("BLENDER_EEVEE_NEXT", "BLENDER_EEVEE"):
        try:
            scene.render.engine = engine
            break
        except TypeError:
            continue
    scene.eevee.taa_render_samples = 32
    scene.view_settings.look = "AgX - Medium High Contrast"

    # Floor stack empties, nested like the STEVE joints.
    def empty(name, parent, loc):
        e = bpy.data.objects.new(name, None)
        scene.collection.objects.link(e)
        e.parent = parent
        e.location = loc
        return e

    pivot = data["pivot"]
    surge = empty("surge", None, (0, 0, 0))
    heave = empty("heave", surge, (0, 0, 0))
    pitch = empty("pitch", heave, (pivot[0] * MM, 0, pivot[2] * MM))
    roll = empty("roll", pitch, (0, 0, 0))
    yaw = empty("yaw", surge, (0, 0, 0))
    stages = {"surge": surge, "heave": heave, "pitch": pitch, "roll": roll, "yaw": yaw}
    acts = data["actuators"]
    for act in acts:
        n = act["name"]
        stages["crank:" + n] = empty("crank_" + n, surge, tuple(c * MM for c in act["axis"]))
        stages["link:" + n] = empty("link_" + n, surge, tuple(c * MM for c in act["tip"]))
    bpy.context.view_layer.update()

    shell_objs = []
    for item in data["items"]:
        bpy.ops.wm.stl_import(filepath=item["file"], global_scale=MM)
        obj = bpy.context.selected_objects[0]
        obj.name = item["instance"] + "." + item["body"]
        mat = make_material(item["color"] + item["material"], item["color"], item["material"])
        obj.data.materials.append(mat)
        parent = stages.get(item["stage"])
        if parent:
            obj.parent = parent
            obj.matrix_parent_inverse = parent.matrix_world.inverted()
        if item["instance"] in ("shell", "door"):
            shell_objs.append(obj)

    # Ground, sky and lights.
    bpy.ops.mesh.primitive_plane_add(size=40, location=(0, 0, -0.001))
    ground = bpy.context.object
    ground.data.materials.append(make_material("ground", "#d9dcdf", "abs"))
    world = bpy.data.worlds.new("sky")
    world.use_nodes = True
    world.node_tree.nodes["Background"].inputs["Color"].default_value = srgb("#c9ced4")
    world.node_tree.nodes["Background"].inputs["Strength"].default_value = 0.9
    scene.world = world
    sun = bpy.data.lights.new("sun", "SUN")
    sun.energy = 3.0
    sun.angle = math.radians(8)
    sun_obj = bpy.data.objects.new("sun", sun)
    sun_obj.rotation_euler = (math.radians(50), math.radians(10), math.radians(35))
    scene.collection.objects.link(sun_obj)
    for name, loc, power in (("cabin", (0.1, 0.0, 1.45), 120), ("footwell", (0.15, 0.3, 0.9), 40)):
        light = bpy.data.lights.new(name, "POINT")
        light.energy = power
        light.shadow_soft_size = 0.3
        obj = bpy.data.objects.new(name, light)
        obj.location = loc
        scene.collection.objects.link(obj)

    # Motion: STEVE rally_stage, looped, keyed every frame; cranks and links solved exactly.
    anim = data["animations"]["rally_stage"]
    r, length = data["crank_r"], data["link_len"]
    for frame in range(scene.frame_start, scene.frame_end + 1):
        v = stage_values((frame - 1) / FPS, anim["keys"], data["poses"])
        surge.location.x = v["surge_drive"] * MM
        heave.location.z = v["heave_drive"] * MM
        roll.rotation_euler.x = math.radians(v["roll_drive"])
        pitch.rotation_euler.y = math.radians(v["pitch_drive"])
        surge.keyframe_insert("location", index=0, frame=frame)
        heave.keyframe_insert("location", index=2, frame=frame)
        roll.keyframe_insert("rotation_euler", index=0, frame=frame)
        pitch.keyframe_insert("rotation_euler", index=1, frame=frame)
        if "yaw_pin" in data:
            pin = data["yaw_pin"]
            yaw.location.z = (floor_point(pin, pivot, v["heave_drive"], v["pitch_drive"], v["roll_drive"])[2]
                              - pin[2]) * MM
            yaw.keyframe_insert("location", index=2, frame=frame)
        for act in acts:
            crank, tilt = solve_actuator(act, pivot, r, length, v)
            ce, le = stages["crank:" + act["name"]], stages["link:" + act["name"]]
            ce.rotation_euler.y = crank
            ax = act["axis"]
            le.location = ((ax[0] + r * math.cos(-crank)) * MM, act["tip"][1] * MM, (ax[2] + r * math.sin(-crank)) * MM)
            le.rotation_euler.y = tilt
            ce.keyframe_insert("rotation_euler", index=1, frame=frame)
            le.keyframe_insert("location", frame=frame)
            le.keyframe_insert("rotation_euler", index=1, frame=frame)

    # One camera per shot, switched by timeline markers; hidden bodies keyed per shot.
    eyes = data.get("eyes", {})
    scene.frame_set(1)  # floor at rest while cameras are parented to it
    objs = [o for o in scene.objects if o.type == "MESH"]
    centre = (0.0, 0.0, 0.8)
    for name, t0, t1, how, lens, hide in SHOTS:
        f0 = int(t0 * FPS) + 1
        f1 = int(t1 * FPS)
        cam_data = bpy.data.cameras.new(name)
        cam_data.lens = lens
        cam_data.clip_start = 0.02
        cam = bpy.data.objects.new(name, cam_data)
        scene.collection.objects.link(cam)
        if how[0] == "pov":
            if how[1] not in eyes:
                continue
            e = Vector(eyes[how[1]]) * MM
            origin = e + Vector((0.11, 0.0, 0.01))
            look(cam, origin, origin + Vector((1.0, -0.12 if how[1] == "driver" else 0.12, -0.12)))
            cam.parent = roll
            cam.matrix_parent_inverse = roll.matrix_world.inverted()
        else:
            for f in range(f0, f1 + 1, 2):
                u = (f - f0) / max(1, f1 - f0)
                if how[0] == "orbit":
                    _kind, radius, height, a0, a1 = how
                    ang = math.radians(a0 + (a1 - a0) * u)
                    origin = (centre[0] + radius * math.cos(ang), radius * math.sin(ang), height)
                    target = centre
                else:
                    s_ = smooth(u)
                    (a, ta), (b, tb) = how[1], how[2]
                    origin = tuple(a[i] + (b[i] - a[i]) * s_ for i in range(3))
                    target = tuple(ta[i] + (tb[i] - ta[i]) * s_ for i in range(3))
                look(cam, origin, target)
                cam.keyframe_insert("location", frame=f)
                cam.keyframe_insert("rotation_euler", frame=f)
        marker = scene.timeline_markers.new(name, frame=f0)
        marker.camera = cam
        for obj in objs:
            obj.hide_render = any(obj.name.startswith(h) for h in hide)
            obj.keyframe_insert("hide_render", frame=f0)
    scene.camera = scene.timeline_markers[0].camera

    if STILLS:
        os.makedirs(OUT, exist_ok=True)
        for name, t0, t1, *_ in SHOTS:
            scene.frame_set(int((t0 + t1) / 2 * FPS))
            scene.render.filepath = os.path.join(OUT, name + ".png")
            bpy.ops.render.render(write_still=True)
        return

    scene.render.image_settings.file_format = "FFMPEG"
    ff = scene.render.ffmpeg
    ff.format = "MPEG4"
    ff.codec = "H264"
    ff.constant_rate_factor = "HIGH"
    ff.gopsize = FPS
    ff.audio_codec = "NONE"
    scene.render.filepath = OUT
    bpy.ops.render.render(animation=True)


main()
