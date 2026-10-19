# S3 Rally Pod: two-seat cockpit, occupants, motion loads, intercom and telemetry

Status, 2026-10-19. CAD: STEVE design "S3 Rally Pod", branch `two_seat` (main is still the one-seat pod).
Local source: `cad/pod/`. Renders: `renders/`, `gravity-renders/`. Load numbers: `analysis/platform_loads.json`.

## 1. Cockpit layout

- **Rally (layout 0):** LHD. Driver on the left, co-driver / instructor on the right, each with their own door.
- **Formula (layout 1):** one reclined seat on the centreline, no co-driver.
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

## 4. Motion platform: loads (not yet redesigned)

From the CAD masses (exact volume × library density) plus the occupants as lumped masses at the torso (`analysis/platform_loads.py`).

Cueing targets assumed:
- heave 1 g
- surge 0.6 g
- roll and pitch 400°/s²

| Crew | Heave mass | Heave force | Pitch I | Pitch peak | Roll I | Roll static | Roll peak | Surge force |
|---|---|---|---|---|---|---|---|---|
| 95 + 95 | 510 kg | 10.0 kN | 354 kg·m² | 4.4 kNm | 336 kg·m² | 32 Nm | 2.8 kNm | 3.1 kN |
| 95 + 5 | 450 kg | 8.8 kN | 297 kg·m² | 3.6 kNm | 290 kg·m² | 226 Nm | 2.6 kNm | 2.8 kN |
| 95 alone | 394 kg | 7.7 kN | 264 kg·m² | 3.1 kNm | 250 kg·m² | 407 Nm | 2.5 kNm | 2.4 kN |
| 5 alone | 334 kg | 6.6 kN | 208 kg·m² | 2.3 kNm | 204 kg·m² | 213 Nm | 1.9 kNm | 2.1 kN |

Findings:
- **The motion stack under the floor is still the one-seat stack** (MGN15 rails, 16 mm heave guides, small drive blocks) and is nowhere near these loads. It needs a redesign.
- **Pitch carries a constant load.** The loaded floor's centre of mass is about 320 mm behind the pitch axis, so the pitch drive holds about 1.6 kNm just to stay level. Move the pitch axis aft to the centre of mass, or counterbalance it.
- **Asymmetric crews bias roll.** Driver alone, or a big driver with a small instructor, leaves 200–400 Nm on the roll drive the whole time. Size the roll drive for that continuously, or add a counterweight that moves with the passenger seat.
- **The masses are conservative.** The seats are modelled as solid ABS (about 31 kg each against 8–10 kg for a real composite seat), and the dash crossbar and floor plate are solid. Expect the real moving mass to be 60–80 kg lower.
- **The low pivots move heads a lot.** At 7° pitch or roll the occupants' heads translate 120–160 mm relative to the fixed screens, which gives false linear cues and parallax. The usual remedy is slow, rate-limited tilt (below the perception threshold) for sustained g, plus surge/heave to put the effective pivot near the head or hip. Use fast low-pivot rotation only for small, high-frequency road texture. Sources: [DLR](https://www.nads-sc.uiowa.edu/dscna/2005/papers/The_New_Dynamic_Driving_Simulator_%20DLR.pdf), [US 6431872](https://image-ppubs.uspto.gov/dirsearch-public/print/downloadPdf/6431872), [NASA TP-1999-208766](https://ntrs.nasa.gov/api/citations/19990080926/downloads/19990080926.pdf), [arXiv 1909.05833](https://arxiv.org/pdf/1909.05833). The platform redesign should make the effective pivot height a tunable parameter of the cueing software.

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

1. **Redesign the motion platform for the loads above:** pitch axis at the centre of mass, roll bias capacity or counterweight, and raised or virtual pivots.
2. **Choose the vehicle-dynamics engine** per variant and write the loose-surface acceptance test.
3. **Get the intercom technical sheets** and design the audio harness and recorder.
4. **Seat buck trial** with real drivers to confirm the ergonomic targets.
5. **Real-weight parts:** replace the solid placeholder seats, crossbar and floor with real-weight parts and re-run `analysis/platform_loads.py`.
