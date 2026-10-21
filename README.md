# S3 Rally Sim

A two-seat rally training simulator pod: an enclosed cockpit on a four-axis motion floor (surge, roll, pitch, heave),
modelled in [STEVE](https://stevecad.studio) and animated in [Gravity](https://holodeck1.ai).

The driver sits on the left. An instructor or co-driver sits on the right with their own door, footrest, grab handle,
telemetry display and intercom.

**One pod, cockpit modules.** The shell, moving floor, motion platform and screens are the same for every version.
The formula / F1 version is a different cockpit module in the same pod: one reclined seat on the centreline, a
formula wheel and electronics, no dog box. The pod does not get smaller. The two-person rally version comes first;
the F1 module follows once rally is feature-complete.

Videos: [60 s walkaround](renders/s3-rally-pod-walkaround.mp4) · [motion cue in Gravity](gravity-renders/rally-pod-two-seat-motion-cue-20261020-031352.mp4)

## What's here

| Path | What it is |
|---|---|
| `cad/pod/` | The STEVE design source: `main.py` places and joints everything, `params.py` holds the numbers, `components/` one part each |
| `cad/pod/ergo.py` | Occupant model: 5th and 95th percentile body sizes, seated posture, and the seat travel, cushion lift, column reach and pedal position they set |
| `cad/pod/mannequin.py` | Builds a seated occupant in race gear (helmet with intercom mic, HANS, suit, boots, harness) from a posture |
| `cad/pod/motion.py` | Motion-platform geometry: actuator points, crank reach, exact crank and link solution |
| `analysis/platform_loads.py` | Actuator, crank and centre-post loads from the CAD masses plus the occupants, for full, mixed and driver-only crews |
| `analysis/platform_clearance.py` | Exact reachable workspace and link and crank clearances |
| `parts/` | Bought-part cards (seats, wheelbases, pedals, servos, gearboxes, rod ends, rails, ballscrews), every value sourced from the vendor's documents |
| `requirements/` | What each bought part must meet, from the loads and ergonomics; `selection.toml` names the chosen part for each |
| `tools/partsel/` | Part selector: checks cards against requirements, and writes the selection into `cad/pod/bought.py` |
| `cad/fea/` | The floor, centre post and carriage, each rebuilt as one welded solid for STEVE structural studies |
| `analysis/floor_fea_loads.py`, `floor_fea_study.py` | Cockpit bolt loads and centre-post loads for those studies, and the study definitions |
| `requirements/vd-loose-surface.toml` | The rally vehicle model's loose-surface acceptance test: manoeuvres, metrics, pass bands |
| `tools/vdat/` | Runs that test: logged real-car runs against pod runs |
| `render/` | Blender walkaround driven by the CAD's own `rally_stage` animation |
| `tools/mesh_to_sim.py` | Samples the CAD meshes into the Gravity motion-cue sim |
| `sims/rally-pod-motion.js` | The Gravity sim (paste into Gravity → ✎ new sim) |
| `docs/two-seat-pod.md` | Design notes: ergonomics, fit check, platform loads, intercom, telemetry and physics stack, open items |
| `docs/floor-structure.md` | Structural check of the floor, centre post and carriage, with the fixes |
| `docs/vehicle-dynamics.md` | Vehicle-dynamics engine recommendation and the loose-surface acceptance test |
| `renders/`, `gravity-renders/` | The current videos |

## The design in brief

- **Ergonomics:** the wheel and pedals are placed for a 95th percentile man with the seat fully back. A 5th percentile
  woman lifts the cushion, slides the seat forward and pulls the column out. Both land inside comfort ranges for
  knee, hip, ankle and elbow, and see over the rim.
- **Steering column:** hangs from a dash crossbar on uprights outboard of each seat and on the tunnel. Both
  footwells stay clear.
- **Fit check:** STEVE checks both occupants against the shell, doors, screens, wheel, dash and pedals. It runs at
  rest, through every axis, and at the envelope corners where every axis is at its stop at once. The crew passes as
  two 95th percentile and as two 5th percentile occupants.
- **Motion platform:** four crank actuators lift the floor's corners, and a passive centre post with a universal
  joint under the loaded floor's centre of mass takes the side loads. Each crank and link is solved exactly in the
  renders. See `docs/two-seat-pod.md` §4 for the workspace, clearances and loads (about 460 Nm peak per crank with
  two large occupants).
- **Real parts:** Simucube 2 Pro wheelbase, Heusinkveld Ultimate+ pedals, FIA rally seats, and Kollmorgen servos on
  Apex 50:1 right-angle gearboxes driving the cranks. Sizes and masses come from the vendors' documents through the
  part selector (see [`tools/partsel/`](tools/partsel/)).

## Rebuilding the outputs

You need Python 3, Blender 4.5 and ffmpeg.

1. In STEVE, generate the design and download its `bodies_mesh` export. Unzip it to `render/build/mesh`.
2. Build the scene file:

   ```sh
   python3 render/build_scene.py cad/pod render/build/mesh render/build/scene.json
   ```

3. Render the walkaround. Add `--stills` (with an output folder in place of the video path) to get one frame per
   shot instead:

   ```sh
   blender -b -P render/render_walkaround.py -- render/build/scene.json renders/s3-rally-pod-walkaround.mp4
   ```

4. Regenerate the Gravity sim from the same scene:

   ```sh
   python3 tools/mesh_to_sim.py render/build/scene.json sims/rally-pod-motion.template.js sims/rally-pod-motion.js 16000
   ```

5. Recompute the platform loads and check the workspace:

   ```sh
   python3 analysis/platform_loads.py render/build/mesh cad/pod > analysis/platform_loads.json
   python3 analysis/platform_clearance.py cad/pod
   ```

6. Recompute the structural-study loads and write a floor study for STEVE's `run_study`. The studies run on the
   *S3 Rally Pod/FEA* parts; see `docs/floor-structure.md`.

   ```sh
   python3 analysis/floor_fea_loads.py render/build/mesh cad/pod > analysis/floor_fea_loads.json
   python3 analysis/floor_fea_study.py analysis/floor_fea_loads.json combined > study.json
   ```

## Vehicle-model acceptance

```sh
python3 tools/vdat/selftest.py                                         # the tool against known answers
python3 tools/vdat/vdat.py requirements/vd-loose-surface.toml <runs_dir>
```

## Choosing parts

```sh
python3 tools/partsel/partsel.py requirements/crank-gearbox.toml --detail   # which gearboxes fit, and why
python3 tools/partsel/to_cad.py                                             # selection.toml -> cad/pod/bought.py
```

Add a part by writing a card in `parts/<category>/` (copy a neighbour, cite every number), then re-run the selector.

## Working on the CAD

`cad/pod` is a plain copy of the STEVE design's files. To bring it into your own STEVE workspace, create a design
and save these files into it (an AI client with STEVE's MCP server can do this with `write_design`). For a team,
work in a STEVE team workspace on a branch and let a member review and merge.

## License

MIT, no warranty. See [LICENSE](LICENSE).
