import mysql.connector
import pandas as pd
import ftx
from bdd_communication import ConnectBbd
from datetime import datetime
import time
from math import *
import ta


def truncate(n, decimals=0):
    r = floor(float(n) * 10 ** decimals) / 10 ** decimals
    return str(r)


def getBalance(myclient, coin):
    jsonBalance = myclient.get_balances()
    if jsonBalance == []:
        return 0
    pandaBalance = pd.DataFrame(jsonBalance)
    if pandaBalance.loc[pandaBalance['coin'] == coin].empty:
        return 0
    else:
        return float(pandaBalance.loc[pandaBalance['coin'] == coin]['free'])


def buyCondition(row, stochTop_conf):
    if row['TRIX_HISTO'] > 0 and row['STOCH_RSI'] <= stochTop_conf:
        return True
    else:
        return False


def sellCondition(row, stochBottom_conf):
    if row['TRIX_HISTO'] < 0 and row['STOCH_RSI'] >= stochBottom_conf:
        return True
    else:
        return False


# First Task
# Get All the necessary columns from the database


cnx = mysql.connector.connect(host='localhost', user='root', password='system', port='3306', database='cryptos',
                              auth_plugin='mysql_native_password')
cursor = cnx.cursor()
query = "select * from params_bot_trix;"
cursor.execute(query)
myresult = cursor.fetchall()

# Trix Set : id, api_key, secret_key, sub_account, pair_symbol, trix_length, trix_signal, stoch_top, stoch_bottom,
# stoch_RSI, bot_id

# Second Task
# For each line launch the api and get the crypto_wallet value

for i in myresult:
    client = ftx.FtxClient(api_key=i[1], api_secret=i[2], subaccount_name=i[3])
    fiatSymbol = 'USD'
    cryptoSymbol = (i[4] + "").upper()
    pairSymbol = cryptoSymbol + '/USD'
    myTruncate = 3

    data = client.get_historical_data(market_name=pairSymbol, resolution=3600, limit=1000,
                                      start_time=float(round(time.time())) - 150 * 3600,
                                      end_time=float(round(time.time())))
    df = pd.DataFrame(data)

    trixLength = i[5]
    trixSignal = i[6]
    df['TRIX'] = ta.trend.ema_indicator(
        ta.trend.ema_indicator(ta.trend.ema_indicator(close=df['close'], window=trixLength), window=trixLength),
        window=trixLength)
    df['TRIX_PCT'] = df["TRIX"].pct_change() * 100
    df['TRIX_SIGNAL'] = ta.trend.sma_indicator(df['TRIX_PCT'], trixSignal)
    df['TRIX_HISTO'] = df['TRIX_PCT'] - df['TRIX_SIGNAL']
    df['STOCH_RSI'] = ta.momentum.stochrsi(close=df['close'], window=i[9], smooth1=3, smooth2=3)

    actualPrice = df['close'].iloc[-1]
    fiatAmount = getBalance(client, fiatSymbol)
    cryptoAmount = getBalance(client, cryptoSymbol)
    minToken = 5 / actualPrice

    if buyCondition(df.iloc[-2], i[7]):
        if float(fiatAmount) > 5:
            quantityBuy = truncate(float(fiatAmount) / actualPrice, myTruncate)
            buyOrder = client.place_order(
                market=pairSymbol,
                side="buy",
                price=None,
                size=quantityBuy,
                type='market')
        else:
            goOn = True

    elif sellCondition(df.iloc[-2], i[8]):
        if float(cryptoAmount) > minToken:
            sellOrder = client.place_order(
                market=pairSymbol,
                side="sell",
                price=None,
                size=truncate(cryptoAmount, myTruncate),
                type='market')
        else:
            goOn = True
    else:
        goOn = True

    listBalances = sorted(client.get_balances(), key=lambda d: d['total'], reverse=True)
    con = ConnectBbd('localhost', '3306', 'root', 'system', 'cryptos', 'mysql_native_password')
    con.insert_trix_balence(datetime.now(), f"Trix : {i[4]}_len{i[5]}_sign{i[6]}_top{i[7]}_bottom{i[8]}_RSI{i[9]}",
                            listBalances[0]['total'], i[10])

print("We're done")
