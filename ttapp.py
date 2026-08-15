from flask import Flask, render_template, request, jsonify, redirect, url_for, session, flash
import os
import base64
import requests
import hashlib
import secrets
try:
    import pandas as pd
    PANDAS_AVAILABLE = True
except ImportError:
    PANDAS_AVAILABLE = False
    print("Warning: pandas not available, using fallback JSON processing")
import signal    
from dotenv import load_dotenv
from loguru import logger
from flask import Flask, jsonify
from flasgger import Swagger
import time
from datetime import timedelta
from schwab import SchwabClient
from flask_socketio import SocketIO, emit
from functools import wraps
from werkzeug.middleware.proxy_fix import ProxyFix
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.jobstores.base import JobLookupError

from flask_redis import FlaskRedis
import yfinance as yf
import pandas as pd
import numpy as np
from collections import OrderedDict
scheduler10067672=[]
scheduler10067672_0 = BackgroundScheduler()
scheduler10067672_1 = BackgroundScheduler()
scheduler10067672_2 = BackgroundScheduler()
scheduler10067672_0.start()
scheduler10067672_1.start()
scheduler10067672_2.start()
scheduler10067672.append(scheduler10067672_0)
scheduler10067672.append(scheduler10067672_1)
scheduler10067672.append(scheduler10067672_2)

scheduler26609977=[]
scheduler26609977_0 = BackgroundScheduler()
scheduler26609977_1 = BackgroundScheduler()
scheduler26609977_2 = BackgroundScheduler()
scheduler26609977_0.start()
scheduler26609977_1.start()
scheduler26609977_2.start()
scheduler26609977.append(scheduler26609977_0)
scheduler26609977.append(scheduler26609977_1)
scheduler26609977.append(scheduler26609977_2)

scheduler34614483=[]
scheduler34614483_0 = BackgroundScheduler()
scheduler34614483_1 = BackgroundScheduler()
scheduler34614483_2 = BackgroundScheduler()
scheduler34614483_0.start()
scheduler34614483_1.start()
scheduler34614483_2.start()
scheduler34614483.append(scheduler34614483_0)
scheduler34614483.append(scheduler34614483_1)
scheduler34614483.append(scheduler34614483_2)

scheduler87390906=[]
scheduler87390906_0 = BackgroundScheduler()
scheduler87390906_1 = BackgroundScheduler()
scheduler87390906_2 = BackgroundScheduler()
scheduler87390906_0.start()
scheduler87390906_1.start()
scheduler87390906_2.start()
scheduler87390906.append(scheduler87390906_0)
scheduler87390906.append(scheduler87390906_1)
scheduler87390906.append(scheduler87390906_2)

AccountSchedulerMap={}
AccountSchedulerMap["34614483"] =scheduler34614483 
AccountSchedulerMap["87390906"] =scheduler87390906 
AccountSchedulerMap["26609977"] =scheduler26609977 
AccountSchedulerMap["10067672"] =scheduler10067672 

AccountRunCounter={}
counter10067672 = [[0,100,0],[0,100,0],[0,100,0]]
counter26609977 = [[0,100,0],[0,100,0],[0,100,0]]
counter34614483 = [[0,10,0],[0,100,0],[0,100,0]]
counter87390906 = [[0,100,0],[0,100,0],[0,100,0]]
AccountRunCounter["34614483"] = counter34614483 
AccountRunCounter["87390906"] = counter87390906 
AccountRunCounter["26609977"] = counter26609977 
AccountRunCounter["10067672"] = counter10067672 

# Hashtable with Account as key and Id as value
ThreadRowNumberMap = {
    "10067672-0": 1,
    "10067672-1": 2,
    "10067672-2": 3,
    "26609977-0": 4,
    "26609977-1": 5,
    "26609977-2": 6,
    "34614483-0": 7,
    "34614483-1": 8,
    "34614483-2": 9,
    "87390906-0": 10,
    "87390906-1": 11,
    "87390906-2": 12
}

# Load environment variables
load_dotenv()
app = Flask(__name__ , static_folder="static")
# Use a consistent secret key for sessions to persist
app.secret_key = os.getenv("FLASK_SECRET_KEY", secrets.token_hex(32))
app.config['SESSION_TYPE'] = 'filesystem'
app.config['PERMANENT_SESSION_LIFETIME'] = 3600  # 1 hour
app.config['SESSION_COOKIE_SECURE'] = False  # Set to True in production with HTTPS
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'

# Environment variables
APP_KEY = os.getenv("app_key")
APP_SECRET = os.getenv("app_secret")
REDIRECT_URI = os.getenv("redirect_uri")

client = None
DEFAULT_EXPIRES_IN = 1800  # 30 min
REFRESH_MARGIN = 120      # seconds (refresh 2 min early)
CHECK_INTERVAL = 60       # scheduler checks every 60 seconds

import threading

Token_lock = threading.Lock()
Job_lock34614483 = threading.Lock()
Job_lock87390906 = threading.Lock()
Job_lock26609977 = threading.Lock()
Job_lock10067672 = threading.Lock()

AccountJob_lock_Map = {}
AccountJob_lock_Map["34614483"] =Job_lock34614483 
AccountJob_lock_Map["87390906"] =Job_lock87390906 
AccountJob_lock_Map["26609977"] =Job_lock26609977 
AccountJob_lock_Map["10067672"] =Job_lock10067672 


TokenStore = {
            "access_token": None,
            "refresh_token": None,
            "expires_at": 0  # initialize to 0 to force first refresh
            }

Refresh_scheduler = BackgroundScheduler(daemon=True)

def auto_refresh_job():
    with app.app_context():   # <-- push app context
        with Token_lock:
            remaining = TokenStore["expires_at"] - time.time()
            logger.info(f"[APScheduler] Refreshing calc expiration remain:{remaining}")
            if remaining > REFRESH_MARGIN:
                return  # still valid
            logger.info("[APScheduler] Refreshing Schwab access token...")
            refresh_token()

def start_refresh_token_scheduler():
    job_id = "schwab_token_refresh"
    existing_job = Refresh_scheduler.get_job(job_id)
    if existing_job is None:
        Refresh_scheduler.add_job(auto_refresh_job, trigger="interval",seconds=CHECK_INTERVAL,id="schwab_token_refresh",max_instances=1,coalesce=True,)
        Refresh_scheduler.start()

    logger.info("[APScheduler] Refreshing Schwab access tokeni started: start_refresh_token_scheduler()...")

# Initialize Swagger
swagger = Swagger(app)
from flask import send_from_directory

# Hard-coded username/password
USERNAME = 'admin'
PASSWORD = 'password123'
# Login required decorator
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('logged_in'):
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        if username == USERNAME and password == PASSWORD:
            session['logged_in'] = True
            # Always make session permanent → remember user
            session.permanent = True  
            return redirect(url_for('index'))
        else:
            flash('Invalid username or password', 'error')
    return render_template('login.html')

@app.route('/')
@login_required
def index():
    return render_template('index.html')

@app.route("/redoc")
def redoc():
        return send_from_directory(app.static_folder, "redoc.html")


@app.route('/logout')
def logout():
    session.clear()  # Clears the remembered session
    session.pop('logged_in', None)
    return redirect(url_for('login'))

@app.route("/callback")
@login_required
def autotrader():
    return render_template('autotrader.html')

@app.route("/api")
@login_required
def api():
    return render_template('api.html')
#@app.route("/ping", methods=["GET"])
#def ping():
#    """
#    ---
#    responses:
#      200:
#        description: Pong
#    """

#    return jsonify(message="pong")


app.config['REDIS_URL'] = "redis://localhost:6379/0"
redis_client = FlaskRedis(app)
socketio = SocketIO(cors_allowed_origins="*", async_mode= "eventlet")
socketio.init_app(app)

app.wsgi_app = ProxyFix(
    app.wsgi_app,
    x_proto=1,
    x_host=1
)
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=30)
@socketio.on('connect')
def handle_connect():
    print("Client connected!")

@socketio.on('update_message')
def handle_pdate_message(msg):
    logger.info(f"Received message: {msg}")
    emit('response', msg, broadcast = True)

@socketio.on('update_symbol')
def handle_pdate_message(msg):
    logger.info(f"Received message: {msg}")
    emit('response_symbol', msg, broadcast = True)

@socketio.on('update_status')
def handle_pdate_message(msg):
    logger.info(f"Received message: {msg}")
    emit('response_status', msg, broadcast = True)

def calculate_beta(
    tickers,
    benchmark="SPY",
    start="2023-06-01",
    end="2026-06-01"
):
    # Download Adjusted Close prices
    all_tickers = tickers + [benchmark]

    prices = yf.download(
        all_tickers,
        start=start,
        end=end,
        auto_adjust=True,
        progress=False
    )["Close"]

    # Daily returns
    returns = prices.pct_change().dropna()

    market_return = returns[benchmark]
    results = []
    try:
        for ticker in tickers:
            if ticker.upper() != "SPCX":
                stock_return = returns[ticker]

                covariance = np.cov(stock_return, market_return)[0][1]
                market_variance = np.var(market_return)

                beta = covariance / market_variance
                beta = round(float(beta), 2)
                logger.info(f"Ticker: {ticker}， Beta：{beta}")
                redis_client.set(ticker, beta)
                results.append(OrderedDict([
                    ("Ticker", ticker),
                    ("Beta", beta)
                ]))
            else:
                redis_client.set(ticker, 1.5)
                results.append(OrderedDict([
                    ("Ticker", ticker),
                    ("Beta", 1.5)
                ]))
    except Exception as e:
        logger.error(f"Error in get beta: {str(e)}")
        raise

    return pd.DataFrame(results)

@app.route("/beta", methods=["GET"])
def get_beta():

    # Option 1: comma-separated list
    tickers = request.args.get("tickers")

    if tickers:
        ticker_list = [
            ticker.strip().upper()
            for ticker in tickers.split(",")
            if ticker.strip()
        ]
    else:
        # Option 2: multiple ticker parameters
        ticker_list = [
            ticker.upper()
            for ticker in request.args.getlist("ticker")
        ]
    if not ticker_list:
        return jsonify({
            "error": "Please provide stock tickers."
        }), 400

    beta_df = calculate_beta(ticker_list)
    # convert DataFrame → JSON
    return jsonify({
        "data": beta_df.to_dict(orient="records"),
        "count": len(ticker_list)
    })


@app.route('/set_redis')
def set_redis():
    redis_client.set('my_key', 'my_value')

    return "Key 'my_key' set to 'my_value'"

@app.route('/get_redis')
def get_redis():
    value = redis_client.get('my_key')
    if value:
        return f"Value for 'my_key': {value.decode()}"
    else:
        return "Key not found"


class AccountsTrading:
    account_hash_map = None
    access_token = None
    def __init__(self, access_token):
        AccountsTrading.access_token = access_token
        self.base_url = "https://api.schwabapi.com/trader/v1"
        self.Market_BASE_URL = "https://api.schwabapi.com/marketdata/v1"
        self.headers = {"Authorization": f"Bearer {access_token}"}
        self.get_account_number_hash_value()

    def get_account_number_hash_value(self):
        if AccountsTrading.account_hash_map is None:
            response = requests.get(
                f"{self.base_url}/accounts/accountNumbers",
                headers=self.headers
            )
            response.raise_for_status()
        
            if PANDAS_AVAILABLE:
                response_frame = pd.json_normalize(response.json())
                account_map = dict(zip(
                    response_frame["accountNumber"],
                    response_frame["hashValue"]
                ))
            else:
                # Fallback without pandas
                data = response.json()
                account_map = {}
                for account in data:
                    if 'accountNumber' in account and 'hashValue' in account:
                        account_map[account['accountNumber']] = account['hashValue']

            AccountsTrading.account_hash_map = account_map
            logger.info(f"Found {len(account_map)} accounts")
        return AccountsTrading.account_hash_map


    
    def place_dip(self, account_hash_value, accountNumber, threadNumber, symbol, price, gapprice, quantity, orderType, instruction, assetType, gapinterval):
        try:
            import requests

            base_url = "https://api.schwabapi.com/trader/v1"
            account_hash = account_hash_value
            access_token = AccountsTrading.access_token
            
            url = f"{base_url}/accounts/{account_hash}/orders"
            logger.info(f"placing dip for account hash: {account_hash_value}")
            logger.info(f"placing dip for access_token: {AccountsTrading.access_token}")

            params = {
                      "orderType": orderType,
                      "price": price,
                      "session": "NORMAL",
                      "duration": "DAY",
                      "orderStrategyType": "SINGLE",
                      "orderLegCollection": [
                               {
                                  "instruction": instruction,
                                  "quantity": quantity,
                                  "instrument": {
                                              "symbol": symbol,
                                              "assetType": assetType
                                                 }
                                }
                       ]
                     }
            

            headers = {
                        "Authorization": f"Bearer {AccountsTrading.access_token}",
                            "Accept": "application/json"
                            }

            logger.info(f"placing dip for account hash: {account_hash_value[:10]},{params}")
            response = requests.post(url, headers=headers, json=params)
            if response.status_code == 201:
                order_url = response.headers.get("Location") 
                logger.info(f"response order_url:{order_url}")
                order_id  = order_url.rstrip("/").split("/")[-1]
                dipurl = f"{base_url}/accounts/{account_hash}/orders/{order_id}"
                rowNumber = ThreadRowNumberMap[accountNumber + "-" + str(threadNumber)]
                #if AccountRunCounter[accountNumber][threadNumber][2]  == 0， indicated Table has 0 symbol:
                if  AccountRunCounter[accountNumber][threadNumber][2] == 0:
                    socketio.emit('response_symbol', {'Id': rowNumber, 'Symbol': symbol}, namespace='/')
                    AccountRunCounter[accountNumber][threadNumber][2]  == 1
                # mark  == 1 indicate is first run is done

                time.sleep(3)
                
                response = requests.delete( dipurl, headers=headers)
                try:
                    if response.status_code == 200:
                        logger.info("Cancel request accepted")
                        AccountRunCounter[accountNumber][threadNumber][0] =  AccountRunCounter[accountNumber][threadNumber][0] - 1 
                        return {
                             "success": True,
                             "order_url": order_url,
                             "cancel_status":"ok" 
                        }
                    else:
                        logger.info(f"Cancel failed due to:{response.status_code}, {response.text}")
                        if response.status_code == 429:
                            rowNumber = ThreadRowNumberMap[accountNumber + "-" + str(threadNumber)]
                            socketio.emit('response_status', {'Id': rowNumber, 'Status': "Too many requests, sleep 60 seconds"}, namespace='/')
                            time.sleep(60 )
                            AccountRunCounter[accountNumber][threadNumber][0] =  AccountRunCounter[accountNumber][threadNumber][0] - 1 
                            return
                            
                    error = response.json()
                    if "Order in state FILLED cannot be canceled" not in error["message"] : 
                        AccountRunCounter[accountNumber][threadNumber][0] =  AccountRunCounter[accountNumber][threadNumber][0] - 1 
                    logger.info(f"dip place cancel order response :{response.json()}, error:{error}")

                    if gapprice != 0.0:
                        if instruction == "SELL_TO_OPEN": 
                            instruction = "BUY_TO_CLOSE"
                            price = price - gapprice
                        if instruction == "BUY_TO_OPEN": 
                            instruction = "SELL_TO_CLOSE"
                            price = price + gapprice
                        params = {
                        "orderType": orderType,
                        "price": price,
                        "session": "NORMAL",
                        "duration": "DAY",
                        "orderStrategyType": "SINGLE",
                        "orderLegCollection": [
                               {
                                  "instruction": instruction,
                                  "quantity": quantity,
                                  "instrument": {
                                              "symbol": symbol,
                                              "assetType": assetType
                                                 }
                                }
                            ]
                        }
            
                        logger.info(f"placing gap dip now for account hash: {account_hash_value[:10]},{params}")
                        time.sleep(gapinterval)
                        response = requests.post(url, headers=headers, json=params)
                        if response.status_code == 201:
                            gaporder_url = response.headers.get("Location") 
                            logger.info(f"response gap order_url:{gaporder_url}")
                            gaporder_id  = gaporder_url.rstrip("/").split("/")[-1]
                            dipgapurl = f"{base_url}/accounts/{account_hash}/orders/{gaporder_id}"
                            logger.info(f"placing gap dip succesfully for account hash: {account_hash_value[:10]},{params}")
                            time.sleep(2)
                            response = requests.delete( dipgapurl, headers=headers)
                            logger.info(f"cancel gap dip submit for account hash: {account_hash_value[:10]},{params}")
                        else:
                            error = response.json()
                            logger.info(f"dip place gap order failed, response :{response.json()}, error:{error}")
                            logger.info(f"placing gap dip failed for account hash: {account_hash_value[:10]},{params}")
                        AccountRunCounter[accountNumber][threadNumber][0] =  AccountRunCounter[accountNumber][threadNumber][0] - 1 

                        error = response.json()
                        logger.info(f"dip igap place cancel order response :{response.json()}, error:{error}")
                except ValueError:
                    error = response.text
                    logger.error(f"dip gap place cancel order response :{error}")
                return {
                        "success": True,
                        "order_url": order_url,
                        "cancel_status": error
                        }
            else:
                logger.info(f"dip place order response is not 201 :{response.json()}")
                #get rowNumber
                rowNumber = ThreadRowNumberMap[accountNumber + "-" + str(threadNumber)]
                socketio.emit('response', {'Id': rowNumber, 'QtyLeft': str(0)}, namespace='/')
                socketio.emit('response_symbol', {'Id': rowNumber, 'Symbol': "TBA"}, namespace='/')
                data = response.json()
                msg = data.get('message', '')
                socketio.emit('response_status', {'Id': rowNumber, 'Status': msg}, namespace='/')

                AccountRunCounter[accountNumber][threadNumber][0] = 0
                #if the symbol is invalid or param is wrong, we still consider has run once, set it to 1 to make the UI shows QtyLeft = 0 when job is removed
                AccountRunCounter[accountNumber][threadNumber][1] = 1 
                AccountRunCounter[accountNumber][threadNumber][2] = 0

                #self.emit_symbol(accountNumber, threadNumber, "")


            try:
                error = response.json()
            except ValueError:
                error = response.text

            return {
                "success": False,
                "status_code": response.status_code,
                "error": error
            }

            logger.info(f"response code:{response.status_code}")
            logger.info(f"placing successfully dip for account hash: {account_hash_value[:10]}...")
        except Exception as e:
            logger.error(f"Error in place_dip {str(e)}")
            raise


    def place_orders(self, account_hash_value):
        try:
            import requests

            base_url = "https://api.schwabapi.com/trader/v1"
            account_hash = account_hash_value
            access_token = AccountsTrading.access_token
            
            url = f"{base_url}/accounts/{account_hash}/orders"
            logger.info(f"placing orders for account hash: {account_hash_value}")
            logger.info(f"placing orders for access_token: {access_token}")

            params = {
                      "orderType": "LIMIT",
                      "price": "18.00",
                      "session": "NORMAL",
                      "duration": "DAY",
                      "orderStrategyType": "SINGLE",
                      "orderLegCollection": [
                               {
                                  "instruction": "BUY",
                                  "quantity": 1,
                                  "instrument": {
                                              "symbol": "AAPL",
                                              "assetType": "EQUITY"
                                                 }
                                }
                       ]
                     }


            headers = {
                        "Authorization": f"Bearer {access_token}",
                            "Accept": "application/json"
                            }

            logger.info(f"placing orders for account hash: {account_hash_value[:10]}...")
            response = requests.post(url, headers=headers, json=params)
            if response.status_code == 201:
                order_url = response.headers.get("Location") 
                logger.info(f"response order_url:{order_url}")
                return {
                    "success": True,
                    "order_url": order_url 
                }

            try:
                error = response.json()
            except ValueError:
                error = response.text

            return {
                "success": False,
                "status_code": response.status_code,
                "error": error
            }

            logger.info(f"response code:{response.status_code}")
            logger.info(f"placing successfully orders for account hash: {account_hash_value[:10]}...")
        except Exception as e:
            logger.error(f"Error in place_orders {str(e)}")
            raise


    def list_orders(self, account_hash_value):
        try:
            import requests

            base_url = "https://api.schwabapi.com/trader/v1"
            account_hash = account_hash_value
            access_token = AccountsTrading.access_token
            
            url = f"{base_url}/accounts/{account_hash}/orders"
            logger.info(f"Fetching orders for account hash: {account_hash_value}")
            logger.info(f"Fetching orders for access_token: {access_token}")

            params = {
                        "fromEnteredTime": "2025-10-01T00:00:00.000Z",
                            "toEnteredTime": "2025-12-31T00:00:00.000Z",
                            "status":"PENDING_ACTIVATION"
                                }

            headers = {
                        "Authorization": f"Bearer {access_token}",
                            "Accept": "application/json"
                            }

            logger.info(f"Fetching orders for account hash: {account_hash_value[:10]}...")
            response = requests.get(url, headers=headers, params=params)
            logger.info(f"response code:{response.status_code}")
            logger.info(f"response json:{response.json()}")
            logger.info(f"Fetching successfully orders for account hash: {account_hash_value[:10]}...")

        except Exception as e:
            logger.error(f"Error in list_orders {str(e)}")
            raise

    def enrich_option(self, option_symbol, underlyingSymbol):
        url = f"{self.Market_BASE_URL}/quotes"
        headers = {"Authorization": f"Bearer {AccountsTrading.access_token}"}

        r = requests.get(url, headers=headers, params={"symbols": option_symbol})
        data = r.json()

        q = data[option_symbol]
        quote = q.get("quote", {})

        logger.info(f"Fetched market data for {option_symbol}: {q}")
        #
        # params = {"symbols": underlyingSymbol, "fields": "fundamental"}
        # resp = requests.get(url, params=params, headers=headers)
        # resp.raise_for_status()
        # data = resp.json()
        # beta = 0
        # for symbol, info in data.items():
        #     beta = info.get('fundamental', {}).get('beta')
        #     logger.info(f"{underlyingSymbol}: beta = {beta}, info:{info}")
        beta = redis_client.get(underlyingSymbol)
        beta = float(beta)
        logger.info(f"Fetched beta for {underlyingSymbol}: {beta}")
        return {
            "beta": beta,
            "delta": quote.get("delta"),
            "gamma": quote.get("gamma"),
            "vega": quote.get("vega"),
            "iv": quote.get("volatility"),
        }


    def calc_total(self, account_hash_value):
        try:
            logger.info(f"Fetching positions for account hash: {account_hash_value[:10]}...")
            response = requests.get(
                f"{self.base_url}/accounts/{account_hash_value}?fields=positions", 
                headers=self.headers
            )
            
            if response.status_code != 200:
                logger.error(f"API request failed with status {response.status_code}: {response.text}")
                raise Exception(f"API request failed: {response.status_code}")
            
            response_data = response.json()
            logger.info(f"Response received: {response_data.keys() if isinstance(response_data, dict) else 'Not a dict'}")
            
            data = response_data.get("securitiesAccount", {}).get("positions", [])
            logger.info(f"Found {len(data)} positions")

            options = [
                pos for pos in data
                if pos.get("instrument", {}).get("assetType") == "OPTION"
                and pos.get("shortQuantity", 0) > 0
            ]
            logger.info(f"Found {len(options)} short option positions")

            uvxy = [pos for pos in options if pos["instrument"].get("underlyingSymbol") == "UVXY"]
            for p in uvxy:
                instrument = p.get("instrument", {})
                symbol = instrument.get("symbol")
                qty = p.get("longQuantity", 0) - p.get("shortQuantity", 0)
                underlying = instrument.get("underlyingSymbol")
                market_data = self.enrich_option(symbol, underlying)
                delta= market_data.get("delta", 0)
                gamma= market_data.get("gamma", 0)
                vega= market_data.get("vega", 0)
                iv = market_data.get("iv", 0)
                beta = market_data.get("beta", 0)
                logger.info(f"instrument: {instrument}, symbol: {symbol}, Qty: {qty},  delta:{delta}, gamma:{gamma}, vega:{vega}， iv:{iv}, beta:{beta}")

            other = [pos for pos in options if pos["instrument"].get("underlyingSymbol") != "UVXY"]
            for p in other:
                instrument = p.get("instrument", {})
                symbol = instrument.get("symbol")
                qty = p.get("longQuantity", 0) - p.get("shortQuantity", 0)
                underlying = instrument.get("underlyingSymbol")
                market_data = self.enrich_option(symbol, underlying)
                delta= market_data.get("delta", 0)
                gamma= market_data.get("gamma", 0)
                vega= market_data.get("vega", 0)
                iv = market_data.get("iv", 0)
                beta =  market_data.get("beta", 0)
                logger.info(f"instrument: {instrument}, symbol: {symbol}, Qty: {qty},  delta:{delta}, gamma:{gamma}, vega:{vega}， iv:{iv}, beta:{beta}")

            uvxy_total = sum(pos.get("shortQuantity", 0) for pos in uvxy)
            other_total = sum(pos.get("shortQuantity", 0) for pos in other)
            total = (500 * uvxy_total) + (200 * other_total) 
            
            logger.info(f"Calculated totals - UVXY: {uvxy_total}, Other: {other_total}, Total: {total}")
        
            return {
                "total": total,
                "uvxy_total": uvxy_total,
                "other_total": other_total,
                "uvxy_options": uvxy,
                "other_options": other
            }
        except Exception as e:
            logger.error(f"Error in calc_total: {str(e)}")
            raise


@app.route("/stopdip", methods=["POST"])
def stopdip():
    """
    Stop a dip 
    ---
    tags:
        - stop Dip Orders
    consumes:
        - application/json
    produces:
        - application/json
    parameters:
        - in: body
          name: body
          required: true
          schema:
            type: object
            required:
                - accountNumber 
            properties:
                accountNumber:
                    type: string
                    example: "34614483" 
                threadNumber:
                    type: integer
                    example: 0 

    responses:
        200:
          description: ok
    """
    payload = request.get_json()
    accountNumber = payload["accountNumber"] 
    threadNumber = payload["threadNumber"] 
    scheduler = AccountSchedulerMap[payload["accountNumber"]][payload["threadNumber"]]
    with AccountJob_lock_Map[accountNumber]:
        job = scheduler.get_job("dipbuysell")
        if not job:
            return {"status": "not running"}
        try:
            job.remove()
            rowNumber = ThreadRowNumberMap[accountNumber + "-" + str(threadNumber)]
            socketio.emit('response', {'Id': rowNumber, 'QtyLeft': "0"}, namespace='/')
            socketio.emit('response_symbol', {'Id': rowNumber, 'Symbol': "TBA"}, namespace='/')
            socketio.emit('response_status', {'Id': rowNumber, 'Status': ""}, namespace='/')
            AccountRunCounter[accountNumber][threadNumber][0] = 0
            AccountRunCounter[accountNumber][threadNumber][1] = 0
            AccountRunCounter[accountNumber][threadNumber][2] = 0

        except JobLookupError:
            pass

   

    logger.info(f"stopped AccountSchedulerMap instance:{accountNumber},{threadNumber}")
    return jsonify(status="stopped")



@app.route("/startdip", methods=["POST"])
def startdip():
    """
    Submit a dip order every certain seconds， accounts are : 34614483 10067672 26609977 87390906 
    ---
    tags:
        - Dip Orders
    consumes:
        - application/json
    produces:
        - application/json
    parameters:
        - in: body
          name: body
          required: true
          schema:
            type: object
            required:
                - symbol
                - quantity
            properties:
                accountNumber:
                    type: string
                    example: "34614483" 
                threadNumber:
                    type: integer
                    example: 0 
                maxRunNumber:
                    type: integer
                    example: 100 
                symbol:
                    type: string
                    example: QQQ   260618P00254780 
                price:
                    type: number
                    example: 3.5
                gapprice:
                    type: number
                    example: 0.0
                quantity:
                    type: integer
                    example: 1
                orderType:
                    type: string
                    example: LIMIT 
                instruction:    
                    type: string
                    example: SELL_TO_OPEN
                assetType:
                    type: string
                    example: OPTION
                interval:
                    type: integer
                    example: 6 
                gapinterval:
                    type: integer
                    example: 0 

    responses:
        201:
            description: Dip Order submitted successfully
        400:
            description: Invalid request
    """
    payload = request.get_json()
    accountNumber = payload["accountNumber"]
    threadNumber = payload["threadNumber"] 
    scheduler = AccountSchedulerMap[payload["accountNumber"]][payload["threadNumber"]]
    AccountRunCounter[accountNumber][threadNumber][1] = payload["maxRunNumber"]
    rowNumber = ThreadRowNumberMap[accountNumber + "-" + str(threadNumber)]
 
    with AccountJob_lock_Map[accountNumber]:
        if scheduler.get_job("dipbuysell"):
            socketio.emit('response_status', {'Id': rowNumber, 'Status': "already running"}, namespace='/')
            return {"status": "already running"}
        else:
            socketio.emit('response_status', {'Id': rowNumber, 'Status': ""}, namespace='/')
    scheduler.add_job( dipbuysellmarket,  "interval",seconds=payload["interval"],id="dipbuysell",max_instances=1,coalesce=True, replace_existing=True, kwargs={"accountNumber":payload["accountNumber"],"threadNumber":payload["threadNumber"], "symbol": payload["symbol"],"price":payload["price"],  "gapprice": payload["gapprice"], "quantity": payload["quantity"],"orderType": payload["orderType"],"instruction": payload["instruction"],"assetType": payload["assetType"], "gapinterval":payload["gapinterval"]})
    return jsonify(message="ok")



@app.route('/dipbuysellmarket')
def dipbuysellmarket(accountNumber, threadNumber, symbol, price, gapprice, quantity, orderType, instruction, assetType, gapinterval):
    def handler(signum, frame):
        raise TimeoutError("Job timed out")

    signal.signal(signal.SIGALRM, handler)
    signal.alarm(30)  # seconds

    with app.app_context(): 
        access_token = AccountsTrading.access_token 
        logger.info(f"dipbuysell {accountNumber}[{threadNumber}] with access_token: {access_token[:10] if access_token else 'None'}...")
    
        if not access_token:
            return jsonify({"error": "No access token found. Please authenticate first."}), 401
    
        try:
            logger.info("Creating AccountsTrading instance...")
            accounts = AccountsTrading(access_token)
            logger.info(f"AccountsTrading instance created successfully. Found {len(AccountsTrading.account_hash_map)} accounts.")
        
            if not AccountsTrading.account_hash_map:
                return jsonify({"error": "No accounts found or failed to retrieve account information"}), 400
        
            results = {}
        
            for account_number, hash_value in AccountsTrading.account_hash_map.items():
                logger.info(f"Processing account {account_number} with hash {hash_value[:10]}...")
                try:
                    results[account_number]  =  None 
                    #if account_number == "87390906":
                    if account_number == accountNumber:
                    #if account_number == "10067672":
                        logger.info(f"Successfully begin to get account detail ")
                        accounts.place_dip(hash_value, accountNumber, threadNumber, symbol, price, gapprice, quantity, orderType, instruction, assetType, gapinterval )
                        
                        AccountRunCounter[accountNumber][threadNumber][0] = AccountRunCounter[accountNumber][threadNumber][0] + 1
                        if AccountRunCounter[accountNumber][threadNumber][0] + 1 > AccountRunCounter[accountNumber][threadNumber][1]:
                            with AccountJob_lock_Map[accountNumber]:
                                job = AccountSchedulerMap[accountNumber][threadNumber].get_job("dipbuysell")
                                if job: 
                                    try:
                                        logger.info(f"Successfully remove job:{accountNumber}.{threadNumber} because {AccountRunCounter[accountNumber][threadNumber][0]} >= {AccountRunCounter[accountNumber][threadNumber][1]}")
                                        #AccountRunCounter[accountNumber][threadNumber][0] =  AccountRunCounter[accountNumber][threadNumber][0] + 1
                                        rowNumber = ThreadRowNumberMap[accountNumber + "-" + str(threadNumber)]
                                        left = AccountRunCounter[accountNumber][threadNumber][1] - AccountRunCounter[accountNumber][threadNumber][0]
                                        socketio.emit('response', {'Id': rowNumber, 'QtyLeft': str(left)}, namespace='/')
                                        socketio.emit('response_symbol', {'Id': rowNumber, 'Symbol': "TBA"}, namespace='/')
                                        socketio.emit('response_status', {'Id': rowNumber, 'Status': ""}, namespace='/')

                                     #  AccountsTrading.emit_symbol(accountNumber, threadNumber, "")
                                        AccountRunCounter[accountNumber][threadNumber][0] = 0
                                        AccountRunCounter[accountNumber][threadNumber][1] = 0
                                        AccountRunCounter[accountNumber][threadNumber][2] = 0
                                        job.remove()
                                    except JobLookupError:
                                        pass
                        else:
                            job = AccountSchedulerMap[accountNumber][threadNumber].get_job("dipbuysell")
                            rowNumber = ThreadRowNumberMap[accountNumber + "-" + str(threadNumber)]
                            if job:
                                left = AccountRunCounter[accountNumber][threadNumber][1] - AccountRunCounter[accountNumber][threadNumber][0]
                                socketio.emit('response', {'Id': rowNumber, 'QtyLeft': str(left)}, namespace='/')
                                logger.info(f"Successfully run place_dip : {left} times ")
                            else:                         
                                AccountRunCounter[accountNumber][threadNumber][0] = 0
                                AccountRunCounter[accountNumber][threadNumber][1] = 0
                                AccountRunCounter[accountNumber][threadNumber][2] = 0
                                socketio.emit('response_symbol', {'Id': rowNumber, 'Symbol': "TBA"}, namespace='/')
                                socketio.emit('response_status', {'Id': rowNumber, 'Status': ""}, namespace='/')
                except Exception as e:
                    logger.error(f"Error dip for account {account_number}: {str(e)}")
                    results[account_number] = {"error": str(e)}
        
            logger.info(f"dip completed. Results: {results}")
            return jsonify(results)
        
        except Exception as e:
            logger.error(f"dip error: {str(e)}")
            import traceback
            logger.error(f"Full traceback: {traceback.format_exc()}")
            return jsonify({"error": str(e)}), 400
        finally:
            signal.alarm(0)


def generate_code_verifier():
    return base64.urlsafe_b64encode(secrets.token_bytes(32)).decode("utf-8").rstrip("=")

def generate_code_challenge(verifier):
    digest = hashlib.sha256(verifier.encode("utf-8")).digest()
    return base64.urlsafe_b64encode(digest).decode("utf-8").rstrip("=")

def construct_init_auth_url():
    code_verifier = generate_code_verifier()
    code_challenge = generate_code_challenge(code_verifier)
    
    auth_url = (
        "https://api.schwabapi.com/v1/oauth/authorize"
        f"?client_id={APP_KEY}"
        f"&redirect_uri={REDIRECT_URI}"
        f"&response_type=code"
        f"&scope=readonly"
        f"&code_challenge={code_challenge}"
        f"&code_challenge_method=S256"
    )
    
    return auth_url, code_verifier

def construct_headers_and_payload(returned_url, code_verifier):
    # Extract the authorization code from the returned URL
    if 'code=' in returned_url:
        code_start = returned_url.index('code=') + 5
        code_end = returned_url.find('&', code_start)
        if code_end == -1:
            code_end = len(returned_url)
        response_code = returned_url[code_start:code_end]
        
        # Clean up the authorization code - remove any URL encoding and ensure proper length
        import urllib.parse
        response_code = urllib.parse.unquote(response_code)
        
        # Remove any trailing characters that might cause issues
        response_code = response_code.strip()
        
        # Log the extracted code for debugging
        logger.info(f"Extracted authorization code: {response_code[:20]}... (length: {len(response_code)})")
        
        # Validate the code length
        if len(response_code) % 4 != 0:
            logger.warning(f"Authorization code length {len(response_code)} is not a multiple of 4")
            # Try to pad it if needed
            padding_needed = 4 - (len(response_code) % 4)
            response_code += "=" * padding_needed
            logger.info(f"Padded code to length {len(response_code)}")
    else:
        raise ValueError("No authorization code found in URL")

    # Use the same approach as j.ipynb - get refresh token first
    credentials = f"{APP_KEY}:{APP_SECRET}"
    base64_credentials = base64.b64encode(credentials.encode("utf-8")).decode("utf-8")

    headers = {
        "Authorization": f"Basic {base64_credentials}",
        "Content-Type": "application/x-www-form-urlencoded",
    }

    # First get the initial tokens
    initial_payload = {
        "grant_type": "authorization_code",
        "code": response_code,
        "redirect_uri": REDIRECT_URI,
        "code_verifier": code_verifier
    }

    return headers, initial_payload

def retrieve_tokens(headers, payload):
    response = requests.post(
        url="https://api.schwabapi.com/v1/oauth/token",
        headers=headers,
        data=payload,
    )
    
    if response.status_code != 200:
        raise Exception(f"Token request failed: {response.text}")
    
    return response.json()

def refresh_token_method(client_id, client_secret, refresh_token):
    """Same method as used in j.ipynb"""
    url = "https://api.schwabapi.com/v1/oauth/token"
    
    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
        "Authorization": "Basic " + base64.b64encode(f"{client_id}:{client_secret}".encode()).decode()
    }

    data = {
        "grant_type": "refresh_token",
        "refresh_token": refresh_token
    }

    response = requests.post(url, headers=headers, data=data)
    response.raise_for_status()  # raise exception if HTTP error
    token_data = response.json()
    return token_data["access_token"]


@app.route('/debug_session')
def debug_session():
    """Debug endpoint to check session contents"""
    session_data = {
        'has_code_verifier': 'code_verifier' in session,
        'has_access_token': 'access_token' in session,
        'has_refresh_token': 'refresh_token' in session,
        'session_keys': list(session.keys()),
        'code_verifier_length': len(session.get('code_verifier', '')) if session.get('code_verifier') else 0,
        'access_token_length': len(session.get('access_token', '')) if session.get('access_token') else 0,
        'refresh_token_length': len(session.get('refresh_token', '')) if session.get('refresh_token') else 0
    }
    return jsonify(session_data)

@app.route('/test_url_parsing', methods=['POST'])
def test_url_parsing():
    """Test endpoint to debug URL parsing"""
    try:
        returned_url = request.form['returned_url']
        
        # Extract the authorization code from the returned URL
        if 'code=' in returned_url:
            code_start = returned_url.index('code=') + 5
            code_end = returned_url.find('&', code_start)
            if code_end == -1:
                code_end = len(returned_url)
            response_code = returned_url[code_start:code_end]
            
            # Clean up the authorization code
            import urllib.parse
            response_code = urllib.parse.unquote(response_code)
            response_code = response_code.strip()
            
            return jsonify({
                "original_url": returned_url,
                "extracted_code": response_code,
                "code_length": len(response_code),
                "is_multiple_of_4": len(response_code) % 4 == 0,
                "code_start": code_start,
                "code_end": code_end
            })
        else:
            return jsonify({"error": "No authorization code found in URL"})
            
    except Exception as e:
        return jsonify({"error": str(e)})

@app.route('/auth')
def auth():
    auth_url, code_verifier = construct_init_auth_url()
    # Store code_verifier in session for later use
    session['code_verifier'] = code_verifier
    logger.info(f"Stored code_verifier in session: {code_verifier[:10]}...")
    logger.info(f"Session contents: {dict(session)}")
    return render_template('auth.html', auth_url=auth_url)

@app.route('/process_auth', methods=['POST'])
def process_auth():
    try:
        returned_url = request.form['returned_url']
        code_verifier = session.get('code_verifier')
        
        logger.info(f"Processing auth with returned_url: {returned_url}")
        logger.info(f"Processing auth with code_verifier: {code_verifier[:10] if code_verifier else 'None'}...")
        logger.info(f"Session contents: {dict(session)}")
        
        if not code_verifier:
            return jsonify({"error": "No code verifier found. Please restart the auth process."}), 400
        
        # Get initial tokens using authorization code
        headers, payload = construct_headers_and_payload(returned_url, code_verifier)
        initial_tokens = retrieve_tokens(headers, payload)
        
        logger.info("Got initial tokens, now getting access token using refresh token approach")
        
        # Now use the same approach as j.ipynb - use refresh token to get access token
        refresh_token = initial_tokens.get('refresh_token')
        if not refresh_token:
            return jsonify({"error": "No refresh token received from initial auth"}), 400
        
        # Use the refresh_token method like in j.ipynb
        access_token = refresh_token_method(APP_KEY, APP_SECRET, refresh_token)
        
        TokenStore['access_token'] = access_token
        TokenStore['refresh_token'] = refresh_token
        TokenStore['expires_at'] = 0
        start_refresh_token_scheduler() 
        AccountsTrading.access_token = access_token 
        logger.info("Successfully stored tokens in token store ")
        return jsonify({"success": True, "message": "Authentication successful!"})
        
    except Exception as e:
        logger.error(f"Authentication error: {str(e)}")
        return jsonify({"error": str(e)}), 400

@app.route('/calculate_totals')
def calculate_totals():
    access_token = TokenStore['access_token']
    
    logger.info(f"Calculating totals with access_token: {access_token[:10] if access_token else 'None'}...")
    logger.info(f"Session contents: {dict(session)}")
    
    if not access_token:
        return jsonify({"error": "No access token found. Please authenticate first."}), 401
    
    try:
        logger.info("Creating AccountsTrading instance...")
        accounts = AccountsTrading(access_token)
        logger.info(f"AccountsTrading instance created successfully. Found {len(AccountsTrading.account_hash_map)} accounts.")
        
        if not AccountsTrading.account_hash_map:
            return jsonify({"error": "No accounts found or failed to retrieve account information"}), 400
        
        results = {}
        
        for account_number, hash_value in AccountsTrading.account_hash_map.items():
            logger.info(f"Processing account {account_number} with hash {hash_value[:10]}...")
            try:
                account_total = accounts.calc_total(hash_value)
                results[account_number] = account_total
                if account_number == "34614483":
                    logger.info(f"Successfully begin to get accunt detail for : 34614483")
                    #accounts.list_orders(hash_value)
                    #accounts.place_orders(hash_value)
                    logger.info(f"Successfully end to get accunt detail for : 34614483")
                else:
                    logger.info(f"failed to get accunt detail for : 34614483")
                logger.info(f"Successfully calculated totals for account {account_number}\n")
            except Exception as e:
                logger.error(f"Error calculating totals for account {account_number}: {str(e)}")
                results[account_number] = {"error": str(e)}
        
        logger.info(f"Calculation completed. Results: {results}")
        return jsonify(results)
        
    except Exception as e:
        logger.error(f"Calculation error: {str(e)}")
        import traceback
        logger.error(f"Full traceback: {traceback.format_exc()}")
        return jsonify({"error": str(e)}), 400

@app.route('/refresh_token')
def refresh_token():
    refresh_token = TokenStore['refresh_token']
    
    logger.info(f"Refreshing token with refresh_token: {refresh_token[:10] if refresh_token else 'None'}...")
    
    if not refresh_token:
        return jsonify({"error": "No refresh token found. Please authenticate first."}), 401
    
    try:
        url = "https://api.schwabapi.com/v1/oauth/token"
        
        headers = {
            "Content-Type": "application/x-www-form-urlencoded",
            "Authorization": "Basic " + base64.b64encode(f"{APP_KEY}:{APP_SECRET}".encode()).decode()
        }

        data = {
            "grant_type": "refresh_token",
            "refresh_token": refresh_token
        }

        response = requests.post(url, headers=headers, data=data)
        response.raise_for_status()
        
        token_data = response.json()
        expires_in = token_data.get("expires_in") or DEFAULT_EXPIRES_IN
        TokenStore["expires_at"] = int(time.time()) + expires_in
        TokenStore['access_token'] = token_data["access_token"]
        TokenStore['refresh_token'] = token_data["refresh_token"]
        AccountsTrading.access_token = TokenStore['access_token']

        logger.info(f"Successfully refreshed access token , response :{token_data}")
        return jsonify({"success": True, "message": "Token refreshed successfully!"})
        
    except Exception as e:
        logger.error(f"Token refresh error: {str(e)}")
        return jsonify({"error": str(e)}), 400

if __name__ == '__main__':
    #app.run(debug=True, port=5052)
    #socketio.run(app, host="0.0.0.0", port=5052, certfile='/etc/nginx/ssl/app.daoyi.ai/NGINX/bundleCert.crt', keyfile='/etc/nginx/ssl/app.daoyi.ai/privateKey.key', debug=False)
    socketio.run(app, host="127.0.0.1", port=5052,  debug=False)
