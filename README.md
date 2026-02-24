# YouTube Kids History Cleaner

A personal utility script that removes kids-targeted videos from your YouTube watch history. Useful when children occasionally use your YouTube profile on shared home devices, polluting your watch history and degrading recommendations.

## How it works

The script authenticates with the YouTube Data API v3 using your Google account, reads your watch history, and removes any videos flagged as `madeForKids` by YouTube/the creator. You control how far back in history to scan on each run.

Detection is based solely on the `madeForKids` flag — the same flag YouTube uses for COPPA compliance. It is the most reliable signal available and produces no false positives on adult content.

## Scripts

| Script | Purpose |
|---|---|
| `auth.py` | One-time authentication via OAuth 2.0 device flow |
| `clean_history.py` | Scans history and removes kids videos |
| `revoke.py` | Revokes access and deletes the local token |

## Setup

### 1. Google Cloud credentials (one-time)

1. Go to [console.cloud.google.com](https://console.cloud.google.com/)
2. Create a project (or select an existing one)
3. Enable the **YouTube Data API v3**:
   - APIs & Services → Library → search "YouTube Data API v3" → Enable
4. Create **OAuth 2.0 credentials**:
   - APIs & Services → Credentials → Create Credentials → OAuth client ID
   - Application type: **Desktop app**
   - Download the JSON file and save it as `client_secrets.json` in this directory
5. If your app is in testing mode, add your Google account as a test user:
   - APIs & Services → OAuth consent screen → Test users

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Authenticate (one-time)

```bash
python auth.py
```

The script prints a URL and a short code. Open the URL on any device (phone, laptop), enter the code, and approve access. The token is saved to `token.json` and reused on every subsequent run — no login required after this.

## Usage

```bash
# Remove kids videos from the last 2 hours of history
python clean_history.py --since 2h

# Preview what would be removed without deleting anything
python clean_history.py --since 24h --dry-run
```

### `--since` values

| Value | Window |
|---|---|
| `1h` | Last 1 hour |
| `3h` | Last 3 hours |
| `12h` | Last 12 hours |
| `1d` | Last 24 hours |

### Scheduling with cron

To run automatically every hour:

```bash
crontab -e
```

Add:

```
0 * * * * /usr/bin/python3 /path/to/clean_history.py --since 1h
```

## Revoking access

To invalidate the token on Google's servers and remove the local file:

```bash
python revoke.py
```

After revoking, run `auth.py` again to re-authenticate. You can also revoke access at any time from [myaccount.google.com/permissions](https://myaccount.google.com/permissions).

## Notes

- The token (`token.json`) is stored in plaintext and is scoped to YouTube only. Keep it private.
- `madeForKids` is not set on all older videos — some kids content may be missed, but there are no false removals.
- Typical runs cost well under 2,000 API quota units. The default daily quota is 10,000 units.
