#!/usr/bin/env python3
"""
revoke.py — Revoke the OAuth 2.0 token server-side and delete token.json.

Invalidates the token on Google's servers and removes the local file.
After running this, you will need to run auth.py again to re-authenticate.

Usage:
  python revoke.py
"""

import json
import os
import sys

import requests

TOKEN_FILE = "token.json"
REVOKE_URL = "https://oauth2.googleapis.com/revoke"


def main():
    if not os.path.exists(TOKEN_FILE):
        print(f"No token found at {TOKEN_FILE}. Nothing to revoke.")
        sys.exit(0)

    with open(TOKEN_FILE) as f:
        token_data = json.load(f)

    access_token = token_data.get("token")
    if access_token:
        resp = requests.post(REVOKE_URL, params={"token": access_token})
        if resp.status_code == 200:
            print("Token successfully revoked on Google's servers.")
        else:
            print(
                f"Warning: Revocation request returned status {resp.status_code}. "
                "The token may already be expired. Proceeding to delete local file."
            )
    else:
        print("Warning: No access token found in token.json. Proceeding to delete local file.")

    os.remove(TOKEN_FILE)
    print(f"{TOKEN_FILE} deleted.")
    print("Run auth.py to re-authenticate.")


if __name__ == "__main__":
    main()
