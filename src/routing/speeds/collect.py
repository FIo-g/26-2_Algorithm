"""ITS real-time traffic speed collector.

Every poll saves the raw API response as out_dir/YYYYMMDD/HHMMSS.json.gz so field
names can be fixed later without losing data. Failures go to out_dir/errors.log
and the loop keeps running.

The API key is read from the ITS_API_KEY environment variable (or a local .env
file that is gitignored). It is never written to disk by this module.
"""
from __future__ import annotations

import argparse
import gzip
import json
import os
import sys
import time
from collections.abc import Callable
from datetime import datetime
from pathlib import Path

ITS_URL = "https://openapi.its.go.kr:9443/trafficInfo"
# (minX, minY, maxX, maxY) in lon/lat; south edge covers Seocho-gu (37.4285).
BBOX_GSS = (126.98, 37.42, 127.19, 37.55)

Fetch = Callable[[str, dict], bytes]


def build_params(api_key: str, bbox: tuple[float, float, float, float]) -> dict[str, str]:
    min_x, min_y, max_x, max_y = bbox
    return {"apiKey": api_key, "type": "all", "drcType": "all",
            "minX": str(min_x), "maxX": str(max_x), "minY": str(min_y), "maxY": str(max_y),
            "getType": "json"}


def _log_error(out_dir: Path, now: datetime, kind: str, msg: str, api_key: str) -> None:
    if api_key:
        msg = msg.replace(api_key, "***")
    msg = msg[:200].replace("\r", " ").replace("\n", " ").replace("\t", " ")
    out_dir.mkdir(parents=True, exist_ok=True)
    with open(out_dir / "errors.log", "a", encoding="utf-8") as f:
        f.write(f"{now.isoformat()}\t{kind}: {msg}\n")


def poll_once(fetch: Fetch, api_key: str, bbox, out_dir: Path, now: datetime) -> Path | None:
    """Fetch once and save the raw bytes gzipped. Returns None on any failure."""
    out_dir = Path(out_dir)
    try:
        raw = fetch(ITS_URL, build_params(api_key, bbox))
    except Exception as e:
        _log_error(out_dir, now, type(e).__name__, str(e), api_key)
        return None
    try:
        doc = json.loads(raw)
    except ValueError as e:
        # Log the start of the body: a non-JSON reply usually explains itself.
        _log_error(out_dir, now, type(e).__name__, raw[:200].decode("utf-8", "replace"), api_key)
        return None
    header = doc.get("header") if isinstance(doc, dict) else None
    code = header.get("resultCode") if isinstance(header, dict) else None
    if code is not None and str(code) != "0":
        _log_error(out_dir, now, "ApiError", f"resultCode={code} {header.get('resultMsg', '')}", api_key)
        return None
    path = out_dir / now.strftime("%Y%m%d") / now.strftime("%H%M%S.json.gz")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(gzip.compress(raw))
    return path


def run_forever(fetch: Fetch, api_key: str, bbox, out_dir: Path, *, interval_s: float = 300,
                max_polls: int | None = None, sleep=time.sleep, clock=datetime.now) -> None:
    polls = 0
    while max_polls is None or polls < max_polls:
        start = time.monotonic()
        now = clock()                       # exactly once per poll
        try:
            poll_once(fetch, api_key, bbox, out_dir, now)
        except Exception as e:              # e.g. disk full or file lock; KeyboardInterrupt still stops the loop
            try:
                _log_error(Path(out_dir), now, type(e).__name__, str(e), api_key)
            except Exception:
                print(f"{now.isoformat()}\t{type(e).__name__}: poll failed; errors.log not writable",
                      file=sys.stderr, flush=True)
        polls += 1
        if max_polls is not None and polls >= max_polls:
            break
        sleep(max(0.0, interval_s - (time.monotonic() - start)))


def parse_items(raw: bytes) -> list[dict]:
    items = json.loads(raw)["body"]["items"]
    return [{"link_id": str(it["linkId"]), "speed_kph": float(it["speed"]),
             "created": str(it["createdDate"])} for it in items]


def load_env_file(path: Path) -> None:
    """Load KEY=VALUE lines into os.environ without overriding variables already set."""
    path = Path(path)
    if not path.is_file():
        return
    for line in path.read_text(encoding="utf-8-sig").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key, value = key.strip(), value.strip().strip('"').strip("'")
        if key and key not in os.environ:
            os.environ[key] = value


def requests_fetch(url: str, params: dict) -> bytes:
    import requests
    r = requests.get(url, params=params, timeout=30)
    r.raise_for_status()
    return r.content


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Poll ITS traffic speeds into gzipped JSON files.")
    ap.add_argument("--interval", type=float, default=300, help="seconds between polls")
    ap.add_argument("--out", type=Path, default=Path("data/speeds/raw"))
    ap.add_argument("--max-polls", type=int, default=None, help="stop after N polls (testing)")
    args = ap.parse_args(argv)
    load_env_file(Path(".env"))
    api_key = os.environ.get("ITS_API_KEY", "").strip()
    if not api_key:
        print("ITS_API_KEY is not set (environment variable or .env)", file=sys.stderr)
        return 2
    print(f"collecting every {args.interval:g}s into {args.out}", flush=True)
    run_forever(requests_fetch, api_key, BBOX_GSS, args.out,
                interval_s=args.interval, max_polls=args.max_polls)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
