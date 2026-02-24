## Context

Personal utility script for cleaning kids-targeted videos from a YouTube watch history. The YouTube Data API v3 represents watch history as a special playlist (playlist ID prefixed with `HL`). Videos can be removed from it by deleting the playlist item. The tooling runs inside an LXC Alpine container without a browser, and is scheduled periodically (e.g., cron).

## Goals / Non-Goals

**Goals:**
- Authenticate via OAuth 2.0 Device Flow (headless-friendly — no browser required on the container)
- Cache the OAuth token locally so the auth script only needs to be run once
- Page through a configurable window of recent watch history (`--since` flag) and identify kids-targeted videos
- Delete those playlist items from the history
- Provide a `--dry-run` mode that prints what would be removed without deleting
- Three separate scripts: auth token acquisition, history cleanup, and token revocation
- Pin all dependencies in `requirements.txt`

**Non-Goals:**
- Not a web app or daemon — no server, no UI
- Not managing multiple Google accounts
- Not blocking future kids videos in real-time
- Not restoring deleted history items
- No video category-based detection — `madeForKids` flag only

## Decisions

### 1. OAuth 2.0 Device Flow for headless auth

The watch history playlist requires user-scoped OAuth. Since the container has no browser, we use the Device Authorization Grant (RFC 8628): the auth script prints a short URL and a user code to the terminal. The user opens the URL on any device, enters the code, and approves access. The token is then saved to `token.json` on the container. Subsequent runs by the cleanup script load and auto-refresh the token silently.

**Alternatives considered:**
- OOB (out-of-band) flow: deprecated by Google in 2022, not viable.
- Copying `token.json` from another machine: works but requires running a browser-based flow elsewhere first. Device flow is cleaner and self-contained.

### 2. Three-script structure

- `auth.py`: runs the device flow, saves `token.json`. Only needs to be run once (or after revocation).
- `clean_history.py`: loads `token.json`, scans the history window defined by `--since`, removes kids videos.
- `revoke.py`: calls Google's revocation endpoint (`https://oauth2.googleapis.com/revoke`) to invalidate the token server-side, then deletes the local `token.json`. One-command clean revocation.

The scheduled cron job only calls `clean_history.py`. Auth and revocation are manual one-time actions.

### 3. Kids detection: `madeForKids` flag only

The YouTube API returns a `madeForKids` boolean on each video's `status` resource, fetched in the same API call as the snippet (no extra quota cost). This is the most reliable signal — set by YouTube/creator to comply with COPPA. No category-based detection.

### 4. `--since` flag for history window

Rather than scanning the full history on every run, `--since` accepts a duration string (e.g., `1h`, `3h`, `12h`, `1d`). The script filters playlist items by `publishedAt` timestamp, only processing videos added to history within that window. This keeps each run fast and quota-efficient, and lets the cron schedule and the flag match up (e.g., run every hour with `--since 1h`).

### 5. Quota

Each `playlistItems.list` page costs 1 unit. Each `playlistItems.delete` costs 50 units. With an expected removal count of 1–30 videos per run and a few pages of history to scan, typical runs will cost well under 2,000 units against the 10,000/day default quota. No batching strategy needed.

### 6. Dependencies and `requirements.txt`

Minimal dependencies, pinned versions:
- `google-api-python-client` — YouTube Data API v3 client
- `google-auth-oauthlib` — OAuth 2.0 device flow support
- `google-auth-httplib2` — HTTP transport for the client

All pinned in `requirements.txt`. No other package structure needed.

## Risks / Trade-offs

- **Token file stored in plaintext** → Acceptable for a personal local script; token is scoped to YouTube only and can be revoked at any time via `revoke.py` or Google account settings.
- **`madeForKids` not set on all kids videos** → Some older videos may not have the flag. Acceptable miss rate for this use case.
- **History playlist not available in all regions** → The `HL` playlist may not exist for accounts in certain regions. Script exits with a clear error if the playlist is not found.
- **Device flow requires a second device to approve** → One-time setup cost; the token persists indefinitely with auto-refresh as long as the script runs regularly.
