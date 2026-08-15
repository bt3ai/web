#!/usr/bin/env python3

import os
import sys
import time
import json
import requests

# ============================================================
# TASTYTRADE OAUTH2 CONFIGURATION
# ============================================================

CLIENT_ID = os.environ.get("TASTYTRADE_CLIENT_ID")
CLIENT_SECRET = os.environ.get("TASTYTRADE_CLIENT_SECRET")

# Put the OAuth2 authorization/token URLs supplied by
# Tastytrade for your Personal OAuth2 App here.
AUTHORIZATION_URL = os.environ.get("TASTYTRADE_AUTHORIZATION_URL")
TOKEN_URL = os.environ.get("TASTYTRADE_TOKEN_URL")

# This must exactly match the redirect URI configured
# in your Tastytrade OAuth2 application.
REDIRECT_URI = os.environ.get("TASTYTRADE_REDIRECT_URI")

# API
API_BASE = "https://api.tastyworks.com"

USER_AGENT = "SchwabPortfolio/1.0"


def check_config():
    required = {
        "TASTYTRADE_CLIENT_ID": CLIENT_ID,
        "TASTYTRADE_CLIENT_SECRET": CLIENT_SECRET,
        "TASTYTRADE_AUTHORIZATION_URL": AUTHORIZATION_URL,
        "TASTYTRADE_TOKEN_URL": TOKEN_URL,
        "TASTYTRADE_REDIRECT_URI": REDIRECT_URI,
    }

    missing = [name for name, value in required.items() if not value]

    if missing:
        print("Missing environment variables:")
        for name in missing:
            print(f"  {name}")
        sys.exit(1)


def exchange_code_for_token(code):
    """
    Exchange the OAuth2 authorization code for an access token.
    """

    data = {
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": REDIRECT_URI,
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
    }

    headers = {
        "Accept": "application/json",
        "Content-Type": "application/x-www-form-urlencoded",
        "User-Agent": USER_AGENT,
    }

    response = requests.post(
        TOKEN_URL,
        data=data,
        headers=headers,
        timeout=30,
    )

    print("TOKEN STATUS:", response.status_code)

    if response.status_code != 200:
        print(response.text)
        raise RuntimeError(
            f"OAuth token request failed: {response.status_code}"
        )

    token_data = response.json()

    if "access_token" not in token_data:
        print(json.dumps(token_data, indent=2))
        raise RuntimeError("No access_token returned")

    return token_data


def get_accounts(access_token):
    """
    Test the access token by retrieving the user's accounts.
    """

    headers = {
        "Authorization": f"Bearer {access_token}",
        "Accept": "application/json",
        "User-Agent": USER_AGENT,
    }

    url = f"{API_BASE}/customers/me/accounts"

    response = requests.get(
        url,
        headers=headers,
        timeout=30,
    )

    print("ACCOUNT STATUS:", response.status_code)

    if response.status_code != 200:
        print(response.text)
        raise RuntimeError(
            f"Account request failed: {response.status_code}"
        )

    return response.json()


def save_token(token_data):
    """
    Save token information locally.

    Protect this file because it contains credentials.
    """

    token_file = os.path.expanduser(
        "/home/ubuntu/.tastytrade_tokens.json"
    )

    with open(token_file, "w") as f:
        json.dump(token_data, f, indent=2)

    os.chmod(token_file, 0o600)

    print(f"Token saved to {token_file}")


def main():

    check_config()

    print("=" * 70)
    print("TASTYTRADE OAUTH2 LOGIN")
    print("=" * 70)

    print()
    print("Client ID:", CLIENT_ID)
    print("Redirect URI:", REDIRECT_URI)
    print()

    # --------------------------------------------------------
    # OAuth authorization
    # --------------------------------------------------------

    print("Open this URL in your browser:")
    print()
    print(
        f"{AUTHORIZATION_URL}"
        f"?response_type=code"
        f"&client_id={CLIENT_ID}"
        f"&redirect_uri={REDIRECT_URI}"
    )

    print()
    print("After approving the application, Tastytrade will")
    print("redirect you to your configured redirect URI.")
    print()

    code = input("Paste the authorization CODE here: ").strip()

    if not code:
        raise RuntimeError("No authorization code supplied")

    # --------------------------------------------------------
    # Exchange authorization code for access token
    # --------------------------------------------------------

    token_data = exchange_code_for_token(code)

    access_token = token_data["access_token"]

    print()
    print("OAuth2 authentication successful.")

    if "expires_in" in token_data:
        print("Access token expires in:",
              token_data["expires_in"], "seconds")

    # --------------------------------------------------------
    # Test API
    # --------------------------------------------------------

    accounts = get_accounts(access_token)

    print()
    print("Tastytrade account request successful.")
    print()

    print(json.dumps(accounts, indent=2))

    # --------------------------------------------------------
    # Save token
    # --------------------------------------------------------

    save_token(token_data)


if __name__ == "__main__":
    main()
