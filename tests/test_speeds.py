"""Collector tests with a fake fetch; no network access or API key is required."""
from __future__ import annotations

import gzip
import os
from datetime import datetime

from routing.speeds.collect import (
    BBOX_GSS, build_params, load_env_file, parse_items, poll_once, run_forever,
)

SAMPLE = b'{"header":{"resultCode":0},"body":{"items":[{"linkId":"1220001200","speed":"34.5","createdDate":"20261030083000"}]}}'


def test_poll_once_saves_gzip(tmp_path):
    p = poll_once(lambda url, params: SAMPLE, "K", BBOX_GSS, tmp_path, datetime(2026, 10, 30, 8, 30, 0))
    assert p == tmp_path / "20261030" / "083000.json.gz"
    assert gzip.decompress(p.read_bytes()) == SAMPLE


def test_parse_items():
    assert parse_items(SAMPLE) == [{"link_id": "1220001200", "speed_kph": 34.5, "created": "20261030083000"}]


def test_collector_survives_errors(tmp_path):            # Review Focus 1
    calls = iter([TimeoutError("t"), b"<xml>error</xml>", SAMPLE])
    def fetch(url, params):
        r = next(calls)
        if isinstance(r, Exception): raise r
        return r
    run_forever(fetch, "K", BBOX_GSS, tmp_path, max_polls=3, sleep=lambda s: None,
                clock=iter([datetime(2026, 10, 30, 0, i) for i in range(3)]).__next__)
    assert len((tmp_path / "errors.log").read_text().splitlines()) == 2
    assert len(list(tmp_path.rglob("*.json.gz"))) == 1


def test_build_params():
    p = build_params("K", BBOX_GSS)
    assert p == {"apiKey": "K", "type": "all", "drcType": "all",
                 "minX": "126.98", "maxX": "127.19", "minY": "37.42", "maxY": "37.55",
                 "getType": "json"}


def test_api_error_code_is_logged_not_saved(tmp_path):
    bad = b'{"header":{"resultCode":"99","resultMsg":"invalid key"},"body":{"items":[]}}'
    assert poll_once(lambda u, p: bad, "K", BBOX_GSS, tmp_path, datetime(2026, 10, 30)) is None
    assert "invalid key" in (tmp_path / "errors.log").read_text()
    assert not list(tmp_path.rglob("*.json.gz"))


def test_error_log_never_contains_key(tmp_path):
    def fetch(url, params):
        raise RuntimeError(f"403 Forbidden for url: {url}?apiKey={params['apiKey']}")
    poll_once(fetch, "SECRET123", BBOX_GSS, tmp_path, datetime(2026, 10, 30))
    log = (tmp_path / "errors.log").read_text()
    assert "SECRET123" not in log and "***" in log


def test_collector_survives_write_errors(tmp_path):
    (tmp_path / "20261030").write_text("x")   # a file where the day directory belongs
    run_forever(lambda u, p: SAMPLE, "K", BBOX_GSS, tmp_path, max_polls=2, sleep=lambda s: None,
                clock=iter([datetime(2026, 10, 30, 0, i) for i in range(2)]).__next__)
    assert len((tmp_path / "errors.log").read_text().splitlines()) == 2


def test_load_env_file_does_not_override(tmp_path, monkeypatch):
    env = tmp_path / ".env"
    env.write_text('# comment\nITS_API_KEY="from-file"\nSEOUL_API_KEY=abc\n\n', encoding="utf-8")
    monkeypatch.delenv("ITS_API_KEY", raising=False)
    monkeypatch.setenv("SEOUL_API_KEY", "from-shell")
    load_env_file(env)
    assert os.environ["ITS_API_KEY"] == "from-file"
    assert os.environ["SEOUL_API_KEY"] == "from-shell"
    load_env_file(tmp_path / "missing.env")             # absent file is not an error
