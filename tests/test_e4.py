import importlib.util
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
_spec = importlib.util.spec_from_file_location("run_e4", REPO / "scripts" / "run_e4.py")
e4 = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(e4)


def test_trips_rows_and_summary(tmp_path):
    p = tmp_path / "tripinfo.xml"
    p.write_text('<tripinfos>'
                 '<tripinfo id="a" depart="0" arrival="80" duration="80" devices="tripinfo_a routing_a"/>'
                 '<tripinfo id="b" depart="0" arrival="100" duration="100" devices="tripinfo_b"/>'
                 '<tripinfo id="c" depart="10" arrival="-1.00" duration="300" devices="tripinfo_c"/>'
                 '<tripinfo id="d" depart="-1" arrival="-1.00" duration="0.00" devices="tripinfo_d"/>'
                 '</tripinfos>', encoding="utf-8")
    trips = e4.trips(p)
    assert trips == [(80.0, True, True, True), (100.0, True, True, False),
                     (300.0, False, True, False), (0.0, False, False, False)]

    rows = {r["group"]: r for r in e4.run_rows("W", "medium", "reroute30", 1, trips)}
    # c (stuck, 300 s so far) counts as a lower bound; d never departed and counts only as not arrived
    assert rows["all"]["mean_tt_s"] == 160 and rows["all"]["mean_tt_arrived_s"] == 90
    assert rows["all"]["arrived_pct"] == 50 and rows["all"]["p95_tt_s"] == 300
    assert rows["equipped"]["mean_tt_s"] == 80 and rows["unequipped"]["arrived_pct"] == 33.33
    fixed = e4.run_rows("W", "medium", "fixed", 1, [(200.0, True, True, False)])
    assert [r["group"] for r in fixed] == ["all"]  # equipped/unequipped only for the 30% runs

    summary = {(o["strategy"], o["group"]): o for o in e4.summarize(fixed + list(rows.values()))}
    assert summary[("fixed", "all")]["change_pct"] == 0
    assert summary[("reroute30", "all")]["change_pct"] == -20  # 160 s vs 200 s
