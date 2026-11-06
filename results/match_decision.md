REJECT
Real ITS speeds were collected but cannot be used for E3 before the 11/5 freeze: the ITS API monthly call limit ended collection on 2026-11-03 03:21 KST before any 08 h snapshot existed.

## What we did

- Built a collector (`routing.speeds.collect`, Task 2) that polls the ITS traffic API every 5 minutes over the Gangnam, Seocho and Songpa bounding box. It saves every raw response and keeps running through timeouts, non-JSON replies and file write errors (8 tests in `tests/test_speeds.py`).
- Collected 142 snapshots between 2026-10-31 16:30 and 2026-11-03 03:16 KST. The first snapshot held 7,441 links, including Olympic-daero, Yangjae-daero and Gangbyeon-buk-ro.
- When laptop sleep left gaps, moved collection on 2026-11-03 01:26 to an always-on desktop: sleep disabled, automatic restart at boot, remote checks over Tailscale.
- Diagnosed the stop from the API reply itself: HTTP 401 with resultCode 4001, "monthly API call limit exceeded", after about 100 successful calls in November.

## Why REJECT

- The real-speed E3 scenarios need 03 h, 08 h and 18 h snapshots. We have 03 h (2026-11-03) and 18 h (2026-10-31), but no 08 h.
- Polling every 5 minutes takes about 288 calls a day, so this limit stops collection within a day whenever it starts. Raising the limit is a request on the ITS site with no guaranteed turnaround before 11/5.
- Without speeds for all three hours, matching ITS links to OSM edges cannot change the E3 result, so the matching was not run. Task 21 is skipped and E3 uses the synthetic congestion scenarios (Task 15), as the plan specifies for this case.

## Next time

- Check the API key's call limit before collecting, and poll only around the target hours (for example 03, 08 and 18 h). That fits within a small monthly limit.
