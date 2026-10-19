"""Exact link and crank clearances over the motion platform's whole reachable workspace.

Usage: python3 platform_clearance.py <cad_source_dir>

STEVE animates the cranks and links with small-angle gearing, so its fit check sees each link
upright. This solves every link exactly (leaning from its crank tip to its floor pin) across a grid of
heave, pitch and roll, keeps the poses every crank can reach within +-65 deg, and reports:
- the reachable workspace (how much of each axis is available at the extremes of the others);
- the smallest gap between each link (rod and eyes) and the floor's under-frame tubes, in the
  floor's own frame;
- the lowest crank tip above the ground and the largest link lean.
"""

import itertools
import math
import sys

ROD_R, EYE_R = 13, 20


def box_distance(p, lo, hi):
    """Distance from point p to an axis-aligned box (0 inside)."""
    d = [max(lo[i] - p[i], 0, p[i] - hi[i]) for i in range(3)]
    return math.sqrt(sum(v * v for v in d))


def segment_box(a, b, lo, hi, steps=40):
    return min(box_distance([a[i] + (b[i] - a[i]) * k / steps for i in range(3)], lo, hi) for k in range(steps + 1))


def to_floor(pt, heave, pitch, roll, pivot):
    """Inverse of motion.floor_point: a carriage-frame point into the floor's rest frame."""
    p, r = math.radians(pitch), math.radians(roll)
    x, y, z = pt[0] - pivot[0], pt[1], pt[2] - pivot[2] - heave
    # Undo roll (about X), then pitch (about Y).
    y1 = y * math.cos(r) + z * math.sin(r)
    z1 = -y * math.sin(r) + z * math.cos(r)
    x2 = x * math.cos(p) - z1 * math.sin(p)
    z2 = x * math.sin(p) + z1 * math.cos(p)
    return (x2 + pivot[0], y1, z2 + pivot[2])


def main():
    sys.path.insert(0, sys.argv[1])
    import motion  # noqa: E402
    import params  # noqa: E402
    pivot = (params.pivot_x, 0, params.pivot_z)
    r, length = params.crank_r, params.link_len
    top = motion.DECK_BOT
    bot = top - motion.FRAME_H
    # Floor under-frame tubes, as built in components/deck.py.
    x0, x1, w = -940, 790, 660
    tubes = {
        "rear": ((x0, -w, bot), (x0 + 40, w, top)),
        "act_r": ((params.act_xr + 50, -w, bot), (params.act_xr + 90, w, top)),
        "act_f": ((params.act_xf - 130, -w, bot), (params.act_xf - 90, w, top)),
        "front": ((x1 - 40, -w, bot), (x1, w, top)),
    }
    reach = []
    worst = {"tube_gap": (1e9, None), "tip_low": (1e9, None), "lean": (0, None)}
    for h, p, ro in itertools.product(range(-40, 41, 5), [x * 0.5 for x in range(-14, 15)],
                                      [x * 0.5 for x in range(-14, 15)]):
        ok = True
        geo = []
        for name, x, y in motion.ACTUATORS:
            a = motion.crank_angle(x, y, h, p, ro)
            if a is None or abs(a) > 65:
                ok = False
                break
            ax = motion.crank_axis(x, y)
            tip = (ax[0] + r * math.cos(math.radians(-a)), y, ax[2] + r * math.sin(math.radians(-a)))
            pin = motion.floor_point(motion.top_pin(x, y), h, p, ro)
            geo.append((name, tip, pin))
        if not ok:
            continue
        reach.append((h, p, ro))
        for name, tip, pin in geo:
            lean = math.degrees(math.atan2(pin[0] - tip[0], pin[2] - tip[2]))
            if abs(lean) > worst["lean"][0]:
                worst["lean"] = (abs(lean), (name, h, p, ro))
            if tip[2] - EYE_R < worst["tip_low"][0]:
                worst["tip_low"] = (tip[2] - EYE_R, (name, h, p, ro))
            # Link from tip to pin, in the floor's frame, against the under-frame tubes.
            a_f, b_f = to_floor(tip, h, p, ro, pivot), to_floor(pin, h, p, ro, pivot)
            # The top eye sits in its clevis by design: stop the check one eye radius short of the pin.
            frac = 1 - (EYE_R + 2) / length
            b_f = tuple(a_f[i] + (b_f[i] - a_f[i]) * frac for i in range(3))
            for tname, (lo, hi) in tubes.items():
                gap = segment_box(a_f, b_f, lo, hi) - EYE_R
                if gap < worst["tube_gap"][0]:
                    worst["tube_gap"] = (gap, (name, tname, h, p, ro))

    def span(axis):
        vals = sorted({pt[axis] for pt in reach})
        return vals[0], vals[-1]

    print("reachable poses:", len(reach))
    print("heave range mm:", span(0), " pitch deg:", span(1), " roll deg:", span(2))
    for label, test in (("full roll (7) with heave", lambda q: abs(q[2]) == 7),
                        ("full pitch (7) with heave", lambda q: abs(q[1]) == 7),
                        ("full heave (40) with roll", lambda q: abs(q[0]) == 40)):
        sub = [q for q in reach if test(q)]
        if label.endswith("heave"):
            print(f"{label}: heave {min(q[0] for q in sub)}..{max(q[0] for q in sub)} mm" if sub else label + ": none")
        else:
            print(f"{label}: roll {min(q[2] for q in sub)}..{max(q[2] for q in sub)} deg" if sub else label + ": none")
    both = [q for q in reach if abs(q[1]) == 7 and abs(q[2]) == 7]
    print("full pitch and full roll together:", "reachable" if both else "not reachable",
          f"(at heave {sorted({q[0] for q in both})})" if both else "")
    print("smallest link-to-tube gap mm: %.1f at %s" % worst["tube_gap"])
    print("lowest crank tip (eye bottom) above ground mm: %.1f at %s" % worst["tip_low"])
    print("largest link lean deg: %.1f at %s" % worst["lean"])


if __name__ == "__main__":
    main()
