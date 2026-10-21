# S3 Rally Pod: floor, centre post and carriage structural check

Status, 2026-10-21. This covers open item 1 in [`two-seat-pod.md`](two-seat-pod.md) §7: the first STEVE structural
studies of the platform's load path, from the cockpit's bolts down to the surge rails. The geometry is main
revision 6.

**Verdict: the design as it stands is not ready.**

- **Floor:** the seat rails bolt to unsupported 4 mm sheet. A cross tube fixes that, and FE shows it works.
- **Centre post:** strong enough, but it stands on a carriage cross tube that twists. That makes the floor's
  fore-aft and sideways support soft enough to bring a structural mode down to about 7 Hz, inside the cueing band.
  Twin tubes help (about 12 Hz) but are not enough.
- **Universal joint and heave sleeve:** the CAD has no thrust faces on the pins and gives the sleeve 2 mm of radial
  clearance.

## 1. Method

STEVE's static studies solve one solid. So each structure is rebuilt as one welded solid in its own part
document, in the STEVE folder *S3 Rally Pod/FEA*. Each document's source is mirrored in `cad/fea/`.

| Part (STEVE) | Source | What it is | Idealisations |
|---|---|---|---|
| S3 Rally Pod floor (FEA) | `cad/fea/floor_frame.py` | `deck`: 4 mm sheet, 40 × 60 × 4 tubes, link clevises, upper yoke; 6061-T6 | Sheet welded or bonded to every tube. Steel yokes treated as aluminium. 1 mm pads where the cockpit bolts down. |
| S3 Rally Pod centre post (FEA) | `cad/fea/centre_post.py` | Heave column, sleeve and lower yoke, at the +40 mm heave stop (shortest engagement); S235JR | Sleeve bonded to the column over the engagement (the 2 mm clearance closed). Column held at its foot. |
| S3 Rally Pod carriage (FEA) | `cad/fea/carriage.py` | Carriage runners and cross tubes, column plate; 6061-T6 | Gearbox outriggers left out. Held at the four rail-block faces. |

**Fix switches.** Each part has switches for the fixes below, off by default. In STEVE the fixed variants were
solved at floor revision 5 and carriage revision 2. Both documents are back at the baseline now.

**Loads.** `analysis/floor_fea_loads.py` produces them, using the same masses and cueing targets as
`platform_loads.py`, for two 95th-percentile occupants and the 6.6 kg Heusinkveld pedal set.
- Each cockpit group's inertial load acts at its centre of mass. It is moved to its bolt pads as the force and
  couple those bolts would carry.
- The groups are: seat with rails and occupant, dash frame with wheel, pedal box, footrest, tunnel.

The three floor cases:

| Case | What it is |
|---|---|
| landing | 2 g vertical: gravity plus a 1 g heave kick |
| combined | 2 g vertical, 0.6 g surge, and 400 °/s² of roll and pitch, all at once |
| brake | 1 g, with the driver at the Heusinkveld's 180 kg brake maximum and the co-driver bracing at 1 kN |

**Floor supports.**
- The eight clevis bores hold the floor vertically: the links are pinned at both ends, so they carry only axial load.
- The two yoke bores hold it fore-aft and sideways: the sleeve slides, so it carries no vertical load.

**Generating studies.** `analysis/floor_fea_study.py` writes each floor study.

**Mesh.** The floor's 4 mm walls are the limit.
- A 12 mm mesh needs more than STEVE's 8 GB, so the floor studies use 25 mm quadratic tetrahedra.
- That resolves the sheet bending between tubes. It under-reads the peaks at the bolt pads, so the bolt-point
  numbers below are lower bounds.
- Every study's force and moment balance closed to below 1e-8.

## 2. Results

### Moving floor

| Case | Design | Peak von Mises | Where | Max displacement | Where |
|---|---|---|---|---|---|
| landing | as designed | 95 MPa | co-driver inner rear seat bolt | 3.81 mm | centre bay under both inner seat rails |
| landing | with fixes | 43 MPa | rear clevis bore (support edge) | 1.78 mm | front centre bay |
| combined | as designed | **108 MPa** | driver outer rear seat bolt | **3.84 mm** | centre seat bay |
| combined | with fixes | 43 MPa | — | 1.68 mm | front centre bay, under the dash's centre foot |
| brake | as designed | 59 MPa | — | 2.64 mm | front corner: the floor ahead of the front actuators |

**The seat rails are the problem.** The rails' rear bolts (x = -513) land on bare 4 mm sheet. They fall between
the rear actuator tube (x = -700) and the front one (x = 60), and the inner rails sit in the 620 mm bay between
the runners. A clamped-plate hand check gives about 140 MPa and 5.8 mm at the inner rear bolt in the landing case
(Roark, concentrated load on a 310 mm radius clamped plate). FE gives 95 MPa and 3.8 mm on its coarse mesh. They
agree on the picture: the sheet is acting as the structure. That is too soft for cueing, because the seat moves
4 mm against the motion, and too highly stressed for an aluminium sheet with bolt holes.
- **Fatigue:** with every cue cycle swinging the stress by about 100 MPa, the bolt holes would crack. A bolted
  aluminium detail is good for roughly 50 MPa of stress range at 2 million cycles.

**Fix A: a cross tube under the seats' rear bolts** (`seat_cross`).
- A 40 × 60 × 4 tube at x = -512. The rails' rear bolts fall on it for every occupant, because the rails are fixed
  in the floor frame. The front bolts already land on the front actuator-line tube.
- With it, the peaks drop from 108 to 43 MPa and the sag from 3.8 to 1.7 mm. What remains sits at the support
  bores and the front bay.
- It adds 3.1 kg, together with fix B.

**Fix B: clevis boxes** (`clevis_box`).
- As drawn, each link's two 8 mm clevis cheeks hang from the 4 mm sheet alone, 14 mm from a runner.
- The fix runs the cheeks back to the actuator-line tube and ties the inner cheek to the runner with a 6 mm web.
- **Honest note:** the FE does not show the clevises governing, so its effect isn't separated from fix A's. I
  still recommend it. The links reverse into 1.6 kN of tension, and a cheek-to-sheet weld under alternating load
  is a classic place for a fatigue crack to start.

**Still open: the front overhang.** The floor runs 620 mm ahead of the front actuators on a 60 mm deep frame.
- **Brake case:** the front corner drops 2.6 mm. The pedal box moves with the floor under a full brake press, and a
  load-cell brake will feel that.
- **Fixed floor, landing and combined:** the dash's centre foot, in the same bay, leaves about 1.7 mm.
- **Next fix to model:** a cross tube under the dash feet (x ≈ 272) and a deeper (80–100 mm) front frame or gussets.

### Centre post

**Load.** 3.40 kN fore-aft and 1.10 kN sideways at the joint, at the +40 mm heave stop. This is
`platform_loads.py`'s worst case: surge plus pitch and roll kicks.

**Result.**
- **50 MPa peak** at the root of the lower yoke lug (a sharp inside corner). A hand check gives about 38 MPa
  nominal: lug bending, M ≈ 3.4 kN × 45 mm on a 60 × 20 section.
- **0.06 mm** displacement.
- S235JR yield is 235 MPa, so the factor is 4.7 on yield. The steel post is fine; give the lug root a fillet.

**Two gaps in the CAD, not stress problems:**
1. **No thrust faces on the universal-joint pins.** The spider block is 50 mm wide, and the yoke lugs sit 130 mm
   apart, leaving 40 mm of air on each side.
   - The fore-aft load (3.4 kN) runs along the roll pin, and the sideways load (1.1 kN) along the pitch pin.
   - Nothing in the model carries either. The study assumed a thrust washer on the lug's inner face.
   - **Design them:** shouldered pins with thrust washers, or a spider that fills the gap.
2. **The heave sleeve has 2 mm of radial clearance on the column.** That is up to 2 mm of play, plus rocking, at
   the joint, right where every horizontal cue passes. It needs preloaded linear bearings, or adjustable bearing
   pads, on the column.

### Surge carriage (what the post stands on)

**Load.** The post's foot carries 1.03 kN·m about the lateral axis and 0.33 kN·m about the fore-aft axis, into a
200 × 200 × 12 aluminium plate on a single 60 × 60 × 5 cross tube.

| Design | Peak von Mises | Plate edge displacement | Rotation at the post (est.) | Joint deflection (est.) | Floor fore-aft mode (est.) |
|---|---|---|---|---|---|
| as designed: one cross tube twisting | **118 MPa** (tube-to-runner corner) | 1.37 mm | about 0.013 rad | about 4.5 mm | **about 7 Hz** |
| fix C: two cross tubes under the plate's edges (`twin_mid`) | 56 MPa | 0.42 mm | about 0.004 rad | about 1.4 mm | about 12 Hz |

**How the estimates were made.**
- **Rotation:** the plate-edge displacement divided by its 100 mm lever.
- **Joint deflection:** that rotation times the 344 mm from the tube to the joint at the top stop.
- **Floor fore-aft mode:** √(k/m) / 2π, with k = 3.4 kN over that deflection and m = 392 kg (floor and crew).
  Nothing else holds the floor fore-aft or sideways: the pinned links add almost no stiffness.

These are estimates, not a modal study of the assembly.

**Why this matters most.**
- **Strength:** 118 MPa sits at a weld. Welded 6061-T6 keeps only about 115 MPa (EN 1999 heat-affected-zone
  value), so the as-drawn carriage would yield there at the peak cue and crack in fatigue well before.
- **Stiffness:** the cue band reaches about 10 Hz, so the first structural mode should sit at 25–30 Hz or above.
  - That needs about 10 kN/mm at the joint: at most 0.35 mm of deflection at 3.4 kN.
  - Twin tubes reach 2.4 kN/mm, a quarter of that.
- **Next step:** brace the post directly to the carriage, so its moment goes into members in tension and
  compression. Options:
  - Diagonal struts from the column's upper end to the runners, fore and aft and to each side.
  - A steel box carriage centre in place of aluminium tube.
  - Lowering the joint to shorten the lever, if the cockpit allows it.

  Then confirm with a modal study of floor, post and carriage together.

## 3. What changes in the design

| # | Change | Status |
|---|---|---|
| A | Cross tube under the seat rails' rear bolts | FE-tested on the floor model; ready to put in `deck.py` |
| B | Clevis boxes tying each clevis to the actuator-line tube and the runner | Recommended (fatigue detail); in the FE model; not separately shown to be needed |
| C | Twin cross tubes under the column plate | FE-tested on the carriage model; a step, not enough on its own |
| D | Post bracing to reach 10 kN/mm at the joint | **To design**, then a modal study of the assembly |
| E | Thrust faces on both universal-joint pins | **To design** |
| F | Preloaded linear bearings, or adjustable pads, for the heave sleeve | **To design** (a bought part: add a card and a requirement) |
| G | Front-overhang stiffening: cross tube under the dash feet, deeper front frame | **To design**, then re-run the brake case |

**After A–G:**
1. Re-run `analysis/platform_clearance.py`. Fix A adds a tube under the floor at x = -512, and the floor must still
   clear the drives and links everywhere in the workspace.
2. Then re-run the fit check.

**Not covered here:**
- **Weld and bolt detail:** sizes, fatigue classes, preload.
- **The gearbox outriggers** that carry each crank's 3.7 kN and 460 N·m into the carriage.
- **The base frame.**
- **A modal study of the assembly.**
