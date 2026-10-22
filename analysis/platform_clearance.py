"""Exact link and crank clearances over the motion platform's whole reachable workspace.

Usage: python3 platform_clearance.py <cad_source_dir>

STEVE animates the cranks and links with small-angle gearing, so its fit check sees each link
upright. This solves every link exactly (leaning from its crank tip to its floor pin) across a grid of
heave, pitch and roll, keeps the poses every crank can reach within +-65 deg, and reports:
- the reachable workspace (how much of each axis is available at the extremes of the others);
- the smallest gap between each link (rod and eyes) and the floor's under-frame tubes, in the
  floor's own frame;
- the lowest crank tip above the ground, the largest link lean, and the gap between the floor's
  under-frame and the gearbox drives below it;
- the smallest gap between the heave guide's struts and column tops and the floor (plate and under-frame).
"""

import itertools
import math
import sys

ROD_R = 13


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
    # Undo pitch (about Y, the crosshead's pin), then roll (about X, the floor's pin).
    x1 = x * math.cos(p) - z * math.sin(p)
    z1 = x * math.sin(p) + z * math.cos(p)
    y2 = y * math.cos(r) + z1 * math.sin(r)
    z2 = -y * math.sin(r) + z1 * math.cos(r)
    return (x1 + pivot[0], y2, z2 + pivot[2])


def box_points(lo, hi, n=6):
    """Points on a box's surface: its corners, edges and faces on an n x n grid."""
    pts = []
    for i in range(n + 1):
        for j in range(n + 1):
            for k in range(n + 1):
                if 0 < i < n and 0 < j < n and 0 < k < n:
                    continue
                pts.append(tuple(lo[a] + (hi[a] - lo[a]) * (i, j, k)[a] / n for a in range(3)))
    return pts


def main():
    sys.path.insert(0, sys.argv[1])
    import motion  # noqa: E402
    import params  # noqa: E402
    import drive_parts  # noqa: E402
    from bought import LINK_ROD_END  # noqa: E402
    eye_r = LINK_ROD_END["eye_diameter_mm"] / 2
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
        "seat": ((-532, -w, bot), (-492, w, top)),
    }
    # The yoke mount (fix H): cross tubes either side of the joint, and the bars carrying the yoke lugs.
    for name, s_ in (("yoke_b", -1), ("yoke_f", 1)):
        xc = params.pivot_x + s_ * motion.UJ_TUBE_DX
        tubes[name] = ((xc - 20, -w, bot), (xc + 20, w, top))
    # The front overhang (fix G): front-bay cross tubes, the bars under the runners and the tubes under the edge tubes.
    for name, xc in zip(("dash", "pedal", "foot"), motion.FRONT_CROSS_X):
        tubes[name] = ((xc - 20, -w, bot), (xc + 20, w, top))
    for s_ in (1, -1):
        y0, y1 = sorted((s_ * 310, s_ * (310 + motion.FRONT_DEEP_BAR_W)))
        tubes["runner_deep" + str(s_)] = ((params.act_xf - 90, y0, bot - motion.FRONT_DEEP), (x1 - 40, y1, bot))
        y0, y1 = sorted((s_ * (w - 40), s_ * w))
        tubes["edge_deep" + str(s_)] = ((motion.FRONT_DEEP_EDGE_X, y0, bot - motion.FRONT_DEEP), (x1 - 40, y1, bot))
    # The 6 mm webs from each clevis's inner cheek to its runner (the cheeks themselves flank the link).
    for name, x, y in (("fl", params.act_xf, params.act_y), ("fr", params.act_xf, -params.act_y),
                       ("rl", params.act_xr, params.act_y), ("rr", params.act_xr, -params.act_y)):
        xa, xb = sorted((x + 30, params.act_xf - 90) if x == params.act_xf else (x - 30, params.act_xr + 50))
        ya, yb = sorted((y - (1 if y > 0 else -1) * 26, (1 if y > 0 else -1) * 350))
        tubes["web_" + name] = ((xa, ya, top - 6), (xb, yb, top))
    # The whole floor for the heave guide check: cross tubes, runners, edge tubes and the plate.
    floor = dict(tubes)
    for s_ in (1, -1):
        floor["runner" + str(s_)] = ((x0 + 40, min(s_ * 310, s_ * 350), bot), (x1 - 40, max(s_ * 310, s_ * 350), top))
        floor["edge" + str(s_)] = ((x0, min(s_ * (w - 40), s_ * w), bot), (x1, max(s_ * (w - 40), s_ * w), top))
    floor["plate"] = ((x0, -w, top), (x1, w, top + params.deck_t))
    # The floor's yoke lugs and their reach to the yoke tubes (fix H), and the yaw restraint's tail and clevis (fix I).
    for s_ in (1, -1):
        x0_, x1_ = sorted((params.pivot_x + s_ * (motion.UJ_LUG - motion.UJ_LUG_T / 2),
                           params.pivot_x + s_ * (motion.UJ_TUBE_DX - 20)))
        floor["yoke_reach" + str(s_)] = ((x0_, -30, bot), (x1_, 30, top))
    tail_z0 = params.pivot_z + 35
    floor["yaw_tail"] = ((motion.YAW_PIN_X - 30.5, -30, tail_z0), (x0, 30, tail_z0 + 40))
    floor["yaw_clevis"] = ((motion.YAW_PIN_X - 30.5, -30, params.pivot_z - 30), (motion.YAW_PIN_X + 24.5, 30, tail_z0))
    # Heave guide struts (axis segments) and column top corners, in the carriage frame (components/sled.py).
    struts, col_corners = [], []
    for s_ in (1, -1):
        y = s_ * motion.GUIDE_Y
        for bx in (160, -870):
            struts.append(((params.pivot_x, y, motion.STRUT_Z), (bx, s_ * motion.RAIL_Y, motion.SLED_TOP + motion.STRUT_R)))
        h = motion.GUIDE_COL / 2
        col_corners += [(params.pivot_x + dx, y + dy, motion.GUIDE_TOP) for dx in (-h, h) for dy in (-h, h)]
    # The yaw restraint's post and strut on the carriage (components/sled.py).
    h_ = motion.YAW_POST / 2
    post = ((motion.YAW_POST_X - h_, motion.YAW_POST_Y - h_ - motion.GUIDE_RAIL_H, motion.SLED_TOP),
            (motion.YAW_POST_X + h_, motion.YAW_POST_Y + h_, motion.YAW_POST_TOP))
    post_pts = box_points(*post)
    yaw_strut = ((motion.YAW_POST_X, motion.YAW_POST_Y + h_, motion.YAW_POST_TOP - 50),
                 (motion.YAW_POST_X, motion.RAIL_Y, motion.SLED_TOP + 21.2))
    floor_pts = {name: box_points(lo, hi, 4) for name, (lo, hi) in floor.items()}
    reach = []
    worst = {"yaw_post_gap": (1e9, None), "yaw_strut_gap": (1e9, None),
             "tube_gap": (1e9, None), "tip_low": (1e9, None), "lean": (0, None), "drive_gap": (1e9, None),
             "strut_gap": (1e9, None), "column_gap": (1e9, None)}
    # Drive tops (gearbox body and its mounting plate) under the floor's under-frame, per actuator.
    frame_bottom = motion.DECK_BOT - motion.FRAME_H
    drives = []
    for name, x, y in motion.ACTUATORS:
        s_ = 1 if y > 0 else -1
        ax = motion.crank_axis(x, y)
        plane = y + s_ * motion.CRANK_DY
        y0, y1 = plane + s_ * drive_parts.BODY_Y0, plane + s_ * drive_parts.BODY_Y1
        top = ax[2] + drive_parts.FRAME / 2 + 20  # mounting plate stands 20 above the gearbox
        # Only where the floor actually is: its frame ends at +-w and x0..x1.
        ys = [yy for yy in (y0, y1)]
        ys = [max(-w, min(w, yy)) for yy in ys]
        xs = [max(x0, min(x1, ax[0] + dx)) for dx in (-215, 215)]
        corners = [(xx, yy, frame_bottom) for xx in xs for yy in ys]
        drives.append((name, corners, top))
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
        for i, (a, b) in enumerate(struts):
            a_f, b_f = to_floor(a, h, p, ro, pivot), to_floor(b, h, p, ro, pivot)
            for fname, (lo, hi) in floor.items():
                gap = segment_box(a_f, b_f, lo, hi) - motion.STRUT_R
                if gap < worst["strut_gap"][0]:
                    worst["strut_gap"] = (gap, (i, fname, h, p, ro))
        for c in col_corners:
            c_f = to_floor(c, h, p, ro, pivot)
            for fname, (lo, hi) in floor.items():
                gap = box_distance(c_f, lo, hi)
                if gap < worst["column_gap"][0]:
                    worst["column_gap"] = (gap, (fname, h, p, ro))
        if h % 10 == 0 and p % 1 == 0 and ro % 1 == 0:
            for fname, (lo, hi) in floor.items():
                # The post (and its rail) against the floor, both ways round, and the strut against the floor.
                gap = min(min(box_distance(to_floor(q, h, p, ro, pivot), lo, hi) for q in post_pts),
                          min(box_distance(motion.floor_point(q, h, p, ro), *post) for q in floor_pts[fname]))
                if gap < worst["yaw_post_gap"][0]:
                    worst["yaw_post_gap"] = (gap, (fname, h, p, ro))
                a_f, b_f = (to_floor(q, h, p, ro, pivot) for q in yaw_strut)
                gap = segment_box(a_f, b_f, lo, hi) - 21.2
                if gap < worst["yaw_strut_gap"][0]:
                    worst["yaw_strut_gap"] = (gap, (fname, h, p, ro))
        for name, corners, top in drives:
            low = min(motion.floor_point(c, h, p, ro)[2] for c in corners)
            if low - top < worst["drive_gap"][0]:
                worst["drive_gap"] = (low - top, (name, h, p, ro))
        for name, tip, pin in geo:
            lean = math.degrees(math.atan2(pin[0] - tip[0], pin[2] - tip[2]))
            if abs(lean) > worst["lean"][0]:
                worst["lean"] = (abs(lean), (name, h, p, ro))
            if tip[2] - eye_r < worst["tip_low"][0]:
                worst["tip_low"] = (tip[2] - eye_r, (name, h, p, ro))
            # Link from tip to pin, in the floor's frame, against the under-frame tubes.
            a_f, b_f = to_floor(tip, h, p, ro, pivot), to_floor(pin, h, p, ro, pivot)
            # The top eye sits in its clevis by design: stop the check one eye radius short of the pin.
            frac = 1 - (eye_r + 2) / length
            b_f = tuple(a_f[i] + (b_f[i] - a_f[i]) * frac for i in range(3))
            for tname, (lo, hi) in tubes.items():
                gap = segment_box(a_f, b_f, lo, hi) - eye_r
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
    print("smallest floor-frame-to-drive gap mm: %.1f at %s" % worst["drive_gap"])
    print("smallest heave-guide-strut-to-floor gap mm: %.1f at %s" % worst["strut_gap"])
    print("smallest heave-guide-column-top-to-floor gap mm: %.1f at %s" % worst["column_gap"])
    print("smallest yaw-restraint-post-to-floor gap mm (10 mm / 1 deg grid): %.1f at %s" % worst["yaw_post_gap"])
    print("smallest yaw-restraint-strut-to-floor gap mm (10 mm / 1 deg grid): %.1f at %s" % worst["yaw_strut_gap"])


if __name__ == "__main__":
    main()
