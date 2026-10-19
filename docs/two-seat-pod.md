# S3 Rally Pod: two-seat cockpit, occupants, motion loads, intercom and telemetry

Status, 2026-10-19. CAD: STEVE design "S3 Rally Pod", main revision 5 (two-seat cockpit + crank-actuator motion platform).
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
- **Shell:** 2,180 × 1,760 × 1,880 mm frame. It was enlarged until the occupants cleared it at every motion extreme (see 3).

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
- **Result:** all 612 pairs are clear with two 95th-percentile occupants (branch revision 5) and again with two 5th-percentile occupants (revision 6). The only contacts are the six designed ones: seats, gloves on the rim, boots on the pedals and footrest, and the column clamp. The branch is left at 95/95, the worst case for clearance and loads.

What drove the fixes:
- **Shell width:** at 7° roll the occupants' shoulders and elbows move about 120 mm sideways, which needed ±880 mm posts.
- **Shell length:** at −7° pitch the seat-back tops swing back about 160 mm, which moved the rear wall back.
- **Shell height:** the 95th-percentile helmet top is at 1,609 mm at rest.

## 4. Motion platform (`cad/pod/motion.py`)

**Architecture.** The old serial stack (sled → roll cradle → pitch cradle → heave posts, pivots at 118 and 176 mm) is
gone. In its place:

- **Four corner crank actuators lift the floor.** Each is a servo on a right-angle planetary gearbox driving a 125 mm
  crank, with a 245 mm link on rod ends up to a clevis under the floor. The links' top eyes are spherical rod ends
  (the floor tilts up to 7° about them).
- **A passive centre post carries the side and fore-aft loads.** A heave sleeve slides on a square column, and a
  universal joint on the sleeve holds the floor.
  - The universal joint is the roll and pitch pivot, 380 mm up.
  - It sits at x = −300, under the loaded floor's centre of mass. With two 95th-percentile occupants that centre of
    mass is 18 mm from the pivot, so the old constant 1.6 kNm pitch load is gone.
- **Surge:** the whole stack rides a surge carriage on size-25 profile rails, driven by a ballscrew.
- **Floor height:** the floor top went up 25 mm (to 461 mm) so the cranks clear the ground by 25 mm at full swing. The
  cockpit is positioned from the floor top, so the ergonomics are unchanged.

**Workspace (`analysis/platform_clearance.py`, exact geometry).**

- **Each axis alone:** heave ±40 mm, pitch ±7° and roll ±7° are each reachable over their full range.
- **Combinations:**
  - Full pitch with any heave: reachable.
  - Full roll with heave from −40 to +35 mm: reachable.
  - Full pitch *and* full roll together: **not** reachable. The motion software must blend the axes (normal for
    4-actuator rigs).
- **Built-in guard:** `main.py` refuses to build if any pose of the motion cue is out of the cranks' ±65° reach.
- **Clearances over the whole workspace:**
  - Links clear the floor's under-frame by ≥ 28 mm.
  - Crank tips stay ≥ 25 mm above the ground.
  - Links lean at most 18.5° from upright.

**Fit checks (STEVE).** Both pass on main revision 5:

| Check | Instance pairs | What it covers |
|---|---|---|
| `occupants` | 756 | Every pose and envelope corner |
| `platform` | 670 | Every pose of the cue, plus a sweep of every axis |

The only contacts are the designed ones (pins in eyes, blocks on rails, sleeve on column, drives on the carriage).
STEVE gears the cranks with small-angle ratios and draws each link upright. The Blender walkaround and the Gravity sim
solve each crank and link exactly.

**Loads (`analysis/platform_loads.py`).**

Cueing targets assumed:
- heave 1 g
- surge 0.6 g
- roll and pitch 400°/s²

Every combination of those targets was checked. Forces are shared as four equal springs would share them.

| Crew | Floor mass | Actuator static | Actuator peak | Link tension peak | Crank peak torque | Centre post side load | Surge force |
|---|---|---|---|---|---|---|---|
| 95 + 95 | 568 kg | 1.32–1.46 kN | 5.1 kN | 2.2 kN | 641 Nm | 5.1 kN | 4.0 kN |
| 95 + 5 | 508 kg | 1.07–1.42 kN | 4.8 kN | 1.9 kN | 595 Nm | 4.5 kN | 3.6 kN |
| 95 alone | 452 kg | 0.85–1.36 kN | 4.4 kN | 1.7 kN | 553 Nm | 4.0 kN | 3.3 kN |
| 5 alone | 392 kg | 0.68–1.24 kN | 3.9 kN | 1.4 kN | 487 Nm | 3.3 kN | 2.9 kN |

- **Drive size:** about 2 kW servo with a 50:1 gearbox. That gives about 950 Nm peak (641 needed) and 320 Nm continuous
  (183 Nm static).
- **Links work in tension:** at −1 g heave combined with a tilt kick they pull at up to 2.2 kN, so the links and rod
  ends must be rated for both directions.
- **Uneven crews only shift load between corners:** the crank torques stay well inside the drive rating.
- **Masses are conservative:** the seats are still solid placeholders (about 31 kg each).

**Still to do on the platform:**

- **Bought parts:** pick the real servos, gearboxes, rod ends, rails and ballscrew, using STEVE's standard-parts
  catalogue.
- **Structural check:** stress and stiffness on the floor frame and centre post (STEVE simulation).
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

1. **Platform bought parts and structure:** pick the servos, gearboxes, rod ends, rails and ballscrew, then check the
   floor frame and centre post for stress and stiffness (see 4).
2. **Vehicle-dynamics engine:** choose one per variant and write the loose-surface acceptance test.
3. **Intercom:** get the technical sheets and design the audio harness and recorder.
4. **Seat buck trial** with real drivers to confirm the ergonomic targets.
5. **Real-weight parts:** replace the solid placeholder seats, crossbar and floor with real-weight parts and re-run
   `analysis/platform_loads.py`.
