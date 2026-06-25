#!/usr/bin/env python3
"""Fetch fresh GHIN handicap revisions and recent rounds for all golfers."""
import os, json, sys, requests
from datetime import date

BASE = "https://api.ghin.com/api/v1"
S = requests.Session()
S.headers.update({
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15",
    "Accept": "application/json",
    "Content-Type": "application/json",
    "Origin": "https://www.ghin.com",
    "Referer": "https://www.ghin.com/",
})

GOLFERS = {
    "7866286": {"name": "Eddie Mclaughlin", "club": "Costa Mesa GC",      "color": "#d4af37"},
    "7562830": {"name": "Nathan Lee",        "club": "Maderas GC",         "color": "#f0f7f2"},
    "11367668": {"name": "David Ryu",        "club": "Costa Mesa GC",      "color": "#6dbf82"},
    "11634995": {"name": "Adam Hawk",        "club": "AZ Under30",         "color": "#a8d5b5"},
    "10460818": {"name": "John McGinley",    "club": "EClub Monterey Bay", "color": "#e8c84a"},
    "3031631":  {"name": "Alec Negri",       "club": "USGA/SCGA GC",       "color": "#b5d99c"},
}

def login():
    username = os.environ.get("USER")
    password = os.environ.get("PASSWORD")
    if not password:
        print("ERROR: PASSWORD env var not set", file=sys.stderr)
        sys.exit(1)
    r = S.post(f"{BASE}/golfer_login.json", json={
        "user": {"email_or_ghin": username, "password": password, "remember_me": True},
        "token": "123",
    })
    r.raise_for_status()
    return r.json()["golfer_user"]["golfer_user_token"]

def fetch_golfer_info(ghin, hdrs):
    r = S.get(f"{BASE}/golfers/search.json", headers=hdrs,
              params={"golfer_id": ghin, "per_page": 1, "page": 1, "status": "active"})
    if r.status_code == 200 and r.json().get("golfers"):
        g = r.json()["golfers"][0]
        return {"current": str(g.get("handicap_index", "")), "low": str(g.get("low_hi", ""))}
    return {"current": "", "low": ""}

def fetch_revisions(ghin, hdrs):
    today = date.today().isoformat()
    r = S.get(f"{BASE}/golfers/{ghin}/handicap_history.json", headers=hdrs,
              params={"rev_count": 500, "date_begin": "2000-01-01", "date_end": today})
    if r.status_code != 200:
        return []
    revs = r.json().get("handicap_revisions", [])
    valid = [rev for rev in reversed(revs) if rev["Display"] not in ("NH", None, "")]
    return [{"date": rev["RevDate"][:10], "hi": float(rev["Value"])} for rev in valid]

def fetch_rounds(ghin, hdrs):
    r = S.get(f"{BASE}/scores/search.json", headers=hdrs, params={
        "golfer_id": ghin, "per_page": 20, "page": 1,
        "from_date_played": "2000-01-01", "status": "Posted",
    })
    if r.status_code != 200:
        return []
    scores = r.json().get("Scores", [])
    scores.sort(key=lambda s: s["played_at"], reverse=True)
    recent = scores[:20]
    result = []
    for s in recent:
        if s.get("handicap_index") is None:
            continue
        result.append({
            "date": s["played_at"],
            "hi": float(s["handicap_index"]),
            "course": s.get("course_name", ""),
            "score": s.get("adjusted_gross_score"),
            "holes": s.get("number_of_holes", 18),
        })
    result.sort(key=lambda x: x["date"])
    return result

def main():
    print("Logging in...")
    token = login()
    hdrs = {"Authorization": f"Bearer {token}"}

    data = {}
    for ghin, meta in GOLFERS.items():
        print(f"Fetching {meta['name']} ({ghin})...")
        info = fetch_golfer_info(ghin, hdrs)
        revs = fetch_revisions(ghin, hdrs)
        rounds = fetch_rounds(ghin, hdrs)
        data[ghin] = {
            "name": meta["name"],
            "club": meta["club"],
            "color": meta["color"],
            "current": info["current"] or (str(revs[-1]["hi"]) if revs else ""),
            "low": info["low"],
            "revs": revs,
            "rounds": rounds,
        }
        print(f"  {len(revs)} revisions, {len(rounds)} rounds, current HI={data[ghin]['current']}")

    out = f"/Users/nathan.lee/pinehurst/ghin_data.json"
    with open(out, "w") as f:
        json.dump(data, f, indent=2)
    print(f"\nSaved to {out}")

if __name__ == "__main__":
    main()
