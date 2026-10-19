// S3 Rally Pod motion cue, sampled from the STEVE CAD (tools/mesh_to_sim.py fills POINTS).
// Two-seat rally cockpit: driver, co-driver, wheel, pedals and dash ride the floor; the shell,
// windscreen and side-window displays stay fixed. Stops as in the CAD:
// surge ±50 mm, roll ±7 deg, pitch ±7 deg, heave ±40 mm.
// The cue is the CAD's rally_stage animation. Visual gain only scales the picture;
// observe() reports true millimetres and degrees.

const POINTS = /*POINTS*/null;

export const meta = {
  title: 'Rally pod two-seat motion cue',
  summary: 'The CAD rally_stage cue (bump, jump, landing, corner) on the two-seat pod. Gauges show how much of each stop is used.',
  particleCount: /*COUNT*/12000,
  dt: 0.016,
  params: [
    { key: 'gain', label: 'Visual gain', min: 1, max: 3, step: 0.1, default: 1.6 },
    { key: 'jump', label: 'Jump size', min: 0.4, max: 1, step: 0.05, default: 1 },
  ],
  camera: { position: [3.4, 2.3, 2.9], target: [0.0, 1.05, 0.0] },
  pointSize: 0.006,
  trail: 20,
  bloom: 0.3,
  doc: {
    about: 'Motion cue for the enclosed two-seat rally pod, drawn from the CAD meshes. The shell and screens stay put; the floor carries both occupants, the seats, wheel, pedals and dash on surge, roll, pitch and heave.',
    howItWorks: 'A 9.6 s stage keyed like the CAD animation: bump, jump, flight, landing, then a long corner. Each point belongs to a motion stage: the floor turns about the universal joint (pitch inside roll), heaves and surges; the four cranks and links are solved exactly each step to follow it.',
    equations: [
      { label: 'chain', latex: 'p_w = S_x\\,R_x(\\phi)\\,R_y(\\theta)\\,H_z\\,p' },
    ],
    symbols: [
      { key: 'gain', symbol: 'g', meaning: 'Picture scale only. Measured travel ignores it.' },
      { key: 'jump', symbol: 'A', meaning: 'Scales every key of the cue. 1 is the full stage.' },
    ],
    integrator: 'Direct sample of a scripted cue with smoothstep easing between keys. No force integration.',
    mapping: '1 world unit = 700 mm. Y is up. Roll about X and pitch about Y through the universal joint, as in the CAD.',
    assumptions: 'Cue values are the CAD poses. Occupants are 95th percentile mannequins in race gear.',
    limitations: 'No actuator dynamics, compliance or washout. Motion is the scripted cue, not a vehicle model.',
    references: [],
  },
};

const LOOP = 9.6;
const S = 1 / 700;
const KEYS = [
  [0, { h: 0, p: 0, s: 0, r: 0 }],
  [1.2, { h: 22, p: 2, s: -8, r: 0 }],
  [2.0, { h: 0, p: 0, s: 0, r: 0 }],
  [3.2, { h: 32, p: 7, s: 18, r: 1 }],
  [4.2, { h: 8, p: 4, s: 40, r: -1 }],
  [5.0, { h: -40, p: -7, s: -30, r: -2 }],
  [6.4, { h: 0, p: 0, s: 0, r: 0 }],
  [8.0, { h: 12, p: -1, s: 6, r: -7 }],
  [9.6, { h: 0, p: 0, s: 0, r: 0 }],
];
const LIMITS = { h: 40, p: 7, s: 50, r: 7 };

function b64(str) {
  const tbl = new Int16Array(128).fill(-1);
  const abc = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/';
  for (let i = 0; i < 64; i++) tbl[abc.charCodeAt(i)] = i;
  let len = (str.length / 4) * 3;
  if (str.endsWith('==')) len -= 2;
  else if (str.endsWith('=')) len -= 1;
  const out = new Uint8Array(len);
  let o = 0;
  for (let i = 0; i < str.length; i += 4) {
    const a = tbl[str.charCodeAt(i)], b = tbl[str.charCodeAt(i + 1)];
    const c = tbl[str.charCodeAt(i + 2)], d = tbl[str.charCodeAt(i + 3)];
    const v = (a << 18) | (b << 12) | ((c < 0 ? 0 : c) << 6) | (d < 0 ? 0 : d);
    if (o < len) out[o++] = (v >> 16) & 255;
    if (o < len) out[o++] = (v >> 8) & 255;
    if (o < len) out[o++] = v & 255;
  }
  return out;
}

function ease(x) {
  const t = Math.max(0, Math.min(1, x));
  return t * t * (3 - 2 * t);
}

function cue(u, amp, out) {
  for (let k = 0; k < KEYS.length - 1; k++) {
    const [ta, a] = KEYS[k];
    const [tb, b] = KEYS[k + 1];
    if (u >= ta && u <= tb) {
      const w = ease((u - ta) / (tb - ta));
      out.h = amp * (a.h + (b.h - a.h) * w);
      out.p = amp * (a.p + (b.p - a.p) * w);
      out.s = amp * (a.s + (b.s - a.s) * w);
      out.r = amp * (a.r + (b.r - a.r) * w);
      return out;
    }
  }
  out.h = out.p = out.s = out.r = 0;
  return out;
}

export function create(ctx) {
  const { positions: pos, colors: col, particleCount: n } = ctx;
  const raw = b64(POINTS.pos);
  const xyz = new Int16Array(raw.buffer, 0, POINTS.count * 3);
  const stage = b64(POINTS.stage);
  const colour = b64(POINTS.colour);
  const m = Math.min(POINTS.count, n);
  const gauge0 = m;
  const gaugeN = Math.max(0, Math.min(80, Math.floor((n - m) / 4)));

  for (let i = 0; i < n; i++) {
    const o = i * 3;
    if (i < m) {
      const c = POINTS.palette[colour[i]];
      col[o] = c[0];
      col[o + 1] = c[1];
      col[o + 2] = c[2];
    } else {
      pos[o] = 0;
      pos[o + 1] = -3;
      pos[o + 2] = 0;
      col[o] = col[o + 1] = col[o + 2] = 0;
    }
  }

  let t = 0;
  let amp = 1;
  const c = { h: 0, p: 0, s: 0, r: 0 };
  const peak = { h: 0, p: 0, s: 0, r: 0 };

  const PV = POINTS.pivot, R = POINTS.crankR, L = POINTS.linkLen, ACTS = POINTS.acts;
  const crankAng = new Float64Array(4), tipX = new Float64Array(4), tipZ = new Float64Array(4);
  const linkTilt = new Float64Array(4);

  // Pitch (about Y) inside roll (about X), both about the universal joint, then heave. In mm.
  function floorPoint(x, y, z, sp, cp, sr, cr, heave, out) {
    const dx = x - PV[0], dz = z - PV[2];
    const x1 = dx * cp + dz * sp;
    const z1 = -dx * sp + dz * cp;
    out[0] = x1 + PV[0];
    out[1] = y * cr - z1 * sr;
    out[2] = y * sr + z1 * cr + PV[2] + heave;
  }

  const tmp = [0, 0, 0];
  function solve(sp, cp, sr, cr, heave) {
    for (let a = 0; a < 4; a++) {
      const act = ACTS[a];
      floorPoint(act.pin[0], act.pin[1], act.pin[2], sp, cp, sr, cr, heave, tmp);
      const ddx = tmp[0] - act.axis[0], ddz = tmp[2] - act.axis[2];
      const d = Math.hypot(ddx, ddz);
      const c = Math.max(-1, Math.min(1, (R * R + d * d - L * L) / (2 * R * d)));
      const tipAng = Math.atan2(ddz, ddx) - Math.acos(c);
      crankAng[a] = tipAng;
      tipX[a] = act.axis[0] + R * Math.cos(tipAng);
      tipZ[a] = act.axis[2] + R * Math.sin(tipAng);
      linkTilt[a] = Math.atan2(tmp[0] - tipX[a], tmp[2] - tipZ[a]);
    }
  }

  function place(g) {
    const rad = Math.PI / 180;
    const sp = Math.sin(c.p * g * rad), cp = Math.cos(c.p * g * rad);
    const sr = Math.sin(c.r * g * rad), cr = Math.cos(c.r * g * rad);
    const heave = c.h * g, surge = c.s * g;
    solve(sp, cp, sr, cr, heave);
    for (let i = 0; i < m; i++) {
      let x = xyz[i * 3], y = xyz[i * 3 + 1], z = xyz[i * 3 + 2];
      const st = stage[i];
      if (st >= 5 && st <= 8) {
        // Crank: turn about its axis (CCW in X-Z by the tip angle).
        const act = ACTS[st - 5], a = crankAng[st - 5];
        const dx = x - act.axis[0], dz = z - act.axis[2];
        x = act.axis[0] + dx * Math.cos(a) - dz * Math.sin(a);
        z = act.axis[2] + dx * Math.sin(a) + dz * Math.cos(a);
      } else if (st >= 9) {
        // Link: tilt about its bottom pin, then move the pin to the crank tip.
        const k = st - 9, act = ACTS[k], t = linkTilt[k];
        const dx = x - act.tip[0], dz = z - act.tip[2];
        x = tipX[k] + dx * Math.cos(t) + dz * Math.sin(t);
        z = tipZ[k] - dx * Math.sin(t) + dz * Math.cos(t);
      } else if (st >= 2) {
        if (st >= 4) {
          const dx = x - PV[0], dz = z - PV[2];
          const x1 = dx * cp + dz * sp;
          z = -dx * sp + dz * cp + PV[2];
          x = x1 + PV[0];
        }
        if (st >= 3) {
          const dz = z - PV[2];
          const y1 = y * cr - dz * sr;
          z = y * sr + dz * cr + PV[2];
          y = y1;
        }
        z += heave;
      }
      if (st >= 1) x += surge;
      const o = i * 3;
      pos[o] = x * S;
      pos[o + 1] = z * S;
      pos[o + 2] = -y * S;
    }
  }

  function gauges() {
    const vals = [c.h / LIMITS.h, c.p / LIMITS.p, c.s / LIMITS.s, c.r / LIMITS.r];
    for (let g = 0; g < 4; g++) {
      const frac = Math.max(-1, Math.min(1, vals[g]));
      const hot = Math.abs(frac) > 0.92;
      for (let k = 0; k < gaugeN; k++) {
        const o = (gauge0 + g * gaugeN + k) * 3;
        const along = (k / (gaugeN - 1)) * 2 - 1;
        pos[o] = 1.75;
        pos[o + 1] = 0.35 + g * 0.24;
        pos[o + 2] = 1.55 + along * 0.32;
        const on = along >= 0 ? along <= frac : along >= frac;
        if (k === (gaugeN >> 1)) {
          col[o] = col[o + 1] = col[o + 2] = 0.9;
        } else if (on) {
          col[o] = hot ? 1 : 0.95;
          col[o + 1] = hot ? 0.25 : 0.75;
          col[o + 2] = 0.2;
        } else {
          col[o] = 0.18;
          col[o + 1] = 0.2;
          col[o + 2] = 0.24;
        }
      }
    }
  }

  cue(0, amp, c);
  place(1);
  if (gaugeN > 1) gauges();

  return {
    step(dt, p) {
      t += dt;
      amp = p.jump;
      cue(t % LOOP, amp, c);
      peak.h = Math.max(peak.h, Math.abs(c.h));
      peak.p = Math.max(peak.p, Math.abs(c.p));
      peak.s = Math.max(peak.s, Math.abs(c.s));
      peak.r = Math.max(peak.r, Math.abs(c.r));
      place(p.gain);
      if (gaugeN > 1) gauges();
    },
    observe() {
      const used = Math.max(Math.abs(c.h) / LIMITS.h, Math.abs(c.p) / LIMITS.p,
        Math.abs(c.s) / LIMITS.s, Math.abs(c.r) / LIMITS.r);
      return {
        heaveMm: c.h, pitchDeg: c.p, surgeMm: c.s, rollDeg: c.r,
        peakHeaveMm: peak.h, peakPitchDeg: peak.p, peakSurgeMm: peak.s, peakRollDeg: peak.r,
        stopUsed: used, saturated: used > 0.98 ? 1 : 0,
      };
    },
  };
}
