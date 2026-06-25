# Pinehurst Handicap Refresh

Refresh all GHIN handicap data and push an updated `index.html` to GitHub Pages.

## Steps

1. Run the Python fetcher script to pull fresh handicap revisions and last-20-rounds data for all 6 golfers, using `USER` and `PASSWORD` env vars.
2. Regenerate `index.html` (and `handicap.html`) with the new data embedded.
3. `git add`, `git commit`, and `git push` so GitHub Pages updates.

## How to run

Execute this in the `/Users/nathan.lee/pinehurst` directory:

```bash
USER=nathanmlee22@gmail.com PASSWORD=10Deerwood python3 fetch_ghin.py && python3 build_page.py && git add index.html handicap.html && git commit -m "Refresh GHIN data $(date +%Y-%m-%d)" && git push
```

If `USER`/`PASSWORD` are already exported in the shell, just:

```bash
python3 fetch_ghin.py && python3 build_page.py && git add index.html handicap.html && git commit -m "Refresh GHIN data $(date +%Y-%m-%d)" && git push
```

The live page updates at https://nathanmjlee22.github.io/pinehurst/ within ~60 seconds of the push.
