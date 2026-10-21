"""Write one STEVE static study (run_study's `study` JSON) for the moving floor, from floor_fea_loads.json.

Usage: python3 floor_fea_study.py floor_fea_loads.json <landing|combined|brake> [mesh_m] > study.json

Supports: the eight link clevis bores hold the floor vertically (the links are pinned at both ends, so
they carry only their axial load); the two universal-joint yoke bores hold it fore-aft and sideways (the
centre post's sleeve slides, so it carries no vertical load). The heave sleeve and spider hang on the yoke
bores. Each cockpit pad gets its force; the floor's own mass is the study's gravity.

The floor solid is cad/fea/floor_frame.py ("S3 Rally Pod floor (FEA)" in STEVE). Its 4 mm walls make a fine
mesh large: 12 mm needs more than STEVE's 8 GB, so the studies use 25 mm (default here). That resolves the
sheet's bending between tubes but not the peaks at bolt holes; see docs/floor-structure.md.
"""

import json
import sys


def study(loads, case, mesh_m):
    c = loads["cases"][case]
    clevis = [f"part:clevis_{n}_{s}_bore.side" for n in ("fl", "fr", "rl", "rr") for s in "ab"]
    yokes = ["part:yoke_l_bore.side", "part:yoke_r_bore.side"]
    b = [{"type": "fixed", "faces": clevis, "axes": [2]},
         {"type": "fixed", "faces": yokes, "axes": [0, 1]},
         {"type": "force", "faces": yokes, "force_n": [0, 0, round(2 * c["yoke_bores_z_N"], 1)]}]
    for pad, f in c["pads_N"].items():
        b.append({"type": "force", "faces": [f"part:pad_{pad}.top"], "force_n": f})
    return {"name": f"Floor, {case} ({loads['crew'].replace(' ', '')})",
            "analysis": {"type": "static", "gravity_m_s2": c["gravity_m_s2"]},
            "boundaries": b, "mesh": {"size_m": mesh_m}}


def main():
    with open(sys.argv[1]) as fh:
        loads = json.load(fh)
    mesh_m = float(sys.argv[3]) if len(sys.argv) > 3 else 0.025
    print(json.dumps(study(loads, sys.argv[2], mesh_m)))


if __name__ == "__main__":
    main()
