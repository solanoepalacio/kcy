#!/usr/bin/env python3
"""
auth.py — Obtain and save OAuth 2.0 credentials using the device flow.

Run once to generate token.json. No browser required — works in headless
environments (LXC containers, servers, etc.).

SETUP (one-time, before first run):
  1. Go to https://console.cloud.google.com/
  2. Create a project (or select an existing one)
  3. Enable the YouTube Data API v3:
       APIs & Services → Library → search "YouTube Data API v3" → Enable
  4. Create OAuth 2.0 credentials:
       APIs & Services → Credentials → Create Credentials → OAuth client ID
       Application type: TV and Limited Input devices
       Download the JSON file and save it as client_secrets.json
       in the same directory as this script
  5. Configure the OAuth consent screen if prompted:
       Add your Google account as a test user while the app is in testing mode

Usage:
  python auth.py
"""

import json
import os
import sys
import time

import requests

TOKEN_FILE = "token.json"
CLIENT_SECRETS_FILE = "client_secrets.json"
SCOPES = ["https://www.googleapis.com/auth/youtube"]
DEVICE_CODE_URL = "https://oauth2.googleapis.com/device/code"
TOKEN_URL = "https://oauth2.googleapis.com/token"
GRANT_TYPE = "urn:ietf:params:oauth:grant-type:device_code"


def load_client_secrets():
    if not os.path.exists(CLIENT_SECRETS_FILE):
        print(f"Error: {CLIENT_SECRETS_FILE} not found.")
        print("Download OAuth 2.0 client credentials from Google Cloud Console.")
        print("See the setup instructions at the top of this file.")
        sys.exit(1)
    with open(CLIENT_SECRETS_FILE) as f:
        data = json.load(f)
    client = data.get("installed") or data.get("web")
    if not client:
        print(f"Error: Unrecognized format in {CLIENT_SECRETS_FILE}.")
        sys.exit(1)
    return client["client_id"], client["client_secret"]


def main():
    if os.path.exists(TOKEN_FILE):
        print(f"Token already exists at {TOKEN_FILE}.")
        print("Run revoke.py first if you want to re-authenticate.")
        sys.exit(0)

    client_id, client_secret = load_client_secrets()

    # Request device code
    resp = requests.post(DEVICE_CODE_URL, data={
        "client_id": client_id,
        "scope": " ".join(SCOPES),
    })
    if not resp.ok:
        error_data = resp.json()
        print(f"Error: Google rejected the credentials ({resp.status_code}).")
        print(f"  {error_data.get('error')}: {error_data.get('error_description', '')}")
        print()
        print("Make sure client_secrets.json uses an OAuth client of type")
        print("'TVs and Limited Input devices' (not Desktop app or Web application).")
        sys.exit(1)
    device_data = resp.json()

    verification_url = device_data["verification_url"]
    user_code = device_data["user_code"]
    device_code = device_data["device_code"]
    expires_in = device_data["expires_in"]
    interval = device_data.get("interval", 5)

    print()
    print("Open the following URL on any device (phone, laptop, etc.):")
    print(f"\n  {verification_url}\n")
    print(f"Then enter the code: {user_code}")
    print()
    print("Waiting for authorization", end="", flush=True)

    # Poll for token
    deadline = time.time() + expires_in
    while time.time() < deadline:
        time.sleep(interval)
        token_resp = requests.post(TOKEN_URL, data={
            "client_id": client_id,
            "client_secret": client_secret,
            "device_code": device_code,
            "grant_type": GRANT_TYPE,
        })
        token_data = token_resp.json()

        if "error" in token_data:
            error = token_data["error"]
            if error == "authorization_pending":
                print(".", end="", flush=True)
                continue
            elif error == "slow_down":
                interval += 5
                continue
            elif error == "expired_token":
                print("\nDevice code expired. Please run auth.py again.")
                sys.exit(1)
            elif error == "access_denied":
                print("\nAuthorization denied.")
                sys.exit(1)
            else:
                print(f"\nUnexpected error: {error}")
                sys.exit(1)

        # Success
        print("\nAuthorization successful!")
        credentials = {
            "client_id": client_id,
            "client_secret": client_secret,
            "token": token_data["access_token"],
            "refresh_token": token_data.get("refresh_token"),
            "token_uri": TOKEN_URL,
            "scopes": SCOPES,
        }
        with open(TOKEN_FILE, "w") as f:
            json.dump(credentials, f, indent=2)
        print(f"Token saved to {TOKEN_FILE}.")
        return

    print("\nAuthorization timed out. Please run auth.py again.")
    sys.exit(1)


if __name__ == "__main__":
    main()
