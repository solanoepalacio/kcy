## 1. Project Setup

- [ ] 1.1 Create project directory with `auth.py`, `clean_history.py`, `revoke.py`, and `requirements.txt`
- [ ] 1.2 Pin dependencies in `requirements.txt`: `google-api-python-client`, `google-auth-oauthlib`, `google-auth-httplib2`
- [ ] 1.3 Set up a Google Cloud project, enable YouTube Data API v3, and create OAuth 2.0 client credentials (Desktop app type); download `client_secrets.json`

## 2. auth.py — OAuth Device Flow

- [ ] 2.1 Load `client_secrets.json` and define the `youtube.force-ssl` scope
- [ ] 2.2 Implement device flow: request device code, print verification URL and user code to stdout
- [ ] 2.3 Poll Google's token endpoint until user approves or flow times out
- [ ] 2.4 Save credentials to `token.json` on success
- [ ] 2.5 Handle the case where `token.json` already exists: print a message and exit without starting a new flow

## 3. revoke.py — Token Revocation

- [ ] 3.1 Load `token.json`; if not found, print a message and exit cleanly
- [ ] 3.2 POST to `https://oauth2.googleapis.com/revoke` with the access token
- [ ] 3.3 Print a warning (but continue) if the revocation request returns an error
- [ ] 3.4 Delete `token.json` from the local filesystem and print a confirmation message

## 4. clean_history.py — Argument Parsing

- [ ] 4.1 Add required `--since` argument accepting duration strings (`1h`, `3h`, `12h`, `1d`, etc.)
- [ ] 4.2 Parse and validate the `--since` value; exit with a clear error on unrecognized formats
- [ ] 4.3 Add optional `--dry-run` flag

## 5. clean_history.py — Authentication

- [ ] 5.1 Load `token.json`; exit with a clear error if not found, instructing user to run `auth.py`
- [ ] 5.2 Auto-refresh the access token if expired before making any API calls

## 6. clean_history.py — History Fetch

- [ ] 6.1 Retrieve the authenticated user's channel info to get the watch history playlist ID
- [ ] 6.2 Exit with a clear error message if the history playlist is not found
- [ ] 6.3 Call `playlistItems.list` with `snippet,status` parts and paginate using `nextPageToken`
- [ ] 6.4 Stop paginating when all items on a page are older than the `--since` cutoff
- [ ] 6.5 Filter returned items to only those within the `--since` time window

## 7. clean_history.py — Kids Detection and Cleanup

- [ ] 7.1 For each item in the time window, check `status.madeForKids`; flag the item if `true`
- [ ] 7.2 In dry-run mode: print the title and video ID of each flagged item; skip deletion
- [ ] 7.3 In normal mode: call `playlistItems.delete` for each flagged item using its playlist item ID
- [ ] 7.4 Print a run summary: items scanned, kids videos found, videos removed (or would-be removed)
