import json
import websocket
import threading
import sqlite3
import requests

def get_top_50_pairs():
    response = requests.get('https://api.binance.com/api/v3/exchangeInfo')
    symbols = response.json()['symbols']
    
    # Filter valid trading pairs
    valid_pairs = [s for s in symbols if s['status'] == 'TRADING']
    
    # Sort by volume (for simplicity, we'll just use the quote asset volume of the previous 24 hours)
    sorted_pairs = sorted(valid_pairs, key=lambda x: float(x['quoteVolume']), reverse=True)
    
    return [pair['symbol'] for pair in sorted_pairs[:50]]

def on_message(ws, message):
    data = json.loads(message)
    kline = data['k']

    # Extract OHLCV data
    open_price = kline['o']
    high_price = kline['h']
    low_price = kline['l']
    close_price = kline['c']
    volume = kline['v']
    timestamp = kline['t']  # You might want to convert this to a human-readable date
    symbol = data['s']

    # Connect to the SQLite database
    conn = sqlite3.connect('crypto_data.db')
    c = conn.cursor()

    print("Inserting ", open_price, "for ", symbol, " at ", timestamp)
    print("---------------------------------------------------------")
    # Insert the data into the ohlcv table
    c.execute("INSERT INTO ohlcv (date, symbol, open, high, low, close, volume) VALUES (?, ?, ?, ?, ?, ?, ?)",
              (timestamp, symbol, open_price, high_price, low_price, close_price, volume))

    conn.commit()
    conn.close()

    
def connect_to_websocket(symbol):
    ws = websocket.WebSocketApp(f"wss://stream.binance.com:9443/ws/{symbol}@kline_1m",
                                on_message=on_message)
    ws.run_forever()

def threaded_websocket_connection(symbol):
    thread = threading.Thread(target=connect_to_websocket, args=(symbol,))
    thread.start()

top_50_pairs = get_top_50_pairs()
print(top_50_pairs)
for pair in top_50_pairs:
    threaded_websocket_connection(pair)