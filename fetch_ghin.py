#!/usr/bin/env python3
"""Fetch fresh GHIN handicap revisions, recent rounds, and tournament scores."""
import os, json, sys, math, requests
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
    "7866286": {"name": "Eddie Mclaughlin", "club": "Costa Mesa GC",      "color": "#1a5c35"},
    "7562830": {"name": "Nathan Lee",        "club": "Maderas GC",         "color": "#b45309"},
    "11367668": {"name": "David Ryu",        "club": "Costa Mesa GC",      "color": "#1d4ed8"},
    "11634995": {"name": "Adam Hawk",        "club": "AZ Under30",         "color": "#7c3aed"},
    "10460818": {"name": "John McGinley",    "club": "EClub Monterey Bay", "color": "#be123c"},
    "3031631":  {"name": "Alec Negri",       "club": "USGA/SCGA GC",       "color": "#0e7490"},
    "8676617":  {"name": "Dillon Staples",   "club": "NCGA NEXT",          "color": "#d97706"},
    "11466889": {"name": "Mike Gronstal",    "club": "USGA/SCGA GC",       "color": "#059669"},
    "4990445":  {"name": "Alex Newman",      "club": "Preserve GC",        "color": "#dc2626"},
}

# Tournament round definitions
ROUNDS = [
    {"round": 1, "date": "2026-09-04", "course_num": 10, "par": 70,
     "blue": {"rating": 74.1, "slope": 142}, "white": {"rating": 71.5, "slope": 137}},
    {"round": 2, "date": "2026-09-05", "course_num": 4,  "par": 72,
     "blue": {"rating": 73.7, "slope": 135}, "white": {"rating": 70.8, "slope": 131}},
    {"round": 3, "date": "2026-09-05", "course_num": 2,  "par": 72,
     "blue": {"rating": 75.4, "slope": 143}, "white": {"rating": 72.0, "slope": 139}},
    {"round": 4, "date": "2026-09-06", "course_num": 8,  "par": 72,
     "blue": {"rating": 72.9, "slope": 131}, "white": {"rating": 70.5, "slope": 127}},
]

def course_handicap(hi, slope, rating, par):
    """USGA 2020 formula, rounded to nearest integer."""
    return round(hi * (slope / 113) + (rating - par))

def match_course(name, num):
    """Check if a GHIN course name matches a Pinehurst course number."""
    n = name.lower()
    targets = [f"no. {num}", f"no.{num}", f"no {num}", f"#{num}",
               f"pinehurst {num}", f"course {num}", f"number {num}"]
    return any(t in n for t in targets)

def fetch_tournament_scores(ghin, hdrs):
    """Fetch scores for tournament dates from GHIN."""
    # Fetch all scores from Aug 2026 onwards to catch tournament rounds
    r = S.get(f"{BASE}/scores/search.json", headers=hdrs, params={
        "golfer_id": ghin, "per_page": 200, "page": 1,
        "from_date_played": "2026-08-01", "status": "Posted",
    })
    if r.status_code != 200:
        return {}

    all_scores = r.json().get("Scores", [])
    result = {}

    for rnd in ROUNDS:
        rnum = rnd["round"]
        date_scores = [s for s in all_scores if s.get("played_at") == rnd["date"]]

        # Try to match by course number in course name
        matched = [s for s in date_scores if match_course(s.get("course_name", ""), rnd["course_num"])]

        # Fall back to any 18-hole score on that date if only one exists
        if not matched and len(date_scores) == 1 and date_scores[0].get("number_of_holes") == 18:
            matched = date_scores

        if matched:
            s = matched[0]
            gross = s.get("adjusted_gross_score")
            hi = float(s.get("handicap_index", 0) or 0)
            slope = float(s.get("slope_rating") or rnd["blue"]["slope"])
            rating = float(s.get("course_rating") or rnd["blue"]["rating"])
            par = rnd["par"]
            ch = course_handicap(hi, slope, rating, par)
            net = gross - ch if gross else None
            result[rnum] = {
                "gross": gross,
                "net": net,
                "course_handicap": ch,
                "hi": hi,
                "course": s.get("course_name", ""),
                "tee": s.get("tee_name", ""),
                "slope": slope,
                "rating": rating,
            }

    return result

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
    result = []
    for s in scores[:20]:
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
        tourney = fetch_tournament_scores(ghin, hdrs)
        data[ghin] = {
            "name": meta["name"],
            "club": meta["club"],
            "color": meta["color"],
            "current": info["current"] or (str(revs[-1]["hi"]) if revs else ""),
            "low": info["low"],
            "revs": revs,
            "rounds": rounds,
            "tourney": tourney,
        }
        played = list(tourney.keys())
        print(f"  {len(revs)} revisions, {len(rounds)} rounds, HI={data[ghin]['current']}, tourney rounds: {played or 'none yet'}")

    with open("/Users/nathan.lee/pinehurst/ghin_data.json", "w") as f:
        json.dump(data, f, indent=2)
    print("\nSaved to ghin_data.json")

if __name__ == "__main__":
    main()
