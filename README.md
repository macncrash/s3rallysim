# S3 Rally Sim

A two-seat rally training simulator pod: an enclosed cockpit on a four-axis motion floor (surge, roll, pitch, heave),
modelled in [STEVE](https://stevecad.studio) and animated in [Gravity](https://holodeck1.ai).

The driver sits on the left. An instructor or co-driver sits on the right with their own door, footrest, grab handle,
telemetry display and intercom. A formula template turns it into a single-seat, reclined cockpit.

Videos: [60 s walkaround](renders/s3-rally-pod-walkaround.mp4) · [motion cue in Gravity](gravity-renders/rally-pod-two-seat-motion-cue-20261019-190855.mp4)

## What's here

| Path | What it is |
|---|---|
| `cad/pod/` | The STEVE design source: `main.py` places and joints everything, `params.py` holds the numbers, `components/` one part each |
| `cad/pod/ergo.py` | Occupant model: 5th and 95th percentile body sizes, seated posture, and the seat travel, cushion lift, column reach and pedal position they set |
| `cad/pod/mannequin.py` | Builds a seated occupant in race gear (helmet with intercom mic, HANS, suit, boots, harness) from a posture |
| `analysis/platform_loads.py` | Motion-platform loads from the CAD masses plus the occupants, for full, mixed and driver-only crews |
| `render/` | Blender walkaround driven by the CAD's own `rally_stage` animation |
| `tools/mesh_to_sim.py` | Samples the CAD meshes into the Gravity motion-cue sim |
| `sims/rally-pod-motion.js` | The Gravity sim (paste into Gravity → ✎ new sim) |
| `docs/two-seat-pod.md` | Design notes: ergonomics, fit check, platform loads, intercom, telemetry and physics stack, open items |
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
- **Open problem: the motion platform.** The stack under the floor is still the original one-seat mechanism and is
  not sized for about 510 kg of moving load. See `docs/two-seat-pod.md` §4.

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

5. Recompute the platform loads:

   ```sh
   python3 analysis/platform_loads.py render/build/mesh cad/pod
   ```

## Working on the CAD

`cad/pod` is a plain copy of the STEVE design's files. To bring it into your own STEVE workspace, create a design
and save these files into it (an AI client with STEVE's MCP server can do this with `write_design`). For a team,
work in a STEVE team workspace on a branch and let a member review and merge.

## License

MIT, no warranty. See [LICENSE](LICENSE).
