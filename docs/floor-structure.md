# S3 Rally Pod: floor, heave guide and carriage structural check

Status, 2026-10-21. This covers open item 1 in [`two-seat-pod.md`](two-seat-pod.md) §7: the first STEVE structural
studies of the platform's load path, from the cockpit's bolts down to the surge rails. The studies in §2 are of
main revision 6. Fixes A–C went into main revision 8, D and F (a new heave guide, §2.4) into revision 9, E into
revision 10, H into revision 11 and G into revision 13.

**Verdict on revision 6: not ready.** Revisions 8–13 put in every fix, A to H.
- **Fore-aft and sideways:** now about 22–39 and 25–44 Hz (modal study, 6061 and steel bounds), against a
  25–30 Hz target.
- **Floor yaw:** the one mode still low, at about 6–11 Hz. A driver alone does excite it: a sharp surge onset
  leaves a sideways shimmy at the seat 10–60 times the threshold of perception (§2.5). Still open.
- **Brake case:** the front overhang now drops 1.4 mm (was 2.4).

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
- **Guide blocks.** The model above holds them rigid; here is their own give.
  - **Directions:** the blocks' mounting faces face the crosshead. Fore-aft, the joint's load reaches them
    across the rail: lateral force, plus a moment with the joint up to 159 mm above a 104 mm block pair. Sideways,
    it reaches them radially (one column radial, the other reverse radial).
  - **At the joint:** about 0.39 × k, where k is one block's stiffness in that direction (block moment rigidity
    ignored, which is conservative).
  - **Needed for 25 Hz** against the all-aluminium bounds: lateral k ≥ 100 N/µm (fore-aft, governing), radial
    k ≥ 55 N/µm (sideways).
  - **HIWIN's figure:** the catalogue (G99TE22-2011, Table 2-1-13, PDF p. 30) gives HG25C radial stiffness
    292 N/µm at Z0, 539 at ZA and 705 at ZB. The design orders ZA, which passes radial nearly ten times over.
  - **Lateral is not printed.** The catalogue only says the four-row, 45° design has equal load ratings and
    "high rigidity in all four directions". Lateral would have to be below 19 % of the radial figure to miss 25 Hz.
    It is a CHECK in `requirements/heave-guide.toml`, to confirm with HIWIN when ordering.

| Floor mode with the blocks' give (est., 392 kg) | Rigid blocks | ZA, lateral = radial (539 N/µm) | Lateral at Z0's 292 N/µm |
|---|---|---|---|
| Fore-aft (13–40 kN/mm tower) | 29–51 Hz | 28–47 Hz (12–34 kN/mm) | 27–44 Hz |
| Sideways (18–54 kN/mm tower) | 34–59 Hz | 33–53 Hz (17–43 kN/mm) | 32–49 Hz |

- **Load on each block:** about 3.4 kN at most, against C0 = 52.8 kN.

**Fit.**
- **Exact clearance:** `analysis/platform_clearance.py` now checks the struts and column tops against the floor's
  plate and under-frame over the whole reachable workspace.
  - The struts clear by 29.7 mm at least, nearest the seat cross tube at −40 mm heave and full roll.
  - The column tops clear the plate by 16.5 mm.
- **STEVE fit checks:** see §3.

### Modal study: floor, joint, heave guide and carriage together (main revision 10)

**Model (STEVE part *S3 Rally Pod platform (modal)*, `cad/fea/platform_modal.py`).**
- **One solid:** the floor (with fixes A and B), the universal joint, the crosshead, the braced columns and the
  carriage, at the +40 mm heave stop.
- **Joint:** each pin is a short 16 mm rod, which passes force like the bushings but lets the floor roll and pitch.
  The spider holds yaw, as the real joint does.
- **Mass:** the cockpit and crew are two steel blocks on posts at the seat-rail pads. Everything the links carry
  weighs 391.5 kg (crew 95 + 95, `platform_loads.json`).
- **Supports:**
  - **Links:** the clevis bores are held vertically only, so roll, pitch and heave are taken by the links.
  - **Carriage:** the rail blocks are held sideways and vertically, and the ballscrew nut fore-aft.
- **Material:** one material at steel's density. Every frequency scales exactly with √E, so the 6061 bound is
  0.57 × the steel figure. The real floor is 6061 and the tower steel.
- **Mesh:** 30 mm. A 15 mm mesh needs more than STEVE's 8 GB, so these frequencies are not converged. A coarse mesh
  reads high, so the real figures are lower.

| Mode | All steel | 6061 bound | Moves | Shape |
|---|---|---|---|---|
| 1 | 5.5 Hz | 3.1 Hz | almost no fore-aft or side mass | the floor **yaws** about the joint; the tower barely moves |
| 2 | 25.3 Hz | 14.5 Hz | 73 % of the mass sideways | floor slides sideways on the joint |
| 3 | 25.4 Hz | 14.5 Hz | 80 % of the mass fore-aft | floor slides fore-aft on the joint |
| 4–9 | 61–115 Hz | 35–66 Hz | little | local: payload posts, floor panels |
| 10–12 | 115–143 Hz | 66–82 Hz | vertical | floor bending between the links |

**What it shows.**
- **The heave tower is no longer the weak link.** In modes 1–3 the columns, struts and carriage barely move.
- **The floor's joint mount is.** The upper yoke's two lugs hang from the bare 4 mm floor sheet, in a bay
  with the nearest frame tubes 210 mm fore and aft (seat and front actuator tubes) and 330 mm to each side
  (runners).
  - **Fore-aft and sideways:** the joint's force acts 102 mm below the sheet, so the lugs bend the sheet locally
    and the floor slides on the joint.
  - **Yaw:** only that sheet resists it, at about 3–6 Hz.
- **Below target in every direction:** fore-aft and sideways come in at about 15–25 Hz, against the 25–30 Hz target.
  The real floor is aluminium, so the truth is nearer the 6061 bound, and lower again once the mesh converges.
- **Why the static estimates missed it:** the 29–51 Hz figures (§2.4) held the floor rigid.
- **What is left out:**
  - **Link stiffness:** the links get some horizontal stiffness from their lean and the crank drives. That would
    raise mode 1 somewhat, but it depends on the servo loop.
  - **Joint play:** bushing clearance would lower every mode.

**With fix H (modal part revision 3: yoke cross tubes 140 mm either side of the joint).**

| Mode | All steel | 6061 bound | Moves | Shape |
|---|---|---|---|---|
| 1 | 11.2 Hz | 6.4 Hz | almost no fore-aft or side mass | floor yaws about the joint |
| 2 | 39.0 Hz | 22.3 Hz | 93 % of the mass fore-aft | floor slides fore-aft on the joint |
| 3 | 44.4 Hz | 25.4 Hz | 83 % of the mass sideways | floor slides sideways |
| 4–12 | 69–167 Hz | 40–96 Hz | little, or vertical | local modes, floor bending between the links |

- **Fore-aft and sideways:** H lifts them by 55–75 %. The truth lies between the bounds: the floor is 6061, the
  tower steel.
- **Yaw:** doubles, but stays at 6–11 Hz.
  - **Not the pin rods:** making the joint's pin rods nearly rigid (a test run) only lifts it to 13.5 Hz.
  - **Where the give is:** the rest is split between the heave tower's yaw path (the crosshead pushing one
    column forward and the other back) and the floor around the yoke.
- **Does yaw matter?** No cue drives yaw directly. An off-centre crew does couple surge into it: a driver alone
  puts the centre of mass well to one side. Before adding steel, check that coupling in the Gravity sim or a
  frequency-response study.
- **Next if it does:**
  - **Tower:** tie the two column tops together fore and aft of the crosshead.
  - **Floor:** a torsion box around the yoke.
- **Not re-run with G:** G mostly stiffens the front overhang vertically, so modes 1–3 should barely change.

**Yaw check: does an off-centre crew excite it?** (`analysis/yaw_check.py`)
- **Model:** the floor as a rigid body on one yaw spring.
  - **Stiffness:** a STEVE static study of the modal part (a 1,320 N·m couple on the floor's sides) gives
    k = 5.5 × 10⁵ N·m/rad in steel. The front corner moves 3.04 mm, which matches the modal frequency.
  - **The joint model:** the 16 mm pin rods take a fair share of that give (245 MPa peak in one rod). The real
    30 mm pins in bushings sit between the rods and the rigid-pin test (8.1 × 10⁵ N·m/rad). Both are used, and
    6061 scales each by 69/210.
  - **Damping:** 2 %.
  - **Inertia:** each crew's yaw inertia comes from the CAD mesh and the occupant model, plus fixes G and H.
- **Excitation:** the crew's centre of mass is off the joint, so the cue limits in `platform_loads.py` (0.6 g
  surge, 400°/s² roll and pitch) twist the floor.
- **Measures:** the false sideways acceleration at the seats, against about 0.015 m/s² (perception, ISO 2631-1
  Annex C).
  - **Onset:** the ringing after a jerk-limited 0.6 g surge onset.
  - **Resonance:** the response per 0.1 g of surge content at the yaw frequency.

| Crew | CoM off the joint, sideways | Yaw frequency | Ringing after a 0.6 g surge onset, 50 ms / 100 ms rise | At resonance, per 0.1 g of surge |
|---|---|---|---|---|
| 95 + 95 | 12 mm | 6.5–13.7 Hz | 0.04–0.09 / 0.01–0.05 m/s² | 0.44 m/s² |
| 95 + 5 | 71 mm | 6.9–14.5 Hz | 0.19–0.47 / 0.09–0.22 m/s² | 2.4 m/s² |
| 95 alone | 146 mm | 7.2–15.1 Hz | 0.32–0.87 / 0.16–0.37 m/s² | 4.5 m/s² |
| 5 alone | 100 mm | 7.7–16.2 Hz | 0.13–0.46 / 0.05–0.16 m/s² | 2.5 m/s² |

- **Verdict: yes, a driver alone excites it.**
  - **Brake or launch onset:** after a sharp onset the seat shimmies sideways at 7–15 Hz, 10–60 times the
    threshold of perception. The shimmy dies away over about half a second to a second.
  - **Road texture:** any surge, pitch or roll content near the yaw frequency is amplified about 25-fold.
  - **Full crew:** a balanced 95 + 95 crew is near the threshold.
- **Why it is worse alone:** the crew's centre of mass sits 146 mm to the driver's side.
- **Left out:**
  - **Link stiffness:** the links' horizontal stiffness (they stand near vertical at rest) would raise the
    frequency a little.
  - **Joint play:** bushing play would add a knock on top.
  - **Product-of-inertia terms:** the crew's distributed products of inertia are not modelled.
- **Ways out, cheapest first:**
  1. **Cue shaping:** limit surge, pitch and roll onsets to a rise time of 1/f or more, and notch the
     command around the yaw frequency.
     - **Cost:** cheap, but the yaw frequency moves from 7 to 16 Hz with the crew and the material bounds.
     - **Limit:** it does nothing for road texture in that band.
  2. **Stiffen the structure:** a column-top tie and a torsion box round the yoke. Reaching 25 Hz needs about
     2.7 × 10⁶ N·m/rad, 3–5 times today's steel bound, so these alone probably will not get there.
  3. **A yaw restraint at the floor's front:** a guide on the carriage that holds one floor point sideways
     while letting it heave and pitch.
     - **Placement:** the point must sit on the roll axis (y = 0, joint height), so roll does not fight it.
     - **Payoff:** a modest link a metre from the joint is far stiffer in yaw than the whole tower.
     - **Mechanism:** this needs a guide, not a plain Panhard rod. A rod's arc would itself yaw the floor by up
       to about 20 mrad over the stroke.

## 3. What changes in the design

| # | Change | Status |
|---|---|---|
| A | Cross tube under the seat rails' rear bolts | FE-tested on the floor model; **in the design** (`deck.py`, main revision 8) |
| B | Clevis boxes tying each clevis to the actuator-line tube and the runner | Recommended (fatigue detail); not separately shown to be needed; **in the design** (`deck.py`, revision 8) |
| C | Twin cross tubes under the column plate | FE-tested on the carriage model; a step, not enough on its own; **in the design** (`sled.py`, revision 8) |
| D | Bracing to reach 10 kN/mm at the joint | **In the design** (main revision 9): braced twin-column heave guide, 13–40 kN/mm fore-aft by FE |
| E | Thrust faces on both universal-joint pins | **In the design** (main revision 10): SKF PCMF 303416 E flanged bushings in all four lugs, spider bosses to their flanges |
| F | Preloaded linear bearings for the heave guide | **In the design** (revision 9): HGW25CC blocks at ZA preload, two per column: radial 539 N/µm (HIWIN), lateral to confirm with HIWIN |
| G | Front-overhang stiffening: cross tube under the dash feet, deeper front frame | **In the design** (main revision 13): three front-bay cross tubes and a 100 mm deep overhang; brake-case drop 2.4 → 1.4 mm |
| H | A stiff mount for the floor's yoke: tie the lugs into the frame instead of the bare sheet (found by the modal study) | **In the design** (main revision 11): yoke bars between two cross tubes 140 mm either side of the joint; fore-aft and sideways modes up 55–75 % |

**A–C in the design (main revision 8).**
- **Cheek lengths:** in `deck.py` each cheek stops at its actuator-line tube's face: 120 mm long at the front, 80 mm
  at the rear. The FE model ran the rear ones 40 mm into the tube, which only adds overlap inside it.
- **Carriage:** the surge-nut bracket stays where it was, now under the rear mid tube's front edge. Moving it
  further aft hits the surge actuator body at full rear surge (the fit check caught it).
- **Clearance:** `analysis/platform_clearance.py` now checks the links against the seat tube and the four webs as
  well. Every number it reports is unchanged. The seat tube clears the links by at least 210 mm and the webs by
  44 mm across the whole workspace.

**E in the design (main revision 10).**
- **What was missing:** the spider block is 50 mm wide and the lugs' inner faces are 130 mm apart, so each pin's
  thrust (3.4 kN fore-aft on the roll pin, 1.1 kN sideways on the pitch pin) had 40 mm of air to cross. The pins
  also sat in plain bores with 0.5 mm radial clearance as drawn.
- **The fix:**
  - **Bushings:** an SKF PCMF 303416 E flanged bushing (30 × 34 × 16 mm, flange 42 × 2 mm; steel-backed PTFE
    composite, no lubrication) is pressed into each of the four lugs from its inner face
    (`requirements/ujoint-bushing.toml`, `parts/plain-bearings/`).
  - **Pins:** 36 mm down to 30 mm.
  - **Spider bosses:** each arm of the spider has a 42 mm boss out to the flange, so each flange is a thrust face.
    The gap is 0.5 mm a side as drawn, shimmed to 0.05–0.1 mm in all on assembly.
- **Load:** the flange is rated Ca = 29 kN dynamic and C0a = 91.5 kN static, against 3.4 kN. The radial load is at
  most 1.7 kN per lug, against C = 30.5 kN.
- **Play:** with an f7 pin in an H7 lug bore, SKF gives 10–126 µm operating clearance. That is at most about
  0.06 mm each way at the joint, a fifth of the 0.35 mm elastic deflection the 25 Hz budget allows at 3.4 kN.
- **Lug ligament:** the lug bore drops from 37 to 34 mm, so the steel above and below it grows from 6.5 to 8 mm.
- **Fit (STEVE, main revision 10):** the occupants check is clear on 756 pairs and the platform check on 670.
  The spider and its bosses turn with the floor through full roll and pitch without touching the yokes.

**H in the design (main revision 11).**
- **The fix:**
  - **Cross tubes:** two more 40 × 60 floor cross tubes, runner to runner, 140 mm fore and aft of the joint.
  - **Yoke bars:** each steel yoke lug now hangs from a 20 × 60 × 240 mm bar along the frame's full depth, bolted
    between those tubes.
  - **Load path:** the joint's force enters the frame 17 mm above the pin, not 102 mm below the bare sheet.
- **Why 140 mm:** the crosshead's lugs reach to 85 mm either side of the joint, and its guide ears and rails come
  to within a few millimetres of the frame's underside. The heave guide's struts climb toward the floor near the
  columns.
  - **Crosshead:** at 140 mm it clears the tubes and bars by at least 19.5 mm through full roll and pitch.
  - **Struts:** they clear the rear tube by 15.0 mm at −40 mm heave and full roll (11.9 mm at 125 mm).
- **Mass:** the floor gains 8.3 kg.
- **Fit (STEVE, main revision 11):** occupants clear on 756 pairs, platform on 670.

**G in the design (main revision 13).**
- **Bay tubes:** three more cross tubes in the front bay, so the dash feet, the pedal box and the co-driver's
  footrest all bolt on or beside a tube:
  - x = 272, under the dash feet;
  - x = 440, under the rear pedal and footrest pads;
  - x = 600, under the footrest's front pads.
- **Deeper overhang:** the overhang ahead of the front links is now 100 mm deep instead of 60.
  - **Runners:** a solid 20 × 40 mm 6061 bar under each runner's inboard half, from the front actuator tube
    forward.
  - **Edge tubes:** a 40 × 40 tube under each edge tube from x = 270, clear of the front gearboxes.
- **Brake case** (floor study part revision 11, fixes A, B, G and H, 25 mm mesh):

  | Floor | Front-corner drop | Notes |
  |---|---|---|
  | A, B, H | 2.39 mm | the whole overhang bends, plus sheet bulges in the bays |
  | + bay tubes, 40 mm tubes under runners from x 220 | 1.76 mm | bulges gone; the root of the overhang is still 60 mm deep |
  | + runner bars from the front actuator tube (as built) | **1.40 mm** | smooth bending; pedal box about 0.7–1.1 mm |

- **Stress:** the 61 MPa peak is at a front clevis bore, where the study's support sits. Everywhere else is below
  about 25 MPa.
- **What's left:** the overhang bending as a whole. Going further means a deeper frame again, or moving the front
  links forward.
- **Clearance:** a 40 mm tube under each runner from the front actuator tube came within 7.4 mm of the front links,
  so the runners take a bar on their inboard half instead. With the bar, every clearance is unchanged.
- **Mass:** the floor gains 11.8 kg (73.4 kg in all, with H); the pod is 813.2 kg.
- **Fit (STEVE, main revision 13):** occupants clear on 756 pairs, platform on 670.

**Not covered here:**
- **Weld and bolt detail:** sizes, fatigue classes, preload.
- **The gearbox outriggers** that carry each crank's 3.7 kN and 460 N·m into the carriage.
- **The base frame.**
- **A converged modal study** (the 15 mm mesh exceeds STEVE's memory), one with the links' horizontal stiffness, and
  one with G in the floor.
- **The floor's yaw mode** (§2.5): an off-centre crew does excite it. Choose between cue shaping, stiffening and a
  yaw restraint.
