# S3 Rally Pod: vehicle-dynamics engine and loose-surface acceptance

Status, 2026-10-21. Research and recommendation for open item 2 in [`two-seat-pod.md`](two-seat-pod.md) §7. The
acceptance test is [`requirements/vd-loose-surface.toml`](../requirements/vd-loose-surface.toml), and
[`tools/vdat/`](../tools/vdat/) runs it.

## 1. What we found

- **No vendor documents validated rally physics.** No commercial driver-in-the-loop vehicle-dynamics vendor
  publicly documents validated gravel, snow or jump physics. Loose-terrain tyre and soil models do exist, but they
  come from off-road, agricultural and military work, not from rally speeds.
- **The standards only cover tarmac.** ISO 19364 (steady-state circular), ISO 22140 (step and frequency response)
  and ISO 19365 (sine with dwell) define how to compare a vehicle model with the real car. They are written for
  passenger cars on paved roads, and their tolerances are in the paid texts.
- **Consequences:**
  - The gravel tyre and terrain layer is the part nobody has proven, so it must be swappable.
  - Its acceptance test is ours to write. That test is §4. Agree its bands with the vendor before signing, not
    after the first run.

## 2. Recommendation

| Variant | Recommendation | Why |
|---|---|---|
| Rally (first) | Shortlist **AVL VSM** and **VI-grade VI-CarRealTime**. License **FTire** on whichever we choose. In parallel, prototype our own gravel tyre and terrain layer in **Project Chrono (SCM)** or as an HSSTM-style tyre at 1 kHz. | AVL is the FIA's vehicle-simulation supplier and has coupled VSM with a soft-soil tyre. VI-CarRealTime has a WRC track record (Hyundai Motorsport). FTire runs inside both. Neither vendor has shown gravel validation, so we keep our own path open. |
| Formula (later) | **rFpro** for the environment, road surface (TerrainServer) and driver-in-the-loop integration. **VI-CarRealTime** or the team's own Simulink model for the vehicle. **FTire/RT** or **MF-Swift** for the tyres. | Ferrari has used rFpro since 2014. TerrainServer feeds tyre models at 1–4 kHz and is open to third-party tyre models. |
| Both | If VI-CarRealTime or AVL VSM wins the rally choice, use it for formula too. | One toolchain, one set of vehicle files, one acceptance tool. |

(3) RALLY stays as the arcade mode. It is not a candidate for development or training use.

### Rally shortlist in detail

1. **AVL VSM / VSM RACE, with AVL's soft-soil tyre model.**
   - The FIA uses AVL RACETECH as its official vehicle-simulation supplier, including for WRC and cross-country
     ([AVL](https://avl.com/simulate-racing),
     [press](https://www.avl.com/en/press/press-release/avl-racetech-joins-forces-idec-sport-racing-official-partner-vehicle-simulation-software?page=1)).
   - VSM runs in real time. It has been paired with Ansible Motion simulators
     ([AVL VSM](https://avl.com/en/simulation-solutions/simulation-software/avl-vsm),
     [PMW](https://www.pmw-magazine.com/news/simulation/avl-and-ansible-advance-vehicle-validation-with-integrated-simulation-and-driver-in-the-loop-testing.html)).
   - VSM has been coupled with a soft-soil tyre model on unpaved terrain
     ([CARLA](https://carla.org/2023/04/21/avl-off-road-simulation/)), but for agriculture and construction, not rally.
   - No published gravel validation and no public pricing.
2. **VI-grade VI-CarRealTime, plus FTire, plus a gravel layer.**
   - Used by Hyundai Motorsport on its WRC cars
     ([VI-grade](https://vi-grade.com/en/about/news/vi-grade-helps-hyundai-motorsport-to-optimize-their-wrc-rally-cars-50)).
   - A mature real-time product with its own simulator hardware
     ([VI-CarRealTime](https://www.vi-grade.com/en/products/vi-carrealtime/)).
   - We found no public soft-soil or terrain modelling. Gravel would come from tyre scaling or from FTire.
3. **Cosin FTire with FTire/soil.**
   - cosin lists Bekker/Wong and its own soil models, snow, mud and user finite-element soils
     ([cosin](https://cosin.eu/products/ftiresoil)). These bullets were seen in a search snippet only.
   - In FTire/RT the soft-soil models are off by default as too slow
     ([cosin](https://www.cosin.eu/wp-content/uploads/FTire_Artikel_VehicleDynamic_1601213.pdf)).
   - An older brochure says soft-soil and snow traction can't be analysed
     ([2018](https://www.cosin.eu/wp-content/uploads/2018-FTire-flyer-brochure.pdf)).
   - The particle soil model (cosin/prm) is "not yet product ready" ([cosin](https://cosin.eu/products/cosinprm/)).
   - **Ask cosin in writing:** does FTire/soil run in real time at 1 kHz or faster?
4. **Project Chrono, SCM deformable terrain** (open source).
   - A Bekker/Janosi height-field soil, with moving patches to keep it fast
     ([API](https://api.chrono.projectchrono.org/classchrono_1_1vehicle_1_1_s_c_m_terrain.html)).
   - Its developers call it "real-time or close"
     ([Multibody 2023](https://multibody2023.tecnico.ulisboa.pt/prog_MULTIBODY_WEB/MULTBODY2023_ABSTRACTS/ID_106_121_extendedAbstract.pdf)).
   - Operator-in-the-loop terramechanics has been run
     ([SBEL](https://sbel.wisc.edu/2018/05/19/terramechanics-methods-for-real-time-off-road-vehicle-mobility-simulation-on-deformable-terrain/)).
   - No rally validation, and no published real-time factor at 1 kHz.
5. **CarSim terramechanics.** Bekker-Wong soil, sinkage, compaction and bulldozing
   ([CarSim](https://www.carsim.com/products/supporting/terramechanics/index.php)). Its real-time capability is not
   stated. Worth asking about.
6. **BeamNG.tech.** Soft-body physics with a Python API, used in off-road and jump research
   ([docs](https://documentation.beamng.com/beamng_tech/)). No validation against real gravel, and motion-platform
   support not confirmed. Commercial pricing on request.

**Not suitable as the professional engine:**
- **IPG CarMaker:** no native soil model. Off-road goes through a third-party tyre
  ([ISTVS](https://2025.istvs.org/submissions/papers/4217)).
- **rFpro TerrainServer:** paved roads only ([rFpro](https://rfpro.com/simulation-software/terrain-server/)).
- **Simcenter Tire:** wet roads, but no soil
  ([Siemens](https://blogs.sw.siemens.com/simcenter/simcenter-tire-2506-feel-the-rain-in-real-time/)).
- **Altair MotionSolve:** has a soft-soil tyre, but offline only.
- **Consumer rally titles** (EA WRC, RBR/RSF with NGP, Assetto Corsa Rally): no professional licensing and no
  published validation.

**Worth watching:** The Last Garage, a rally sim aimed at working with car makers
([Traxion](https://traxion.gg/former-rfactor-2-lead-teases-richard-burns-rally-spiritual-successor/)).

**Academic loose-surface tyre models** we could build on:
- HSSTM ([Michigan](https://arc.engin.umich.edu/research/projects/off-road-soft-soil-tire-model-development-validati))
- PoliTo terramechanics with lateral bulldozing ([PoliTo](https://iris.polito.it/handle/11583/3003729))
- Rescaling Magic Formula tyre models to a new surface from vehicle tests
  ([Chalmers](https://research.chalmers.se/en/publication/505696))

## 3. What to ask each vendor (in writing, before a quote is compared)

1. Vehicle-model step rate and force-feedback loop rate on our hardware. Input-to-motion latency, end to end.
2. Loose surfaces:
   - Which tyre and terrain models run in real time at the step rate in question 1.
   - Whether their parameters are fitted from vehicle tests or from tyre-rig tests.
3. Any validation against a rally car on gravel, snow or a jump: data, method and results. "None" is an
   acceptable answer; vague is not.
4. Whether we can replace the tyre/terrain model with our own (an API at the tyre-force level), and at what
   step rate.
5. Will they sign up to §4 as the acceptance test, with its bands, and what happens if a check fails.
6. Motion-cueing output: which signals reach our motion controller, at what rate, and with what timestamp.
7. Logging: native MDF4 or a documented stream we can log to MDF4 against PTP time (see `two-seat-pod.md` §6).
8. Licence model and cost for one pod, for a fleet of pods, and for the formula module.

## 4. Loose-surface acceptance test

**Method.** We log one instrumented rally car, then drive the same manoeuvres in the pod with the same driver.
- **Venue:** one surveyed gravel pad and one short stage section. The real car's runs come first.
- **Repeats:** each manoeuvre at least three times in each, so the real car's own scatter is measured. A band
  tighter than that scatter can't be met, and the tool reports it.
- **Surfaces:** packed and loose top layer for the grip-dependent tests. Snow only if the customer needs it.
- **Spec:** the tests, metrics and pass bands are in `requirements/vd-loose-surface.toml`.
- **The bands are our proposals**, from industry practice and the literature: no standard sets them for gravel.

| # | Manoeuvre | Checked | Proposed band |
|---|---|---|---|
| 1 | 40 m circle, speed raised to the limit | understeer gradient, peak lateral g, sideslip vs lateral g | ±20 %, ±10 %, ≤ 1.5° RMS |
| 2 | Braking to a stop from 80 and 100 km/h, packed and loose | stopping distance, mean deceleration | ±7 %, ±0.05 g |
| 3 | Full-throttle launch | time to 60 km/h, wheelspin trace | ±5 %, ≤ 0.03 RMS |
| 4 | Step steer at 60 km/h | yaw and lateral gains, response time | ±15 %, ±15 %, ±50 ms |
| 5 | Swept or random steer, 0.2–3 Hz | yaw/steer and lateral-g/steer response to 2 Hz | ±2 dB gain, ±15° phase |
| 6 | Double lane change and pendulum flick | yaw along distance, peak drift angle | ≤ 15 % of peak RMS, ±3° |
| 7 | Steering torque in 1, 4 and 6 | fit to the real column torque | R² ≥ 0.8, ≤ 15 % of peak RMS |
| 8 | Surveyed crest at three speeds | airtime, landing pitch, landing peak vertical g | ±10 %, ±2°, ±20 % |
| 9 | Packed vs loose (and a second pass in the ruts) | the sim's change against the car's change | same sign, 70–130 % of it |
| 10 | 2–5 km stage section | section time; lateral g, yaw and speed along distance | ±2 %; 0.1 g RMS; 15 % and 5 % of peak RMS |
| 11 | Rig timing | model and force-feedback rates, steer-to-motion and steer-to-image latency | ≥ 1 kHz, ≥ 1 kHz, ≤ 20 ms, ≤ 40 ms |

Two notes on the bands:
- The steering-torque band is set against a published simulator-vs-car slalom, where torque deviated by -18 % to
  +10 % ([Kempten](https://opus4.kobv.de/opus4-hs-kempten/solrsearch/index/search/searchtype/collection/id/16567)).
- The latency band is end to end. For scale, Dynisma quotes under 5 ms for its motion system alone.

**Instrumenting the real car** (the minimum the test needs):
- GPS and a 6-axis IMU at 200 Hz or more
- An optical sideslip sensor
- Steering angle and column torque
- Four wheel speeds and damper potentiometers
- Brake pressures, throttle, gear and rpm
- Ideally, wheel force transducers

Name the channels as in the spec, or map them with a `map.toml`. We found no public rally gravel telemetry
dataset, so this logging is ours to do.

**Running it:**

```sh
python3 tools/vdat/selftest.py                          # the tool against synthetic runs with known answers
python3 tools/vdat/vdat.py requirements/vd-loose-surface.toml runs/2026-11-gravel-pad
```

The tool exits non-zero until every check has been run and passed.

## 5. Not verified

- The tolerance values in ISO 19364, 22140 and 19365 (paid texts).
- Whether FTire/soil or Chrono SCM runs at 1 kHz in real time.
- AVL's soft-soil validation on rally gravel.
- Which vehicle-dynamics software F1 teams use in 2025–26.
- The Rally1 control logger supplier.
- Licence costs. Only BeamNG.tech academic (free) and Chrono (open source) are public.
