import sys
import traceback


sys.path.insert(0, "/home/anisse9/bot_app")
import emailing

import warnings

warnings.simplefilter(action='ignore', category=FutureWarning)

from binance.client import Client
import pandas as pd
from datetime import datetime
from pass_secret import mot_de_passe
import mysql.connector
from bdd_communication import *
import ta
import ccxt

exchangeWallet = ccxt.bybit()

now = datetime.now()
current_time = now.strftime("%d/%m/%Y %H:%M:%S")
print("")
print("--- Start Execution Time :", current_time, "---")
print("")
pwd = mot_de_passe
cnx = mysql.connector.connect(host='localhost', user='root', password=pwd, port='3306', database='cryptos',
                              auth_plugin='mysql_native_password')
cursor = cnx.cursor()
query = "select p.* , b.nom_bot, b.working from params_bot_trix as p ,bots as b where b.bot_id = p.bot_id and b.type_bot ='Trix Bybit';"
cursor.execute(query)
myresult = cursor.fetchall()


def getHistorical(client, symbole):
    timeInterval = '1h'
    ennDatee = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
    sttDatee = datetime.utcnow() - timedelta(days=5)
    sttDatee = sttDatee.strftime("%Y-%m-%dT%H:%M:%SZ")
    # sttDatee = datetime.strptime(sttDate, '%Y-%m-%d %H:%M:%S')
    # sttDatee = sttDatee.strftime("%Y-%m-%dT%H:%M:%SZ")
    # ennDatee = datetime.strptime(ennDate, '%Y-%m-%d %H:%M:%S')
    # ennDatee = ennDatee.strftime("%Y-%m-%dT%H:%M:%SZ")
    exchange = ccxt.bybit()
    since = exchange.parse8601(sttDatee)
    klinesT = []
    while since < exchange.parse8601(ennDatee):
        klines = exchange.fetch_ohlcv(symbole, timeframe=timeInterval, since=since)
        if len(klines) > 0:
            klinesT += klines
            since = klines[-1][0] + (int(timeInterval[:-1]) * 60 * 60 * 1000)
        else:
            since += (int(timeInterval[:-1]) * 60 * 60 * 1000)
    df = pd.DataFrame(klinesT, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
    df['close'] = pd.to_numeric(df['close'])
    df['high'] = pd.to_numeric(df['high'])
    df['low'] = pd.to_numeric(df['low'])
    df['open'] = pd.to_numeric(df['open'])
    df = df.set_index(df['timestamp'])
    df.index = pd.to_datetime(df.index, unit='ms')
    del df['timestamp']
    df.drop(df.columns.difference(['open', 'high', 'low', 'close', 'volume']), 1, inplace=True)
    return df


def getBalance(myclient, coin):
    jsonBalance = myclient.get_balances()
    if jsonBalance == []:
        return 0
    pandaBalance = pd.DataFrame(jsonBalance)
    if pandaBalance.loc[pandaBalance['coin'] == coin].empty:
        return 0
    else:
        return float(pandaBalance.loc[pandaBalance['coin'] == coin]['free'])


def get_step_size(client, symbol):
    stepSize = None
    for filter in client.get_symbol_info(symbol)['filters']:
        if filter['filterType'] == 'LOT_SIZE':
            stepSize = float(filter['stepSize'])
    return stepSize


def get_price_step(client, symbol):
    stepSize = None
    for filter in client.get_symbol_info(symbol)['filters']:
        if filter['filterType'] == 'PRICE_FILTER':
            stepSize = float(filter['tickSize'])
    return stepSize


def convert_amount_to_precision(client, symbol, amount):
    stepSize = get_step_size(client, symbol)
    return (amount // stepSize) * stepSize


def convert_price_to_precision(client, symbol, price):
    stepSize = get_price_step(client, symbol)
    return (price // stepSize) * stepSize


def get_wallet(exchange, pairSymbol):
    try:
        montant = client.fetch_spot_balance()['total'][pairSymbol[:-4]]
    except Exception as exz:
        montant = 0
    return montant


def buyCondition(row, previousRow, stochRsiTop):
    if row['TRIX_HISTO'] > 0 and row['STOCH_RSI'] <= stochRsiTop:  # stoch RSI top
        return True
    else:
        return False


def sellCondition(row, previousRow, stochRsiBottom):
    if row['TRIX_HISTO'] < 0 and row['STOCH_RSI'] >= stochRsiBottom:  # stoch rsi bottom
        return True
    else:
        return False


for i in myresult:
    if i[12]:
        con = ConnectBbd('localhost', '3306', 'root', pwd, 'cryptos', 'mysql_native_password')
        try:
            # CONSTANTS
            fiatSymbol = 'USDT'
            cryptoSymbol = (i[4] + "").upper()
            pairSymbol = cryptoSymbol + 'USDT'
            pairsSymbol = cryptoSymbol + '/USDT'
            trixLength = i[5]
            trixSignal = i[6]
            decimal_count = 8
            stoch_top = i[7]
            stoch_bottom = i[8]
            stoch_rsi = i[9]
            # API
            bybit_api_key = i[1]  # Enter your own API-key here
            bybit_api_secret = i[2]  # Enter your own API-secret here
            idd = i[10]
            bybit_api_key, bybit_api_secret = degenerateApiSecret(bybit_api_key, bybit_api_secret, idd)
            password_api_secret = i[3]  # Enter your own Password Here
            client = ccxt.bybit({
                'apiKey': bybit_api_key,
                'secret': bybit_api_secret,
                'password': password_api_secret,
                'enableRateLimit': True
            })
            # client = Client(api_key=bybit_api_key, api_secret=bybit_api_secret)
            df = getHistorical(Client(), pairSymbol.replace("/", ""))
            df['TRIX'] = ta.trend.ema_indicator(
                ta.trend.ema_indicator(ta.trend.ema_indicator(close=df['close'], window=trixLength), window=trixLength),
                window=trixLength)
            df['TRIX_PCT'] = df["TRIX"].pct_change() * 100
            df['TRIX_SIGNAL'] = ta.trend.sma_indicator(df['TRIX_PCT'], trixSignal)
            df['TRIX_HISTO'] = df['TRIX_PCT'] - df['TRIX_SIGNAL']
            df['STOCH_RSI'] = ta.momentum.stochrsi(close=df['close'], window=stoch_rsi, smooth1=3, smooth2=3)

            actualPrice = df['close'].iloc[-1]
            fiatAmount = float(client.fetch_spot_balance()['total']['USDT'])
            # fiatAmount = float(client.get_asset_balance(asset=fiatSymbol)['free'])  # 23.45
            cryptoAmount = float(get_wallet(client, pairSymbol))
            # cryptoAmount = float(client.get_asset_balance(asset=cryptoSymbol)['free'])  # 5.24e-05
            minToken = 5 / actualPrice
            print(" ")
            print(f"{i[11]} : usd balance = {fiatAmount} ")
            # print('coin price :', actualPrice, 'usd balance', fiatAmount, 'coin balance :', cryptoAmount)
            if buyCondition(df.iloc[-2], df.iloc[-3], stoch_top):
                if float(fiatAmount) > 5:
                    buyOrder = client.create_spot_order(pairsSymbol, "market", "buy", fiatAmount, 1)
                    # buyOrder = client.order_market_buy(symbol=pairSymbol,quantity=f"{float(quantityBuy):.{decimal_count}f}")
                    fiatAmount = float(client.fetch_spot_balance()['total']['USDT'])
                    cryptoAmount = float(get_wallet(client, pairSymbol))
                    ticker = exchangeWallet.fetch_ticker(pairsSymbol)
                    crypto_wallet_value = fiatAmount + (cryptoAmount * ticker['last'])
                    con.insert_balence(datetime.now(),
                                       f"Trix : {i[4]}_len{i[5]}_sign{i[6]}_top{i[7]}_bottom{i[8]}_RSI{i[9]}",
                                       crypto_wallet_value, i[10], "ONN", "buy","No Problem")
                    print("BUY")
                else:
                    fiatAmount = float(client.fetch_spot_balance()['total']['USDT'])
                    cryptoAmount = float(get_wallet(client, pairSymbol))
                    ticker = exchangeWallet.fetch_ticker(pairsSymbol)
                    crypto_wallet_value = fiatAmount + (cryptoAmount * ticker['last'])
                    con.insert_balence(datetime.now(),
                                       f"Trix : {i[4]}_len{i[5]}_sign{i[6]}_top{i[7]}_bottom{i[8]}_RSI{i[9]}",
                                       crypto_wallet_value, i[10], "ONN", "buy","No Problem")
                    print("If you  give me more USD I will buy more", cryptoSymbol)

            elif sellCondition(df.iloc[-2], df.iloc[-3], stoch_bottom):
                if float(cryptoAmount) > minToken:
                    montant = client.fetch_spot_balance()['total'][pairSymbol[:-4]]
                    sellOrder = client.create_spot_order(pairsSymbol, "market", "sell", montant, 1)
                    fiatAmount = float(client.fetch_spot_balance()['total']['USDT'])
                    cryptoAmount = float(get_wallet(client, pairSymbol))
                    ticker = exchangeWallet.fetch_ticker(pairsSymbol)
                    crypto_wallet_value = fiatAmount + (cryptoAmount * ticker['last'])
                    con.insert_balence(datetime.now(),
                                       f"Trix : {i[4]}_len{i[5]}_sign{i[6]}_top{i[7]}_bottom{i[8]}_RSI{i[9]}",
                                       crypto_wallet_value, i[10], "ONN", "sell","No Problem")
                    print("SELL")
                else:
                    fiatAmount = float(client.fetch_spot_balance()['total']['USDT'])
                    cryptoAmount = float(get_wallet(client, pairSymbol))
                    ticker = exchangeWallet.fetch_ticker(pairsSymbol)
                    crypto_wallet_value = fiatAmount + (cryptoAmount * ticker['last'])
                    con.insert_balence(datetime.now(),
                                       f"Trix : {i[4]}_len{i[5]}_sign{i[6]}_top{i[7]}_bottom{i[8]}_RSI{i[9]}",
                                       crypto_wallet_value, i[10], "ONN", "sell","No Problem")
                    print("If you give me more", cryptoSymbol, "I will sell it")
            else:
                print("No opportunity to take")
                fiatAmount = float(client.fetch_spot_balance()['total']['USDT'])
                cryptoAmount = float(get_wallet(client, pairSymbol))
                ticker = exchangeWallet.fetch_ticker(pairsSymbol)
                crypto_wallet_value = fiatAmount + (cryptoAmount * ticker['last'])
                last_status_trix = con.get_last_status_trix(i[10])[0]
                con.insert_balence(datetime.now(),
                                   f"Trix : {i[4]}_len{i[5]}_sign{i[6]}_top{i[7]}_bottom{i[8]}_RSI{i[9]}",
                                   crypto_wallet_value, i[10], "ONN", str(last_status_trix),"No Problem")

        except Exception as ex:
            print(f"----Exception of {i[11]}----")
            print(ex)
            con.insert_balence(datetime.now(),
                               f"Trix : {i[4]}_len{i[5]}_sign{i[6]}_top{i[7]}_bottom{i[8]}_RSI{i[9]}",
                               "0", i[10], "OFF", "none",str(ex))
            name_bot = i[11]
            emailing.send_mail("hadjsassiscompany@gmail.com", name_bot, "Trix Bybit", ex,
                               traceback.format_exc())
            emailing.send_mail("helmichiha@gmail.com ", name_bot, "Trix Bybit", ex,
                               traceback.format_exc())
            emailing.send_mail("aitmoummad.anisse@gmail.com", name_bot, "Trix Bybit", ex,
                               traceback.format_exc())
            emailing.send_mail("aitmoummad.yassine@gmail.com", name_bot, "Trix Bybit", ex,
                               traceback.format_exc())
            print("-----------------")

print("")
print("--- End Execution Time ---")
print("")
