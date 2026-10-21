# S3 Rally Pod: floor, heave guide and carriage structural check

Status, 2026-10-21. This covers open item 1 in [`two-seat-pod.md`](two-seat-pod.md) §7: the first STEVE structural
studies of the platform's load path, from the cockpit's bolts down to the surge rails. The studies in §2 are of
main revision 6. Fixes A–C went into main revision 8, and D and F (a new heave guide, §2.4) into revision 9.

**Verdict on revision 6: not ready.** Revision 9 fixes the floor and the joint's support. E and G are still open.

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

### Centre post (revision 6; replaced by the heave guide in revision 9)

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

### Surge carriage (what the post stands on, revision 6)

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

### Heave guide: fixes D and F together (main revision 9)

**Why the post could not just be braced.**
- **Sleeve in the way:** the heave sleeve slides on the outside of the post and reaches down to z = 240 at the
  −40 mm stop. A brace can only grab the post within 40–80 mm of its foot. That is far too short a lever against a
  joint 300 mm up.
- **Runners too soft:** the aluminium runners alone would rotate the post's foot by about 0.0012 rad under its
  1 kN·m. The whole budget for 10 kN/mm at the joint is about 0.0008 rad.
- **Too little engagement:** at the top stop the sleeve overlapped the post by only 40 mm. Even with preloaded
  bearings (fix F), that short a guide would have used most of the deflection budget.

**The new guide.**
- **Columns:** two fixed steel columns (100 × 100 × 8, S235) stand either side of the joint at y = ±215. Each sits
  on a foot plate across the twin mid tubes (fix C).
- **Struts:** each column is braced by two struts (CHS 60.3 × 5), from z = 360 on the column straight down to the
  surge rail blocks at x = 160 and −870. The joint's load reaches the rails as tension and compression, without
  bending the runners.
- **Crosshead:** the new `heave_car` carries the joint's lower yoke on a 30 mm bridge between two ears.
- **Guides:** each ear carries a guide rail running in two HIWIN HGW25CC blocks, fixed on the column's inner face
  between z = 207 and 415. It is the surge rails' block (`requirements/heave-guide.toml`, `bought.HEAVE_GUIDE`).
  The ears pass down between the twin mid tubes at the −40 mm stop.
- **Joint height:** the joint sits 79–159 mm above the block pair's centre across the heave stroke.
- **The sleeve and its 2 mm of play are gone.** This covers fix F.

**FE (STEVE part *S3 Rally Pod heave tower (FEA)*, `cad/fea/heave_tower.py`).**
- **Model:** the carriage, columns, struts and crosshead as one welded solid, at the +40 mm stop, held at the four
  surge blocks. The load is on the yoke lug bores.
- **One material:** a one-solid study takes one material. Steel overstates the aluminium carriage, and aluminium
  understates the steel tower. Displacement scales exactly with 1/E, so the two bound the real mix.
- **Guide blocks rigid:** the model treats the guide blocks as rigid; they are checked separately below.

| Load at the joint | All steel | All 6061 (lower bound) | Floor mode (est., 392 kg) |
|---|---|---|---|
| 3.4 kN fore-aft | 0.085 mm: 40 kN/mm | 0.259 mm: 13 kN/mm | 29–51 Hz |
| 1.1 kN sideways | 0.020 mm: 54 kN/mm | 0.062 mm (scaled): 18 kN/mm | 34–59 Hz |

- **Where the give is:** the largest movement is at the lug tops, from the crosshead's lugs and bridge bending.
  The braced columns barely move.
- **Stress:** 27 MPa peak in steel at the fore-aft load.
- **Guide blocks.** Fore-aft, the joint's load reaches the four blocks as lateral force plus a moment. The moment
  arm is up to 159 mm above a 104 mm block pair. That gives about 0.39 × k at the joint, where k is one block's
  rigidity (block moment rigidity ignored, which is conservative).
  - Against the all-aluminium lower bound, a 25 Hz floor needs k ≥ 100 N/µm per block.
  - That value is not on the HIWIN card. It is a CHECK in `requirements/heave-guide.toml` and a question for
    HIWIN at ZA preload.
- **Load on each block:** about 3.4 kN at most, against C0 = 52.8 kN.

**Fit.**
- **Exact clearance:** `analysis/platform_clearance.py` now checks the struts and column tops against the floor's
  plate and under-frame over the whole reachable workspace.
  - The struts clear by 29.7 mm at least, nearest the seat cross tube at −40 mm heave and full roll.
  - The column tops clear the plate by 16.5 mm.
- **STEVE fit checks:** see §3.

## 3. What changes in the design

| # | Change | Status |
|---|---|---|
| A | Cross tube under the seat rails' rear bolts | FE-tested on the floor model; **in the design** (`deck.py`, main revision 8) |
| B | Clevis boxes tying each clevis to the actuator-line tube and the runner | Recommended (fatigue detail); not separately shown to be needed; **in the design** (`deck.py`, revision 8) |
| C | Twin cross tubes under the column plate | FE-tested on the carriage model; a step, not enough on its own; **in the design** (`sled.py`, revision 8) |
| D | Bracing to reach 10 kN/mm at the joint | **In the design** (main revision 9): braced twin-column heave guide, 13–40 kN/mm fore-aft by FE |
| E | Thrust faces on both universal-joint pins | **To design** |
| F | Preloaded linear bearings for the heave guide | **In the design** (revision 9): HGW25CC blocks, two per column; block rigidity to confirm with HIWIN |
| G | Front-overhang stiffening: cross tube under the dash feet, deeper front frame | **To design**, then re-run the brake case |

**A–C in the design (main revision 8).**
- **Cheek lengths:** in `deck.py` each cheek stops at its actuator-line tube's face: 120 mm long at the front, 80 mm
  at the rear. The FE model ran the rear ones 40 mm into the tube, which only adds overlap inside it.
- **Carriage:** the surge-nut bracket stays where it was, now under the rear mid tube's front edge. Moving it
  further aft hits the surge actuator body at full rear surge (the fit check caught it).
- **Clearance:** `analysis/platform_clearance.py` now checks the links against the seat tube and the four webs as
  well. Every number it reports is unchanged. The seat tube clears the links by at least 210 mm and the webs by
  44 mm across the whole workspace.

**After E and G:** re-run `analysis/platform_clearance.py` and the fit check, then run a modal study of floor,
guide and carriage together.

**Not covered here:**
- **Weld and bolt detail:** sizes, fatigue classes, preload.
- **The gearbox outriggers** that carry each crank's 3.7 kN and 460 N·m into the carriage.
- **The base frame.**
- **A modal study of the assembly.**
