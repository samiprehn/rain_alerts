# Rain Alerts

Checks [Open-Meteo](https://open-meteo.com/) every 3 hours and sends an [ntfy](https://ntfy.sh/) push notification when rain is in tomorrow's forecast for San Diego.

In a city where it rains a dozen times a year, "bring the patio stuff in" is genuinely useful information. Alerts once per rainy day, the day before. No daily summaries — silence means dry.

## Fork this for your own city

1. **Fork this repo** (top right).
2. **Pick an ntfy topic** — any unique string, e.g. `rain-alerts-yourname-randomchars`. No registration needed; just pick something nobody else would guess.
3. **Install ntfy on your phone** — [iOS](https://apps.apple.com/us/app/ntfy/id1625396347) or [Android](https://play.google.com/store/apps/details?id=io.heckel.ntfy) — subscribe to your topic.
4. **Add repository secrets** (Settings → Secrets and variables → Actions → New repository secret):
   - `NTFY_TOPIC` — from step 2
   - `LAT` / `LON` *(optional)* — your coordinates. Default: San Diego (32.7157, -117.1611)
   - `PLACE` *(optional)* — place name used in the notification. Default `San Diego`
   - `RAIN_THRESHOLD` *(optional)* — precipitation probability (%) that triggers an alert. Default `50`
   - `TIMEZONE` *(optional)* — IANA timezone for "tomorrow". Default `America/Los_Angeles`
5. **Allow the workflow to commit back** — Settings → Actions → General → Workflow permissions → Read and write permissions.
6. **Trigger a test run** — Actions tab → Check Rain → Run workflow.

## How it works

Every 3 hours the workflow pulls tomorrow's `precipitation_probability_max` and `precipitation_sum` from Open-Meteo (free, no API key). If the probability is at or above the threshold and tomorrow hasn't already been alerted, it pushes once and remembers the date in `seen.json` — so a rainy Saturday generates exactly one ping on Friday, no matter how many times the forecast is checked.

## Files

- `check_rain.py` — main script
- `seen.json` — dates already alerted (auto-updated by the workflow)
- `.github/workflows/check.yml` — GitHub Actions workflow, every 3 hours

## Running locally

```
export NTFY_TOPIC=...
python check_rain.py
```

To force a test alert regardless of the forecast, set `RAIN_THRESHOLD=0` for the run (then reset `seen.json`).
