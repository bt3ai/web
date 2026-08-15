import os
import sys
import getpass
import requests
from decimal import Decimal
from tastytrade import Session
from tastytrade import Account
# ============================================================
# CONFIGURATION
# ============================================================

BASE_URL = "https://api.tastyworks.com"

# IMPORTANT:
# False = only perform dry-run validation
# True  = actually submit the order
LIVE_TRADING = False

# Example order
SYMBOL = "SPY"

# BUY or SELL
ACTION = "Buy"

# Number of shares
QUANTITY = 1

# Order type:
# Limit or Market
ORDER_TYPE = "Limit"

# Only used for Limit orders
LIMIT_PRICE = "600.00"

# Day or GTC
TIME_IN_FORCE = "Day"

# API version recommended by current tastytrade docs
ACCEPT_VERSION = "20260427"

# ============================================================
# USER AGENT
# tastytrade requires a User-Agent in product/version format
# ============================================================

HEADERS_BASE = {
    "Content-Type": "application/json",
    "Accept": "application/json",
    "User-Agent": "DaoyiTrading/1.0"
}


# ============================================================
# LOGIN
# ============================================================

def login(username, password):

    url = f"{BASE_URL}/sessions"

    payload = {
        "login": "ttbpcorp11",
        "password": "Shaowandouying8#",
        "remember-me": True
    }

    headers = HEADERS_BASE.copy()

    response = requests.post(
        url,
        json=payload,
        headers=headers,
        timeout=30
    )

    print("LOGIN STATUS:", response.status_code)

    if response.status_code != 201 and response.status_code != 200:
        print("Login failed:")
        print(response.text)
        sys.exit(1)

    data = response.json()["data"]

    session_token = data["session-token"]

    print("Login successful.")

    return session_token


# ============================================================
# API SESSION
# ============================================================

def api_headers(session_token):

    headers = HEADERS_BASE.copy()

    headers["Authorization"] = session_token

    # Current order API version
    headers["Accept-Version"] = ACCEPT_VERSION

    return headers


# ============================================================
# GET ACCOUNTS
# ============================================================

def get_accounts(session_token):

    url = f"{BASE_URL}/customers/me/accounts"

    response = requests.get(
        url,
        headers=api_headers(session_token),
        timeout=30
    )

    print("ACCOUNT STATUS:", response.status_code)

    if response.status_code != 200:
        print(response.text)
        sys.exit(1)

    return response.json()["data"]["items"]


# ============================================================
# DISPLAY ACCOUNTS
# ============================================================

def display_accounts(accounts):

    print("\nAvailable accounts:")
    print("-" * 70)

    for i, item in enumerate(accounts):

        #account = item["account"]
        account = item

        account_number = account.get("account-number")
        nickname = account.get("nickname")
        account_type = account.get("account-type-name")

        authority = item.get("authority-level")

        print(
            f"[{i}] "
            f"{account_number} | "
            f"{nickname} | "
            f"{account_type} | "
            f"authority={authority}"
        )

    print("-" * 70)


# ============================================================
# GET BALANCE
# ============================================================

def get_balance(session_token, account_number):

    url = (
        f"{BASE_URL}/accounts/"
        f"{account_number}/balances"
    )

    response = requests.get(
        url,
        headers=api_headers(session_token),
        timeout=30
    )

    if response.status_code != 200:
        print("Balance request failed:")
        print(response.text)
        return None

    return response.json()["data"]


# ============================================================
# GET POSITIONS
# ============================================================

def get_positions(session_token, account_number):

    url = (
        f"{BASE_URL}/accounts/"
        f"{account_number}/positions"
    )

    response = requests.get(
        url,
        headers=api_headers(session_token),
        timeout=30
    )

    if response.status_code != 200:
        print("Positions request failed:")
        print(response.text)
        return []

    return response.json()["data"]["items"]


# ============================================================
# CREATE ORDER
# ============================================================

def create_order():

    # Order leg
    leg = {
        "instrument-type": "Equity",
        "symbol": SYMBOL,
        "quantity": QUANTITY,
        "action": ACTION
    }

    order = {
        "order-type": ORDER_TYPE,
        "time-in-force": TIME_IN_FORCE,
        "order-leg": [
            leg
        ],
        "price": LIMIT_PRICE if ORDER_TYPE == "Limit" else None
    }

    # Remove price for market orders
    if ORDER_TYPE == "Market":
        order.pop("price", None)

    return order


# ============================================================
# DRY RUN
# ============================================================

def dry_run_order(
    session_token,
    account_number,
    order
):

    url = (
        f"{BASE_URL}/accounts/"
        f"{account_number}/orders/dry-run"
    )

    response = requests.post(
        url,
        json=order,
        headers=api_headers(session_token),
        timeout=30
    )

    print("\nDRY RUN STATUS:", response.status_code)

    print(response.text)

    return response


# ============================================================
# SUBMIT LIVE ORDER
# ============================================================

def submit_order(
    session_token,
    account_number,
    order
):

    url = (
        f"{BASE_URL}/accounts/"
        f"{account_number}/orders"
    )

    response = requests.post(
        url,
        json=order,
        headers=api_headers(session_token),
        timeout=30
    )

    print("\nLIVE ORDER STATUS:", response.status_code)

    print(response.text)

    return response


# ============================================================
# MAIN
# ============================================================

async def main():

    print("=" * 70)
    print("TASTYTRADE ORDER TEST")
    print("=" * 70)

    print("\nEnvironment:")
    print(BASE_URL)

    if LIVE_TRADING:
        print("\n*** LIVE TRADING ENABLED ***")
    else:
        print("\n*** DRY RUN ONLY ***")

    # --------------------------------------------------------
    # Credentials
    # --------------------------------------------------------

    username = "ttbpcorp11"
    #os.getenv("TASTYTRADE_USERNAME")

    if not username:
        username = input("Tastytrade username/email: ")

    password = "Shaowandouying8#"
    #os.getenv("TASTYTRADE_PASSWORD")

    if not password:
        password = getpass.getpass(
            "Tastytrade password: "
        )

    # --------------------------------------------------------
    # Login
    # --------------------------------------------------------


    session = Session('3a89f78a5597ef4365c90f2ed7596ac910e520c0', 'eyJhbGciOiJFZERTQSIsInR5cCI6InJ0K2p3dCIsImtpZCI6IkdSV0RSRlZVNHB5cmE4OTByZnRQN1pXVklMUmlpNFoxQkJQaTV2RzIzeGciLCJqa3UiOiJodHRwczovL2FwaS50YXN0eXRyYWRlLmNvbS9vYXV0aC9qd2tzIn0.eyJpc3MiOiJodHRwczovL2FwaS50YXN0eXRyYWRlLmNvbSIsInN1YiI6IlUwZmJkN2I0OC03ZDFjLTQ2ZGYtODQ0NC1jNDk2YTQ4MGI3ODciLCJpYXQiOjE3ODYyNzk4ODIsImF1ZCI6ImFmNzEzMWQ3LTI4NTItNDYzNi1iODBhLTQ5ZGI0MWEwYTVmZCIsImdyYW50X2lkIjoiRzg0MmE0MWI4LWNlN2UtNDBhNi04ZWIzLTExZGZjYWFiNGIyMCIsInNjb3BlIjoicmVhZCB0cmFkZSBvcGVuaWQifQ.Szv7-0HTuabeA1JNSjHzwCzF-snBejSSHyY2BK6FB8dsCxT45lBtIbb57piyyLw6dykl8boDftLKRKeO7Z3ADg')
    # --------------------------------------------------------
    # Get accounts
    # --------------------------------------------------------
    #accounts = await Account.get(session)
    account = await Account.get(session, "5WI95487")

    balance = await account.get_balances(session)

    print("\nACCOUNT BALANCE:")
    print(balance)

    # --------------------------------------------------------
    # Positions
    # --------------------------------------------------------

    positions = await account.get_positions(session)

    print("\nPOSITIONS:")

    if not positions:
        print("No positions.")

    else:

        for position in positions:

            print(
                position.symbol,
                position.quantity,
                position.quantity_direction
            )

    # --------------------------------------------------------
    # Create order
    # --------------------------------------------------------

    order = create_order()

    print("\nORDER TO TEST:")
    print(order)

    # --------------------------------------------------------
    # ALWAYS DRY RUN FIRST
    # --------------------------------------------------------

    dry_response = dry_run_order(
        token,
        account_number,
        order
    )

    if not dry_response.ok:

        print(
            "\nDry run rejected the order."
        )

        sys.exit(1)

    print("\nDry run succeeded.")

    # --------------------------------------------------------
    # LIVE TRADING CHECK
    # --------------------------------------------------------

    if not LIVE_TRADING:

        print(
            "\nLIVE_TRADING=False"
        )

        print(
            "No real order was submitted."
        )

        return

    # --------------------------------------------------------
    # Extra confirmation
    # --------------------------------------------------------

    print("\n" + "!" * 70)
    print("WARNING: YOU ARE ABOUT TO SUBMIT A REAL ORDER")
    print("!" * 70)

    print(f"Account:   {account_number}")
    print(f"Symbol:    {SYMBOL}")
    print(f"Action:    {ACTION}")
    print(f"Quantity:  {QUANTITY}")
    print(f"Type:      {ORDER_TYPE}")

    if ORDER_TYPE == "Limit":
        print(f"Limit:     {LIMIT_PRICE}")

    confirmation = input(
        "\nType SUBMIT to send the real order: "
    )

    if confirmation != "SUBMIT":

        print(
            "Order cancelled."
        )

        return

    # --------------------------------------------------------
    # Submit
    # --------------------------------------------------------

    submit_order(
        token,
        account_number,
        order
    )


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
    #main()
