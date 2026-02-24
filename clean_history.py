#!/usr/bin/env python3
"""
clean_history.py — Remove kids-targeted videos from YouTube watch history.

Scans the watch history for the time window specified by --since and removes
any videos flagged as madeForKids. Requires token.json (run auth.py first).

Usage:
  python clean_history.py --since 2h
  python clean_history.py --since 1d --dry-run
"""

import argparse
import json
import os
import re
import sys
from datetime import datetime, timedelta, timezone

from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

TOKEN_FILE = "token.json"
SCOPES = ["https://www.googleapis.com/auth/youtube.force-ssl"]


def parse_since(since_str):
    """Parse a duration string (e.g. '1h', '3h', '12h', '1d') into a timedelta."""
    match = re.fullmatch(r"(\d+)(h|d)", since_str.strip())
    if not match:
        print(f"Error: Invalid --since value {since_str!r}.")
        print("Accepted format: a number followed by 'h' (hours) or 'd' (days).")
        print("Examples: 1h, 3h, 12h, 1d")
        sys.exit(1)
    value, unit = int(match.group(1)), match.group(2)
    return timedelta(hours=value) if unit == "h" else timedelta(days=value)


def load_credentials():
    """Load credentials from token.json, refreshing if expired."""
    if not os.path.exists(TOKEN_FILE):
        print(f"Error: {TOKEN_FILE} not found.")
        print("Run auth.py first to authenticate.")
        sys.exit(1)

    creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)

    if creds.expired and creds.refresh_token:
        creds.refresh(Request())
        # Persist the refreshed token
        with open(TOKEN_FILE, "w") as f:
            f.write(creds.to_json())

    return creds


def get_watch_history_playlist_id(youtube):
    """Retrieve the watch history playlist ID for the authenticated user."""
    resp = youtube.channels().list(
        part="contentDetails",
        mine=True,
        maxResults=1,
    ).execute()

    items = resp.get("items", [])
    if not items:
        print("Error: Could not retrieve channel info.")
        sys.exit(1)

    playlist_id = (
        items[0]
        .get("contentDetails", {})
        .get("relatedPlaylists", {})
        .get("watchHistory")
    )

    if not playlist_id:
        print("Error: Watch history playlist not found.")
        print("Your account may not support this feature in your region.")
        sys.exit(1)

    return playlist_id


def fetch_history_items(youtube, playlist_id, cutoff):
    """
    Fetch playlist items from watch history within the time window.
    Stops paginating once all items on a page are older than the cutoff.
    """
    items = []
    next_page_token = None

    while True:
        kwargs = {
            "playlistId": playlist_id,
            "part": "snippet",
            "maxResults": 50,
        }
        if next_page_token:
            kwargs["pageToken"] = next_page_token

        resp = youtube.playlistItems().list(**kwargs).execute()
        page_items = resp.get("items", [])

        all_old = True
        for item in page_items:
            published_at_str = item["snippet"]["publishedAt"]
            published_at = datetime.fromisoformat(
                published_at_str.replace("Z", "+00:00")
            )
            if published_at >= cutoff:
                all_old = False
                items.append(item)

        next_page_token = resp.get("nextPageToken")
        # Stop if no more pages or the whole page was beyond the window
        if not next_page_token or all_old:
            break

    return items


def get_kids_video_ids(youtube, items):
    """
    Return a set of video IDs where madeForKids is True.
    Batches video IDs in groups of 50 to minimise API calls.

    Note: playlistItems.list does not expose the video-level madeForKids flag;
    a separate videos.list call is required.
    """
    if not items:
        return set()

    video_ids = [item["snippet"]["resourceId"]["videoId"] for item in items]
    kids_ids = set()

    for i in range(0, len(video_ids), 50):
        batch = video_ids[i : i + 50]
        resp = youtube.videos().list(
            part="status",
            id=",".join(batch),
            maxResults=50,
        ).execute()
        for video in resp.get("items", []):
            if video.get("status", {}).get("madeForKids"):
                kids_ids.add(video["id"])

    return kids_ids


def main():
    parser = argparse.ArgumentParser(
        description="Remove kids-targeted videos from YouTube watch history."
    )
    parser.add_argument(
        "--since",
        required=True,
        metavar="DURATION",
        help="Time window to scan, e.g. 1h, 3h, 12h, 1d",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print what would be removed without making any changes",
    )
    args = parser.parse_args()

    delta = parse_since(args.since)
    cutoff = datetime.now(timezone.utc) - delta

    creds = load_credentials()
    youtube = build("youtube", "v3", credentials=creds)

    playlist_id = get_watch_history_playlist_id(youtube)
    items = fetch_history_items(youtube, playlist_id, cutoff)
    kids_ids = get_kids_video_ids(youtube, items)

    to_remove = [
        item for item in items
        if item["snippet"]["resourceId"]["videoId"] in kids_ids
    ]

    scanned = len(items)
    found = len(to_remove)

    if args.dry_run:
        if to_remove:
            print(f"[dry-run] Would remove {found} kids video(s):")
            for item in to_remove:
                title = item["snippet"]["title"]
                video_id = item["snippet"]["resourceId"]["videoId"]
                print(f"  - {title}  (https://youtu.be/{video_id})")
        print(f"\nScanned {scanned} items. Found {found} kids videos. Nothing removed (dry-run).")
        return

    removed = 0
    for item in to_remove:
        try:
            youtube.playlistItems().delete(id=item["id"]).execute()
            removed += 1
        except HttpError as e:
            title = item["snippet"]["title"]
            print(f"Warning: Failed to remove '{title}': {e}")

    if removed:
        print(f"Scanned {scanned} items. Found {found} kids videos. Removed {removed}.")
    else:
        print(f"Scanned {scanned} items. Found 0 kids videos. Nothing removed.")


if __name__ == "__main__":
    main()
