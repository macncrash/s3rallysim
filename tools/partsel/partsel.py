"""Part selector: check candidate parts against a project's requirements.

Part cards live in parts/<category>/*.toml, one file per orderable part. Every value carries its source
(a URL from the card's [sources] table plus a page), so a result can always be traced back to the vendor's
own document. A requirements file names the category, the operating point and the checks.

    python3 tools/partsel/partsel.py unknown-machine/requirements/motor.toml
    python3 tools/partsel/partsel.py unknown-machine/requirements/motor.toml --detail
    python3 tools/partsel/partsel.py unknown-machine/requirements/motor.toml --json
    python3 tools/partsel/partsel.py unknown-machine/requirements/motor.toml --brief --set bus_vdc=48

Verdicts: PASS (every hard check met), FAIL (a hard check failed), CHECK (no hard check failed, but a value
is missing from the card, so it can't be confirmed yet). Soft checks ("prefer") only rank.
Plain Python 3.11+, no dependencies.
"""
import argparse
import json
import math
import sys
import tomllib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PARTS = ROOT / "parts"


def load_cards(category):
    folder = PARTS / category
    if not folder.is_dir():
        sys.exit(f"No part folder {folder}")
    cards = []
    for path in sorted(folder.glob("*.toml")):
        with path.open("rb") as f:
            card = tomllib.load(f)
        card["_file"] = str(path.relative_to(ROOT))
        cards.append(card)
    return cards


def value(card, field):
    """A card value, or None when the card doesn't have it. Values are {v = ..., src = ..., page = ...}."""
    entry = card.get("values", {}).get(field, card.get(field))   # top-level fields (maker, country) too
    if entry is None:
        return None
    return entry["v"] if isinstance(entry, dict) else entry


def source(card, field):
    entry = card.get("values", {}).get(field)
    if entry is None and field in card:
        return f"part card ({card['_file']})"
    if not isinstance(entry, dict) or "src" not in entry:
        return ""
    src = card.get("sources", {}).get(entry["src"], {})
    page = f", p. {entry['page']}" if "page" in entry else ""
    return f"{src.get('title', entry['src'])}{page} <{src.get('url', '')}>"


def derived(card, operating):
    """Values worked out from the card and the operating point, e.g. the DC bus a winding needs."""
    out = {}
    speed = operating.get("speed_rpm")
    kb = value(card, "kb_vrms_per_krpm")                 # line-line back-EMF constant
    if speed and kb:
        # Sinusoidal drive: peak line-line voltage must stay below the DC bus; 15% for IR drop and control.
        out["bus_vdc_needed"] = round(kb * speed / 1000 * math.sqrt(2) * 1.15, 1)
    elif speed and value(card, "rated_bus_vdc") and value(card, "rated_speed_rpm"):
        out["bus_vdc_needed"] = round(value(card, "rated_bus_vdc") * speed / value(card, "rated_speed_rpm"), 1)
    kt, tp = value(card, "kt_nm_per_arms"), operating.get("peak_torque_nm")
    if kt and tp:
        out["current_at_peak_torque_arms"] = round(tp / kt, 2)
    t2n, k_stop, pct = (value(card, "nominal_output_torque_nm"), value(card, "estop_torque_factor"),
                        value(card, "accel_torque_pct_of_estop"))
    if t2n and k_stop and value(card, "emergency_stop_torque_nm") is None:
        # Gearboxes that print torque ratings as rules of the nominal torque (e.g. "T2NOT = 3 x T2N").
        out["emergency_stop_torque_nm"] = t2n * k_stop
        if pct and value(card, "max_accel_output_torque_nm") is None:
            out["max_accel_output_torque_nm"] = round(t2n * k_stop * pct / 100)
    c0, b6 = value(card, "static_radial_load_n"), value(card, "alternating_load_factor")
    if c0 and b6:
        # Rod ends: the housing's static rating times the maker's factor for alternating load direction.
        out["permissible_alternating_load_n"] = round(c0 * b6)
    return out


def check(card, rule, extra, operating):
    field = rule["field"]
    v = extra.get(field, value(card, field))
    if isinstance(rule.get("max"), str):                 # a limit taken from the operating point
        rule = {**rule, "max": operating[rule["max"]]}
    if isinstance(rule.get("min"), str):
        rule = {**rule, "min": operating[rule["min"]]}
    if v is None:
        return "?", None
    ok = True
    if "min" in rule:
        ok &= v >= rule["min"]
    if "max" in rule:
        ok &= v <= rule["max"]
    if "equals" in rule:
        ok &= v == rule["equals"]
    if "in" in rule:
        ok &= v in rule["in"]
    return ("ok" if ok else "no"), v


def limit_text(rule, operating):
    parts = []
    for key, sym in (("min", ">="), ("max", "<="), ("equals", "=="), ("in", "in")):
        if key in rule:
            lim = operating[rule[key]] if key in ("min", "max") and isinstance(rule[key], str) else rule[key]
            parts.append(f"{sym} {lim}")
    return " and ".join(parts)


def evaluate(req):
    operating = req.get("operating", {})
    results = []
    for card in load_cards(req["category"]):
        extra = derived(card, operating)
        rows, verdict, score = [], "PASS", 0
        for rule in req.get("check", []):
            status, v = check(card, rule, extra, operating)
            soft = rule.get("prefer", False)
            if status == "no" and not soft:
                verdict = "FAIL"
            elif status == "?" and not soft and verdict == "PASS":
                verdict = "CHECK"
            if soft and status == "ok":
                score += 1
            rows.append({"field": rule["field"], "limit": limit_text(rule, operating), "value": v,
                         "status": status, "soft": soft, "why": rule.get("why", ""),
                         "source": source(card, rule["field"]) if rule["field"] not in extra else "derived"})
        results.append({"id": card.get("id"), "model": card.get("model"), "maker": card.get("maker"),
                        "country": card.get("country"), "file": card["_file"], "verdict": verdict,
                        "preferred": score, "derived": extra, "checks": rows, "notes": card.get("notes", "")})
    order = {"PASS": 0, "CHECK": 1, "FAIL": 2}
    results.sort(key=lambda r: (order[r["verdict"]], -r["preferred"], r["id"]))
    return results


def mark(row):
    sym = {"ok": "ok", "no": "NO", "?": "?"}[row["status"]]
    return f"({sym})" if row["soft"] else sym


def print_table(req, results, detail):
    checks = req.get("check", [])
    print(f"# {req.get('title', req['category'])}\n")
    op = ", ".join(f"{k} = {v}" for k, v in req.get("operating", {}).items())
    if op:
        print(f"Operating point: {op}\n")
    print("| Part | Maker | Verdict | " + " | ".join(c["field"] for c in checks) + " |")
    print("|---|---|---|" + "---|" * len(checks))
    for r in results:
        cells = [f"{mark(c)} {c['value'] if c['value'] is not None else ''}".strip() for c in r["checks"]]
        print(f"| {r['model']} | {r['maker']} ({r['country']}) | **{r['verdict']}** | " + " | ".join(cells) + " |")
    print("\nok / NO / ? = met / not met / not on the card. (brackets) = preference, ranks only.")
    print("\nLimits: " + "; ".join(f"{c['field']} {limit_text(c, req.get('operating', {}))}" for c in checks))
    if detail:
        for r in results:
            print(f"\n## {r['model']} ({r['file']}): {r['verdict']}\n")
            if r["derived"]:
                print("Derived: " + ", ".join(f"{k} = {v}" for k, v in r["derived"].items()) + "\n")
            for c in r["checks"]:
                if c["status"] != "ok":
                    tag = "missing" if c["status"] == "?" else "fails"
                    print(f"- {c['field']} {tag} ({c['limit']}): {c['why']}")
            for c in r["checks"]:
                if c["value"] is not None:
                    print(f"  - {c['field']} = {c['value']}: {c['source']}")
            if r["notes"]:
                print(f"\nNotes: {r['notes']}")


def print_brief(req, results):
    """One line per part: verdict, model, maker, and what failed or is missing."""
    print(f"{req.get('title', req['category'])}  ({', '.join(f'{k}={v}' for k, v in req.get('operating', {}).items())})")
    for r in results:
        hard = [c for c in r["checks"] if not c["soft"]]
        fails = [f"{c['field']} {c['value']} (needs {c['limit']})" for c in hard if c["status"] == "no"]
        missing = [c["field"] for c in hard if c["status"] == "?"]
        soft = [c for c in r["checks"] if c["soft"]]
        why = "; ".join(fails) or (("missing " + ", ".join(missing)) if missing else
                                   f"preferences {r['preferred']}/{len(soft)}")
        print(f"  {r['verdict']:<5}  {r['model']:<14} {r['maker'] + ' (' + r['country'] + ')':<20} {why}")


def parse_set(items):
    """--set key=value overrides for the [operating] table (numbers where they parse)."""
    out = {}
    for item in items:
        key, _, raw = item.partition("=")
        try:
            out[key] = float(raw) if "." in raw else int(raw)
        except ValueError:
            out[key] = raw
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("requirements", help="requirements .toml")
    ap.add_argument("--detail", action="store_true", help="explain each failure and cite every value")
    ap.add_argument("--json", action="store_true", help="machine-readable output")
    ap.add_argument("--brief", action="store_true", help="one line per part, for a terminal")
    ap.add_argument("--set", action="append", default=[], metavar="KEY=VALUE",
                    help="what-if: override an [operating] value, e.g. --set bus_vdc=48 (repeatable)")
    args = ap.parse_args()
    with open(args.requirements, "rb") as f:
        req = tomllib.load(f)
    req["operating"] = {**req.get("operating", {}), **parse_set(args.set)}
    results = evaluate(req)
    if args.brief:
        print_brief(req, results)
    elif args.json:
        json.dump(results, sys.stdout, indent=2)
        print()
    else:
        print_table(req, results, args.detail)
    return 0 if any(r["verdict"] == "PASS" for r in results) else 1


if __name__ == "__main__":
    sys.exit(main())
