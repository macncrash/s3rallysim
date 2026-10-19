"""Sample the S3 Rally Pod CAD meshes into a point cloud and write the Gravity motion-cue sim.

Usage: python3 mesh_to_sim.py <scene.json> <template.js> <out.js> [points]

scene.json comes from render/build_scene.py (meshes, colours and which motion stage carries each
body). Points are spread over each body's surface by area, with extra weight on the parts that
matter for reading the cockpit (occupants, wheel, pedals). Positions are stored as int16 mm and
the stage of each point as a byte, base64-encoded into the template's /*POINTS*/ marker.
"""

import base64
import json
import random
import struct
import sys

STAGES = {"ground": 0, "surge": 1, "roll": 2, "pitch": 3, "heave": 4}
# Bodies drawn per square metre, by instance. Big flat panels get few points, people get many.
DENSITY = {"shell": 900, "door": 0, "door_r": 0, "windscreen": 2200, "window_l": 2200, "window_r": 2200,
           "driver": 30000, "codriver": 30000, "wheel": 40000, "pedals": 40000, "dash": 9000, "deck": 2500}
DEFAULT_DENSITY = 9000
SKIP_BODIES = ("wall_", "roof", "floor", "step_")  # skins would hide the cockpit


def read_stl(path):
    data = open(path, "rb").read()
    n = struct.unpack_from("<I", data, 80)[0]
    tris = []
    if 84 + n * 50 == len(data):
        for i in range(n):
            v = struct.unpack_from("<12f", data, 84 + i * 50)
            tris.append((v[3:6], v[6:9], v[9:12]))
        return tris
    pts = []
    for line in data.decode("ascii", "ignore").splitlines():
        parts = line.split()
        if parts[:1] == ["vertex"]:
            pts.append(tuple(float(p) for p in parts[1:4]))
    return [tuple(pts[i:i + 3]) for i in range(0, len(pts) - 2, 3)]


def area(t):
    a, b, c = t
    u = [b[i] - a[i] for i in range(3)]
    v = [c[i] - a[i] for i in range(3)]
    x = (u[1] * v[2] - u[2] * v[1], u[2] * v[0] - u[0] * v[2], u[0] * v[1] - u[1] * v[0])
    return 0.5 * (x[0] ** 2 + x[1] ** 2 + x[2] ** 2) ** 0.5


def sample(tri, rng):
    r1, r2 = rng.random(), rng.random()
    if r1 + r2 > 1:
        r1, r2 = 1 - r1, 1 - r2
    a, b, c = tri
    return tuple(a[i] + r1 * (b[i] - a[i]) + r2 * (c[i] - a[i]) for i in range(3))


def main():
    scene_path, template, out = sys.argv[1:4]
    total = int(sys.argv[4]) if len(sys.argv) > 4 else 24000
    scene = json.load(open(scene_path))
    rng = random.Random(7)
    wanted = []
    for item in scene["items"]:
        if item["instance"] == "shell" and item["body"].startswith(SKIP_BODIES):
            continue
        dens = DENSITY.get(item["instance"], DEFAULT_DENSITY)
        if dens <= 0:
            continue
        tris = read_stl(item["file"])
        areas = [area(t) for t in tris]
        a_m2 = sum(areas) * 1e-6
        if a_m2 <= 0:
            continue
        wanted.append((item, tris, areas, a_m2 * dens))
    scale = total / sum(w[3] for w in wanted)
    pos, stage, colour = bytearray(), bytearray(), bytearray()
    palette = []
    for item, tris, areas, w in wanted:
        n = max(8, int(round(w * scale)))
        c = item["color"].lstrip("#")
        rgb = tuple(int(c[i:i + 2], 16) for i in (0, 2, 4))
        # Very dark CAD colours would vanish on Gravity's black background: lift them.
        lift = max(0, 90 - max(rgb))
        rgb = tuple(min(255, v + lift) for v in rgb)
        if rgb not in palette:
            palette.append(rgb)
        ci = palette.index(rgb)
        cum, s = [], 0.0
        for a in areas:
            s += a
            cum.append(s)
        for _ in range(n):
            x = rng.random() * s
            lo, hi = 0, len(cum) - 1
            while lo < hi:
                mid = (lo + hi) // 2
                if cum[mid] < x:
                    lo = mid + 1
                else:
                    hi = mid
            p = sample(tris[lo], rng)
            pos += struct.pack("<3h", *(int(round(v)) for v in p))
            stage.append(STAGES[item["stage"]])
            colour.append(ci)
    count = len(stage)
    blob = {
        "count": count,
        "pos": base64.b64encode(bytes(pos)).decode(),
        "stage": base64.b64encode(bytes(stage)).decode(),
        "colour": base64.b64encode(bytes(colour)).decode(),
        "palette": [[round(v / 255, 3) for v in rgb] for rgb in palette],
    }
    src = open(template).read().replace("/*POINTS*/null", json.dumps(blob, separators=(",", ":")))
    src = src.replace("/*COUNT*/12000", str(count + 400))
    open(out, "w").write(src)
    print(count, "points,", len(palette), "colours,", len(src), "chars ->", out)


if __name__ == "__main__":
    main()
