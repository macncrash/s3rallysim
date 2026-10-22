# S3 Rally Pod: two-seat cockpit, occupants, motion loads, intercom and telemetry

Status, 2026-10-19. CAD: STEVE design "S3 Rally Pod", main revision 6 (two-seat cockpit, crank-actuator motion platform, real bought parts).
Local source: `cad/pod/`. Renders: `renders/`, `gravity-renders/`. Load numbers: `analysis/platform_loads.json`.

## 1. Cockpit layout

- **Rally (layout 0):** LHD. Driver on the left, co-driver / instructor on the right, each with their own door.
- **Formula (layout 1):** the same pod with a different cockpit module: one reclined seat on the centreline, formula
  wheel and electronics, no dog box, no co-driver. Shell, floor, platform and screens never depend on `layout`.
  Rally comes first.
- **Steering column:** hangs from a dash crossbar on the moving floor. The crossbar sits on three uprights: outboard of each seat and on the tunnel. Nothing stands in either footwell.
- **Displays:**
  - A 55" windscreen display on the car centreline. Render it with an off-axis frustum for the driver's eye.
  - Two 27" side-window displays on the A-pillars, and a rear-view display.
  - The co-driver gets a 10" telemetry/coaching display on the crossbar.
  - The driver gets a 7" dash display above the column.
- **Shell:** 2,180 × 1,760 × 1,930 mm frame. It was enlarged until the occupants cleared it at every motion extreme (see 3).

## 2. Occupants and ergonomics (`cad/pod/ergo.py`)

The mannequins are a 5th-percentile woman and a 95th-percentile man. Seated link lengths approximate ANSUR II and Pheasant. Each wears an FIA closed-face helmet with an intercom boom mic, a HANS with tethers, a suit, boots and a 6-point harness.

The pedals and wheel are placed for the 95th percentile with the seat fully back. Smaller people:

1. Lift the cushion so their eye clears the rim top by 60 mm.
2. Slide the seat forward until the knee angle matches.
3. Pull the column out until the elbow angle matches.

| Rally, driver seat | 95th pct man | 5th pct woman | Comfort target |
|---|---|---|---|
| Seat forward of rear stop | 0 | 181 mm (of 200) | |
| Cushion lift | 0 | 67 mm (of 80) | |
| Column out | 0 | 60 mm (of 60) | |
| Knee / hip / ankle | 128° / 91° / 113° | 128° / 98° / 107° | 110–135° / 90–110° / 90–115° |
| Elbow, hands at quarter to three | 100° | 95° | 95–120° |
| Rim to legs | 51 mm | 94 mm | > 25 mm |
| Dash crossbar to legs | 174 mm | 134 mm | > 50 mm |
| Eye above rim top | 176 mm | 60 mm | ≥ 60 mm |
| Mass with gear | 116 kg | 56 kg | |

Formula, driver seat:

| | 95th pct | 5th pct |
|---|---|---|
| Knee | 145° | 145° |
| Elbow | 100° | 99° |
| Rim to legs | 96 mm | 108 mm |
| Dash crossbar to legs | 117 mm | 129 mm |

The 5th-percentile driver needs 110 mm of column reach.

The comfort targets are common seating-package practice, not regulations. Treat them as starting points to confirm in a seat buck with real drivers.

Relevant FIA standards ([technical lists](https://www.fia.com/regulation/category/759)):
- Helmets: 8859-2024 and 8860-2018.
- Head restraint (FHR/HANS): 8858-2010.
- Seats: 8855-2021 and 8862-2009 ([standard](https://www.fia.com/sites/default/files/8862-2009_advanced_racing_seat.pdf)). A 2022 FIA safety note gives a vertical stiffness recommendation for rally seat brackets ([note](https://api.fia.com/sites/default/files/safety_department_note_fiasdh-22-010_-_fia_standards_8862-2009.pdf)). That matters on a heaving floor, so the seat mounts should meet it.

## 3. Fit check (STEVE `occupants` fit check)

- **Coverage:** the occupants against the shell, doors, displays, wheel, dash frame, pedals, footrest and console.
- **Poses:** at rest, jump, land, corner, and four envelope corners where every axis is at its stop at once.
- **Sweeps:** each axis through its full range, plus the shifter, handbrake and both doors.
- **Clearance required:** 50 mm to the cabin, 25 mm to the dash frame.
- **Result:** all pairs are clear (756 on main revision 6, real parts fitted) with two 95th-percentile occupants (branch revision 5) and again with two 5th-percentile occupants (revision 6). The only contacts are the six designed ones: seats, gloves on the rim, boots on the pedals and footrest, and the column clamp. The branch is left at 95/95, the worst case for clearance and loads.

What drove the fixes:
- **Shell width:** at 7° roll the occupants' shoulders and elbows move about 120 mm sideways, which needed ±880 mm posts.
- **Shell length:** at −7° pitch the seat-back tops swing back about 160 mm, which moved the rear wall back.
- **Shell height:** the 95th-percentile helmet top is at 1,684 mm at rest (floor top at 511 mm).

## 4. Motion platform (`cad/pod/motion.py`)

**Architecture.** The old serial stack (sled → roll cradle → pitch cradle → heave posts, pivots at 118 and 176 mm) is
gone. In its place:

- **Four corner crank actuators lift the floor.** Each is a servo on a right-angle planetary gearbox driving a 125 mm
  crank, with a 295 mm link on spherical rod ends up to a clevis under the floor (the floor tilts up to 7° about
  them). The links stand 390 mm either side of the centreline. Each crank sits 30 mm outboard of its link, and the
  gearbox and motor sit further outboard, under the floor's edge.
- **A passive heave guide carries the side and fore-aft loads.** A crosshead runs on linear guides between two
  braced steel columns, and a universal joint on the crosshead holds the floor (main revision 9; see
  [`floor-structure.md`](floor-structure.md)).
  - The universal joint is the roll and pitch pivot, 430 mm up.
  - It sits at x = −300, under the loaded floor's centre of mass. With two 95th-percentile occupants that centre of
    mass is 20 mm from the pivot.
- **Surge:** the whole stack rides a surge carriage on size-25 profile rails, driven by a ballscrew.
- **Floor:** a 4 mm sheet on a welded frame, top at 511 mm. That is high enough for the frame to clear the gearboxes by
  15.9 mm or more anywhere the cranks can reach. The cockpit is positioned from the floor top, so the ergonomics are
  unchanged.

**Bought parts.** Every bought part has a vendor-sourced card in [`parts/`](../parts/). The selector in
[`tools/partsel/`](../tools/partsel/) checks the cards against the requirements in [`requirements/`](../requirements/),
which come from the loads below. `tools/partsel/to_cad.py` writes the chosen parts into `cad/pod/bought.py`, and the
CAD reads sizes and masses from there.

| Role | Part | Status |
|---|---|---|
| Wheelbase | Simucube 2 Pro | chosen |
| Pedals | Heusinkveld Ultimate+ 3-pedal | chosen |
| Seats (×2) | Recaro Pro Racer SPG XL (FIA 8855-1999 and 8855-2021 seats are allowed) | provisional: internal width not published, confirm on a sample |
| Crank servo (×4) | Kollmorgen AKM2G-51K, with brake | provisional |
| Crank gearbox (×4) | Apex ABR142, 50:1 right angle | provisional: T2B derived from Apex's printed rule, confirm with Apex |
| Link rod ends (×8) | SKF SIKB 20 F | provisional |
| Surge rails | HIWIN HGW25CC (E2 self-lubricating) | provisional |
| Surge ballscrew | HIWIN 25 × 10 | provisional |

**Workspace (`analysis/platform_clearance.py`, exact geometry).**

- **Each axis alone:** heave ±40 mm, pitch ±7° and roll ±7° are each reachable over their full range.
- **Combinations:**
  - Full pitch or full roll with any heave: reachable.
  - Full pitch *and* full roll together: reachable at heave −15 to 0 mm. Elsewhere the motion software must blend the
    axes (normal for 4-actuator rigs).
- **Built-in guard:** `main.py` refuses to build if any pose of the motion cue is out of the cranks' ±65° reach. The
  cue's largest crank angle is 57.5°.
- **Clearances over the whole workspace:**
  - Links clear the floor's under-frame by ≥ 23 mm.
  - Crank tips (rod-end eye bottoms) stay ≥ 28 mm above the ground.
  - The floor frame clears the gearboxes by ≥ 15.9 mm.
  - Links lean at most 15.6° from upright.

**Fit checks (STEVE).** Both pass on main revision 9 (with structural fixes A–D and F):

| Check | Instance pairs | What it covers |
|---|---|---|
| `occupants` | 756 | Every pose and envelope corner |
| `platform` | 670 | Every pose of the cue, plus a sweep of every axis |

The only contacts are the designed ones (pins in eyes, blocks on rails, sleeve on column, drives on the carriage).
STEVE gears the cranks with small-angle ratios and draws each link upright. The Blender walkaround and the Gravity sim
solve each crank and link exactly.

**Loads (`analysis/platform_loads.py`, main revision 6 masses).**

Cueing targets assumed:
- heave 1 g
- surge 0.6 g
- roll and pitch 400°/s²

Every combination of those targets was checked. Forces are shared as four equal springs would share them.

| Crew | Floor mass | Actuator static | Actuator peak | Link tension peak | Crank peak torque | Centre post side load | Surge force |
|---|---|---|---|---|---|---|---|
| 95 + 95 | 392 kg | 0.89–1.03 kN | 3.7 kN | 1.6 kN | 462 Nm | 3.6 kN | 3.3 kN |
| 95 + 5 | 332 kg | 0.58–1.05 kN | 3.4 kN | 1.3 kN | 427 Nm | 3.0 kN | 3.0 kN |
| 95 alone | 276 kg | 0.33–1.02 kN | 3.1 kN | 1.1 kN | 389 Nm | 2.4 kN | 2.6 kN |
| 5 alone | 216 kg | 0.19–0.87 kN | 2.5 kN | 0.8 kN | 311 Nm | 1.8 kN | 2.3 kN |

- **Real-weight parts cut the loads by about 30%.** The floor is now a 4 mm sheet on a frame instead of a solid 12 mm
  plate. The seats are 10 kg composite shells instead of 31 kg solid placeholders, and the dash frame is tube. With
  two 95th-percentile occupants the floor went from 568 to 392 kg.
- **The requirements keep the old envelope on purpose.** They were sized from the heavier model (641 Nm peak crank
  torque, 5.1 kN actuator peak), which leaves room for the cockpit hardware still to be fitted (electronics, wiring,
  intercom, seat brackets). Each chosen drive gives about 720 Nm peak and 313 Nm continuous at the crank (AKM2G-51K
  15.7 / 6.81 Nm × 50 × 92%; the gearbox's own limit is higher) against 462 Nm peak and 131 Nm static.
- **Links work in tension:** at −1 g heave combined with a tilt kick they pull at up to 1.6 kN, so the links and rod
  ends must be rated for both directions. The SKF rod ends are checked against an alternating load.
- **Uneven crews only shift load between corners:** the crank torques stay well inside the drive rating.

**Still to do on the platform:**

- **Structural fixes** from the first STEVE studies ([`floor-structure.md`](floor-structure.md)):
  - Done in main revision 8: a cross tube under the seat rails' rear bolts, clevis boxes, and twin cross tubes
    under the column plate.
  - Done in main revision 9: the centre post and sleeve are replaced by a braced twin-column heave guide on HIWIN
    blocks. FE gives 13–40 kN/mm fore-aft at the joint. With the blocks' own give (HIWIN: 539 N/µm radial at ZA
    preload) the floor mode is about 28–47 Hz; the blocks' lateral stiffness is not printed, confirm with HIWIN.
  - Thrust faces on the universal-joint pins.
  - A stiffer front overhang.
- **Control:** the motion controller's force sharing across four actuators on three axes, plus software end stops
  and the combined-axis envelope.
- **Cueing:** virtual-pivot cueing near the occupants' heads. The universal joint is still about 1 m below them.

## 5. Intercom and headsets

The aim is to behave like a real rally car while recording everything:

- **Hardware:** a real rally intercom amplifier (Stilo WRC DES or Terratrip), with sockets for both Stilo and Peltor-standard helmet kits so crews can bring their own helmets. Notes:
  - The Stilo DES has a "radio in / camera out" port ([Harris](https://harrisraceradios.com/products/stilo-wrc-des-9v-intercom)).
  - Terratrip uses its own locking Nexus jack; Peltor kits need an adaptor ([GSM](https://gsmperformance.co.uk/will-a-sparco-helmet-kit-work-with-a-terratrip-intercom/)).
  - Published pinouts are inconsistent. Get the Stilo and Terratrip technical sheets before designing the harness.
- **Third channel:** an instructor or engineer outside the pod, with push-to-talk, injected through the radio-in port.
- **Recording:** each microphone (driver, co-driver, instructor) is tapped before the mix and recorded on its own track on a Dante/AES67 interface timed by the pod's PTP clock (see 6).
- **In the CAD:** the intercom unit and helmet jacks sit on the tunnel upright, and both helmets carry boom mics.

## 6. Physics and telemetry for real development use

**Physics.** The pod must run a professional vehicle model, not the arcade (3) RALLY model, for development and training. (3) RALLY stays as the arcade mode.

- **Formula variant:** well served by rFpro (Simulink/Dymola plug-in, FTire in real time), IPG CarMaker (MF-Tyre/MF-Swift), VI-grade or Cruden.
  - Sources: [MathWorks](https://www.mathworks.com/products/connections/product_detail/rfpro.html), [rFpro FTire](https://rfpro.com/ftire-partnership-brings-step-change-in-vehicle-simulation/), [Cruden](https://www.cruden.com/article/four-wheels-good-vehicle-model-integration-for-dynamics-and-more).
- **Choice and acceptance test:** see [`vehicle-dynamics.md`](vehicle-dynamics.md).
- **Rally variant:** no professional DiL vendor publicly documents validated gravel, snow or jump physics.
  - Hyundai Motorsport used VI-CarRealTime for its WRC car ([PMW](https://pmw-magazine.com/uncategorized/hyundai-motorsport-choses-vi-grade-for-simulation-work.html)).
  - M-Sport's public simulator work was on tarmac ([Motorsport.com](https://www.motorsport.com/wrc/news/ford-simulator-boosting-m-sport-wrc-puma-performances/10602699/)).
  - Make loose-surface tyre/terrain modelling a separate contract deliverable with its own acceptance test against logged real-car data.
- **Real-time rate:** get each vendor's figure in writing. Dynisma quotes < 5 ms latency for reference ([MathWorks](https://blogs.mathworks.com/startups/2022/07/27/startup-shorts-dynisma-is-redefining-the-world-of-automotive-motion-simulation/)).

**Logging.** Log natively to ASAM MDF4 (open; `asammdf` reads and writes it). Export:
- to McLaren ATLAS through its SQL Race API ([docs](https://atlas.mclarenapplied.com/developer/sqlrace-api/));
- to MoTeC i2 .ld through the MIT-licensed `motec-i2` writer ([lib.rs](https://lib.rs/crates/motec-i2));
- to CSV.

AiM .xrk has no third-party writer.

**Channels and rates** (industry practice; confirm against the team's own logger configuration):

| Group | Channels | Rate |
|---|---|---|
| Fast chassis | Simulated damper travel, ride heights, 3-axis accelerations, yaw/pitch/roll rates, brake pressures | 500 Hz–1 kHz |
| Driver inputs and wheels | Wheel speeds, steering angle and torque, throttle, brake force, clutch, handbrake, gear and shifter | 100–200 Hz |
| Position | GPS / stage-distance | 10–20 Hz |
| Engine | RPM, boost, lambda | 100 Hz |
| Temperatures | | 1–2 Hz |
| Rig (validates the cues) | Each actuator's commanded and measured position, an IMU on the moving floor, the occupants' seat loads | ≥ 500 Hz |

**Correlation with the real car.** Use the same channel names, units and sign conventions as the real car's logger, map each stage once, and overlay runs against distance rather than time.

**Time.** One PTP (IEEE 1588) grandmaster for the sim PC, motion controller, logger, cockpit cameras (SMPTE ST 2059-2) and the intercom recorder (AES67/Dante); every sample is stamped in PTP time ([SMPTE 2059](https://en.wikipedia.org/wiki/SMPTE_2059)).

**Live data.** UDP out of the sim; CAN/CAN FD with a DBC (written with `cantools`) to the dash displays and any real logger fitted to the pod.

## 7. Open items

1. **Platform structure.** The first STEVE studies are done ([`floor-structure.md`](floor-structure.md)).
   - **Results:** the seat-rail mounting fails as drawn (fixed with one cross tube). The post's carriage mounting
     is far too soft for cueing (fore-aft mode about 7 Hz against a 25–30 Hz target). The universal joint lacks
     thrust faces, and the heave sleeve has 2 mm of play.
   - **Next:**
     - Fixes A–C are in the design (main revision 8).
     - Fixes D and F are in the design (main revision 9): a braced twin-column heave guide. Confirm the guide
       blocks' lateral stiffness with HIWIN (radial is printed: 539 N/µm at ZA).
     - Design E and G: pin thrust faces, front overhang.
     - Run a modal study of floor, guide and carriage together.
     - Re-run the clearance and fit checks.
     - Confirm the provisional bought parts with their makers (Apex T2B, seat internal width).
2. **Vehicle-dynamics engine.** Researched, with a recommendation ([`vehicle-dynamics.md`](vehicle-dynamics.md)).
   - **Recommendation:** for rally, shortlist AVL VSM and VI-CarRealTime with FTire, and prototype our own gravel
     layer in parallel. For formula, rFpro.
   - **Acceptance test:** the loose-surface test is `requirements/vd-loose-surface.toml`, run by `tools/vdat/`.
   - **Next:**
     - Send the vendor questions (§3 of that document).
     - Agree the test's bands before signing.
     - Instrument a car and log the gravel pad.
3. **Intercom:** get the technical sheets and design the audio harness and recorder.
4. **Seat buck trial** with real drivers to confirm the ergonomic targets.
5. **Remaining cockpit hardware:** model the Heusinkveld pedals at their real size and mass (the CAD pedal box is
   4.4 kg, the set is 6.6 kg), the handbrake and sequential shifter as bought parts, the intercom amplifier, the
   electronics and cabling, and E-stops and door switches. Then re-run `analysis/platform_loads.py`.
