## Why

My kids occasionally use my YouTube profile on home devices, polluting my watch history with children's content and degrading my recommendations. This script automates the cleanup so I can run it periodically without manually hunting down and removing kids videos.

## What Changes

- New standalone Python script runnable from the command line
- Authenticates with YouTube Data API v3 using OAuth 2.0
- Fetches the authenticated user's watch history
- Detects kids-targeted videos based on the `madeForKids` flag and content category signals
- Removes detected videos from watch history
- Supports a dry-run mode to preview what would be removed before committing

## Capabilities

### New Capabilities

- `youtube-auth`: OAuth 2.0 authentication flow against YouTube Data API v3, with token caching to avoid re-authenticating on every run
- `history-fetch`: Retrieve the full watch history playlist for the authenticated user, handling pagination
- `kids-detection`: Classify a video as kids-targeted based on `madeForKids` flag and video category
- `history-cleanup`: Remove flagged videos from the watch history playlist
- `cli-runner`: Entry point script with `--dry-run` flag and a summary of what was (or would be) removed

### Modified Capabilities

## Impact

- Greenfield project — no existing code
- Requires a Google Cloud project with YouTube Data API v3 enabled and OAuth 2.0 client credentials
- Runtime dependencies: `google-api-python-client`, `google-auth-oauthlib`
