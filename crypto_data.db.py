import sqlite3

# Connect to the database (it'll create a file named "crypto_data.db")
conn = sqlite3.connect('crypto_data.db')
c = conn.cursor()

# Create the OHLCV table
c.execute('''
CREATE TABLE IF NOT EXISTS ohlcv (
    date text,
    symbol text,
    open real,
    high real,
    low real,
    close real,
    volume real
)
''')

conn.commit()
conn.close()



# conn = sqlite3.connect('crypto_data.db')
# c = conn.cursor()

# c.execute("SELECT * FROM ohlcv WHERE symbol='BTCUSDT'")
# data = c.fetchall()

# for row in data:
#     print(row)

# conn.close()