#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Agrega results/<perfil>/*.xml -> results/<perfil>/summary.json y tabla por nivel."""
import json, os, sys, xml.etree.ElementTree as ET
sys.path.insert(0, os.path.dirname(__file__))
from defects import LEVELS, TEST_DEFECTS

def load(res_dir):
    out = []
    for key, level, target in LEVELS:
        f = os.path.join(res_dir, key + ".xml")
        if not os.path.exists(f):
            continue
        for tc in ET.parse(f).getroot().iter("testcase"):
            name = tc.get("name"); t = float(tc.get("time") or 0)
            fail = tc.find("failure"); skip = tc.find("skipped")
            msg = (fail.get("message") if fail is not None else "") or (fail.text if fail is not None else "") or ""
            status = "SKIP" if skip is not None else ("FAIL" if fail is not None else "PASS")
            defs = TEST_DEFECTS.get(key, {}).get(name, []) if status == "FAIL" else []
            blocked = status == "FAIL" and "la CPU no arranca" in (fail.text or "") + msg
            out.append(dict(key=key, level=level, target=target, name=name, status=status, time=t, msg=msg.strip()[:300],
                            defects=defs, blocked=blocked))
    return out

def main(res_dir):
    rows = load(res_dir)
    json.dump(rows, open(os.path.join(res_dir, "summary.json"), "w"), indent=1, ensure_ascii=False)
    print(f"\n=== {os.path.basename(res_dir)} ===")
    print(f"{'Nivel':<12}{'Objetivo':<20}{'PASS':>5}{'FAIL':>6}{'bloq.':>7}{'total':>7}")
    for key, level, target in LEVELS:
        r = [x for x in rows if x["key"] == key]
        if not r: continue
        p = sum(x["status"] == "PASS" for x in r); f = sum(x["status"] == "FAIL" for x in r)
        b = sum(x["blocked"] for x in r)
        print(f"{level:<12}{target:<20}{p:>5}{f:>6}{b:>7}{len(r):>7}")
    tot = len(rows); p = sum(x["status"] == "PASS" for x in rows)
    print(f"{'TOTAL':<32}{p:>5}{tot - p:>6}{'':>7}{tot:>7}")
    unk = [x for x in rows if x["status"] == "FAIL" and not x["defects"] and not x["blocked"]]
    if unk:
        print("\nFALLOS SIN DEFECTO ASOCIADO:")
        for x in unk: print("  ", x["key"], x["name"], "-", x["msg"][:120].replace("\n", " "))

if __name__ == "__main__":
    main(sys.argv[1])
