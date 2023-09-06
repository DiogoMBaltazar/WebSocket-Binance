import json
import time
import sqlite3
import threading
from websocket import WebSocketApp
import requests

from datetime import datetime

def timestamp_to_datetime(timestamp):
    # Convert milliseconds to seconds (if needed)
    if len(str(timestamp)) > 10:  # it's probably in milliseconds
        timestamp = timestamp / 1000
        
    dt = datetime.utcfromtimestamp(timestamp)
    return dt.strftime('%Y-%m-%d %H:%M:%S')


# Binance API endpoint for exchange information
BINANCE_EXCHANGE_INFO = "https://api.binance.com/api/v3/exchangeInfo"

# Binance WebSocket endpoint
BINANCE_WEBSOCKET_URL = "wss://stream.binance.com:9443/ws/{}@kline_1m"

def get_top_50_pairs():
    response = requests.get('https://api.binance.com/api/v3/ticker/24hr')
    tickers = response.json()
    
    # Sort by 24-hour quote volume
    sorted_tickers = sorted(tickers, key=lambda x: float(x.get('quoteVolume', 0)), reverse=True)
    
    return [ticker['symbol'] for ticker in sorted_tickers[:50]]
def on_message(ws, message):
    data = json.loads(message)
    #print(f"Received WebSocket Message: {data}")
    
    # Check if 'k' and 'o' keys exist in the received message
    if 'k' in data and 'o' in data['k']:
        # print(data['k'])
        kline = data['k']
        open_price = kline['o']
        # print(open_price)
        high_price = kline['h']
        # print(high_price)
        low_price = kline['l']
        # print(low_price)
        close_price = kline['c']
        # print(close_price)
        volume = kline['V']
        # print(volume)
        timestamp = kline['T']
        timestamp_format = timestamp_to_datetime(timestamp)
        symbol = data['s']

        # Connect to the SQLite database
        conn = sqlite3.connect('crypto_data.db')
        c = conn.cursor()

        # Insert the data into the ohlcv table
        c.execute("INSERT INTO ohlcv (date, symbol, open, high, low, close, volume) VALUES (?, ?, ?, ?, ?, ?, ?)",
                  (timestamp, symbol, open_price, high_price, low_price, close_price, volume))
        print("-----------------")
        print("Inserted values for ", {symbol}, " as of ", timestamp_format )
        print("-----------------")

        conn.commit()
        conn.close()
    else:
        print(f"Received message does not contain expected keys. Message: {data}")

# Added WebSocket event handlers for error, close, and open
def on_error(ws, error):
    print(f"WebSocket Error: {error}")
    time.sleep(5)  # Wait for 5 seconds before attempting a reconnection
    connect_to_websocket(ws.url.split('/')[-1].split('@')[0])

def on_close(ws, close_status_code, close_msg):
    print(f"WebSocket Closed. Code: {close_status_code}, Message: {close_msg}")
    time.sleep(5)  # Wait for 5 seconds before attempting a reconnection
    connect_to_websocket(ws.url.split('/')[-1].split('@')[0])

def on_open(ws):
    print(f"WebSocket Opened for {ws.url.split('/')[-1]}")
    # Ping every 10 seconds

def connect_to_websocket(symbol):
    ws_url = BINANCE_WEBSOCKET_URL.format(symbol.lower())
    ws = WebSocketApp(ws_url, on_message=on_message, on_error=on_error, on_close=on_close)
    ws.on_open = on_open
    ws.run_forever()

def threaded_websocket_connection(symbol):
    thread = threading.Thread(target=connect_to_websocket, args=(symbol,))
    thread.start()
    time.sleep(0.5)  # 

if __name__ == "__main__":
    top_50_pairs = get_top_50_pairs()

    for pair in top_50_pairs:
        print(pair)
        threaded_websocket_connection(pair)
