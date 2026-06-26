# Pinehurst 2026

Golf trip dashboard for 9 players at Pinehurst Resort, September 2026.

**Live site:** https://nathanmjlee22.github.io/pinehurst/

## Features
- Handicap index history graph for all 9 players (pulled from GHIN)
- Course info table with yardage, rating, and slope for Blue & White tees
- Match-play scoreboard (Team Expand vs Team Shrink) with tee selection and stroke allocation
- Stroke play leaderboard sorted by total gross score
- Cross-device score sync via `scores.json` on GitHub

## Updating handicap data
The page refreshes automatically every morning at 3 AM PST via GitHub Actions. To trigger a manual refresh, go to **Actions → Refresh GHIN Data → Run workflow** in this repo.

## Entering scores during the trip
Open the live site on any device. When a match result or tee is changed, a **💾 Save Scores** button appears — tap it to sync to all devices. Requires a GitHub PAT with `contents: write` scope stored locally on first use.

## Local development
```bash
# Set GHIN credentials
export USER=your@email.com
export PASSWORD=yourpassword

# Fetch latest GHIN data and rebuild
python fetch_ghin.py && python build_page.py
```

Requires Python 3.11+ and `pip install requests`.

## Rounds
| Round | Date | Course |
|-------|------|--------|
| 1 | Sep 4 | No. 10 |
| 2 | Sep 5 | No. 4  |
| 3 | Sep 5 | No. 2  |
| 4 | Sep 6 | No. 8  |
