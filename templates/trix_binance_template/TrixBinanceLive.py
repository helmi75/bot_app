import sys
import time
import traceback


sys.path.insert(0,"/home/anisse9/bot_app")
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

exchangeWallet = ccxt.binance()

now = datetime.now()
current_time = now.strftime("%d/%m/%Y %H:%M:%S")
print("")
print("--- Start Execution Time :", current_time, "---")
print("")
pwd = mot_de_passe
cnx = mysql.connector.connect(host='localhost', user='root', password=pwd, port='3306', database='cryptos',
                              auth_plugin='mysql_native_password')
cursor = cnx.cursor()
query = "select p.* , b.nom_bot,b.working from params_bot_trix as p ,bots as b where b.bot_id = p.bot_id and b.type_bot ='Trix Binance';"
cursor.execute(query)
myresult = cursor.fetchall()


def getHistorical(client,symbole):
    klinesT = client.get_historical_klines(
        symbole, Client.KLINE_INTERVAL_1HOUR, "5 day ago UTC")
    dataT = pd.DataFrame(klinesT, columns = ['timestamp', 'open', 'high', 'low', 'close', 'volume', 'close_time', 'quote_av', 'trades', 'tb_base_av', 'tb_quote_av', 'ignore' ])
    dataT['close'] = pd.to_numeric(dataT['close'])
    dataT['high'] = pd.to_numeric(dataT['high'])
    dataT['low'] = pd.to_numeric(dataT['low'])
    dataT['open'] = pd.to_numeric(dataT['open'])
    dataT['volume'] = pd.to_numeric(dataT['volume'])
    dataT.drop(dataT.columns.difference(['open','high','low','close','volume']), 1, inplace=True)
    return dataT

def getBalance(myclient, coin):
    jsonBalance = myclient.get_balances()
    if jsonBalance == []:
        return 0
    pandaBalance = pd.DataFrame(jsonBalance)
    if pandaBalance.loc[pandaBalance['coin'] == coin].empty:
        return 0
    else:
        return float(pandaBalance.loc[pandaBalance['coin'] == coin]['free'])

def get_step_size(client,symbol):
    stepSize = None
    for filter in client.get_symbol_info(symbol)['filters']:
        if filter['filterType'] == 'LOT_SIZE':
            stepSize = float(filter['stepSize'])
    return stepSize

def get_price_step(client,symbol):
    stepSize = None
    for filter in client.get_symbol_info(symbol)['filters']:
        if filter['filterType'] == 'PRICE_FILTER':
            stepSize = float(filter['tickSize'])
    return stepSize

def convert_amount_to_precision(client,symbol, amount):
    stepSize = get_step_size(client,symbol)
    return (amount//stepSize)*stepSize

def convert_price_to_precision(client,symbol, price):
    stepSize = get_price_step(client,symbol)
    return (price//stepSize)*stepSize

def buyCondition(row, previousRow,stochRsiTop):
    if row['TRIX_HISTO'] > 0 and row['STOCH_RSI'] <= stochRsiTop:#stoch RSI top
        return True
    else:
        return False

def sellCondition(row, previousRow,stochRsiBottom):
    if row['TRIX_HISTO'] < 0 and row['STOCH_RSI'] >= stochRsiBottom:#stoch rsi bottom
        return True
    else:
        return False

def processus(i,con,iterations):
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
    binance_api_key = i[1]  # Enter your own API-key here
    binance_api_secret = i[2]  # Enter your own API-secret here
    idd = i[10]
    binance_api_key, binance_api_secret = degenerateApiSecret(binance_api_key, binance_api_secret, idd)
    client = Client(api_key=binance_api_key, api_secret=binance_api_secret)
    df = getHistorical(client, pairSymbol.replace("/", ""))
    df['TRIX'] = ta.trend.ema_indicator(
        ta.trend.ema_indicator(ta.trend.ema_indicator(close=df['close'], window=trixLength), window=trixLength),
        window=trixLength)
    df['TRIX_PCT'] = df["TRIX"].pct_change() * 100
    df['TRIX_SIGNAL'] = ta.trend.sma_indicator(df['TRIX_PCT'], trixSignal)
    df['TRIX_HISTO'] = df['TRIX_PCT'] - df['TRIX_SIGNAL']
    df['STOCH_RSI'] = ta.momentum.stochrsi(close=df['close'], window=stoch_rsi, smooth1=3, smooth2=3)

    actualPrice = df['close'].iloc[-1]
    fiatAmount = float(client.get_asset_balance(asset=fiatSymbol)['free'])
    cryptoAmount = float(client.get_asset_balance(asset=cryptoSymbol)['free'])
    minToken = 5 / actualPrice
    print(" ")
    print(f"{i[11]} : usd balance = {fiatAmount} ")
    # print('coin price :', actualPrice, 'usd balance', fiatAmount, 'coin balance :', cryptoAmount)

    if buyCondition(df.iloc[-2], df.iloc[-3], stoch_top):
        if float(fiatAmount) > 5:
            quantityBuy = convert_amount_to_precision(client, pairSymbol, (float(fiatAmount) / actualPrice))
            buyOrder = client.order_market_buy(
                symbol=pairSymbol,
                quantity=f"{float(quantityBuy):.{decimal_count}f}")
            fiatAmount = float(client.get_asset_balance(asset=fiatSymbol)['free'])
            cryptoAmount = float(client.get_asset_balance(asset=cryptoSymbol)['free'])
            ticker = exchangeWallet.fetch_ticker(pairsSymbol)
            crypto_wallet_value = fiatAmount + (cryptoAmount * ticker['last'])
            con.insert_balence(datetime.now(),
                               f"Trix : {i[4]}_len{i[5]}_sign{i[6]}_top{i[7]}_bottom{i[8]}_RSI{i[9]}",
                               crypto_wallet_value, i[10], "ONN", "buy","No Problem")

            print("BUY")
            iterations = True
        else:
            fiatAmount = float(client.get_asset_balance(asset=fiatSymbol)['free'])
            cryptoAmount = float(client.get_asset_balance(asset=cryptoSymbol)['free'])
            ticker = exchangeWallet.fetch_ticker(pairsSymbol)
            crypto_wallet_value = fiatAmount + (cryptoAmount * ticker['last'])
            con.insert_balence(datetime.now(),
                               f"Trix : {i[4]}_len{i[5]}_sign{i[6]}_top{i[7]}_bottom{i[8]}_RSI{i[9]}",
                               crypto_wallet_value, i[10], "ONN", "buy","No Problem")
            print("If you  give me more USD I will buy more", cryptoSymbol)
            iterations = True

    elif sellCondition(df.iloc[-2], df.iloc[-3], stoch_bottom):
        if float(cryptoAmount) > minToken:
            sellOrder = client.order_market_sell(
                symbol=pairSymbol,
                quantity=f"{float(convert_amount_to_precision(client, pairSymbol, cryptoAmount)):.{decimal_count}f}")
            fiatAmount = float(client.get_asset_balance(asset=fiatSymbol)['free'])
            cryptoAmount = float(client.get_asset_balance(asset=cryptoSymbol)['free'])
            ticker = exchangeWallet.fetch_ticker(pairsSymbol)
            crypto_wallet_value = fiatAmount + (cryptoAmount * ticker['last'])
            con.insert_balence(datetime.now(),
                               f"Trix : {i[4]}_len{i[5]}_sign{i[6]}_top{i[7]}_bottom{i[8]}_RSI{i[9]}",
                               crypto_wallet_value, i[10], "ONN", "sell","No Problem")
            print("SELL")
            iterations = True
        else:
            fiatAmount = float(client.get_asset_balance(asset=fiatSymbol)['free'])
            cryptoAmount = float(client.get_asset_balance(asset=cryptoSymbol)['free'])
            ticker = exchangeWallet.fetch_ticker(pairsSymbol)
            crypto_wallet_value = fiatAmount + (cryptoAmount * ticker['last'])
            con.insert_balence(datetime.now(),
                               f"Trix : {i[4]}_len{i[5]}_sign{i[6]}_top{i[7]}_bottom{i[8]}_RSI{i[9]}",
                               crypto_wallet_value, i[10], "ONN", "sell","No Problem")
            print("If you give me more", cryptoSymbol, "I will sell it")
            iterations = True
    else:
        print("No opportunity to take")
        fiatAmount = float(client.get_asset_balance(asset=fiatSymbol)['free'])
        cryptoAmount = float(client.get_asset_balance(asset=cryptoSymbol)['free'])
        ticker = exchangeWallet.fetch_ticker(pairsSymbol)
        crypto_wallet_value = fiatAmount + (cryptoAmount * ticker['last'])
        last_status_trix = con.get_last_status_trix(i[10])[0]
        con.insert_balence(datetime.now(),
                           f"Trix : {i[4]}_len{i[5]}_sign{i[6]}_top{i[7]}_bottom{i[8]}_RSI{i[9]}",
                           crypto_wallet_value, i[10], "ONN", str(last_status_trix),"No Problem")
        iterations = True

def processus2(i,con,iterations):
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
    binance_api_key = i[1]  # Enter your own API-key here
    binance_api_secret = i[2]  # Enter your own API-secret here
    idd = i[10]
    binance_api_key, binance_api_secret = degenerateApiSecret(binance_api_key, binance_api_secret, idd)
    client = Client(api_key=binance_api_key, api_secret=binance_api_secret)
    df = getHistorical(client, pairSymbol.replace("/", ""))
    df['TRIX'] = ta.trend.ema_indicator(
        ta.trend.ema_indicator(ta.trend.ema_indicator(close=df['close'], window=trixLength), window=trixLength),
        window=trixLength)
    df['TRIX_PCT'] = df["TRIX"].pct_change() * 100
    df['TRIX_SIGNAL'] = ta.trend.sma_indicator(df['TRIX_PCT'], trixSignal)
    df['TRIX_HISTO'] = df['TRIX_PCT'] - df['TRIX_SIGNAL']
    df['STOCH_RSI'] = ta.momentum.stochrsi(close=df['close'], window=stoch_rsi, smooth1=3, smooth2=3)

    actualPrice = df['close'].iloc[-1]
    fiatAmount = float(client.get_asset_balance(asset=fiatSymbol)['free'])
    cryptoAmount = float(client.get_asset_balance(asset=cryptoSymbol)['free'])
    minToken = 5 / actualPrice
    print(" ")
    # print(f"{i[11]} : usd balance = {fiatAmount} ")
    # print('coin price :', actualPrice, 'usd balance', fiatAmount, 'coin balance :', cryptoAmount)
    if buyCondition(df.iloc[-2], df.iloc[-3], stoch_top):
        if float(fiatAmount) > 5:
            print(f"Wallet : {fiatAmount} USDT")
            print(f"Coin price {cryptoSymbol} = {actualPrice}")
            print(f"crypot amount  {cryptoSymbol} = {cryptoAmount}")
            print(
                f"Amount {fiatAmount}/{actualPrice} = {floor(100 * (float(fiatAmount) / actualPrice)) / 100} => 0.98*{floor(100 * (float(fiatAmount) / actualPrice)) / 100} = {floor(100 * (float(fiatAmount) / actualPrice)) / 100 * 0.98}")
            print(
                f"order buy = {floor(100 * (float(fiatAmount) / actualPrice)) / 100 * 0.98} * {actualPrice} = {floor(100 * (float(fiatAmount) / actualPrice)) / 100 * 0.98 * actualPrice} USDT")
            quantityBuy = floor(100*(float(fiatAmount) / actualPrice))/100*0.98
            buyOrder = client.order_market_buy(
                symbol=pairSymbol,
                quantity=f"{float(quantityBuy):.{decimal_count}f}")
            fiatAmount = float(client.get_asset_balance(asset=fiatSymbol)['free'])
            cryptoAmount = float(client.get_asset_balance(asset=cryptoSymbol)['free'])
            ticker = exchangeWallet.fetch_ticker(pairsSymbol)
            crypto_wallet_value = fiatAmount + (cryptoAmount * ticker['last'])
            con.insert_balence(datetime.now(),
                               f"Trix : {i[4]}_len{i[5]}_sign{i[6]}_top{i[7]}_bottom{i[8]}_RSI{i[9]}",
                               crypto_wallet_value, i[10], "ONN", "buy","insuffience balance")

            print("BUY")
            iterations = True
        else:
            fiatAmount = float(client.get_asset_balance(asset=fiatSymbol)['free'])
            cryptoAmount = float(client.get_asset_balance(asset=cryptoSymbol)['free'])
            ticker = exchangeWallet.fetch_ticker(pairsSymbol)
            crypto_wallet_value = fiatAmount + (cryptoAmount * ticker['last'])
            con.insert_balence(datetime.now(),
                               f"Trix : {i[4]}_len{i[5]}_sign{i[6]}_top{i[7]}_bottom{i[8]}_RSI{i[9]}",
                               crypto_wallet_value, i[10], "ONN", "buy","insuffience balance")
            print("If you  give me more USD I will buy more", cryptoSymbol)
            iterations = True

    elif sellCondition(df.iloc[-2], df.iloc[-3], stoch_bottom):
        if float(cryptoAmount) > minToken:
            print(f"Wallet : {fiatAmount} USDT")
            print(f"Coin price {cryptoSymbol} = {actualPrice}")
            print(f"crypot amount  {cryptoSymbol} = {cryptoAmount}")
            print(
                f"Amount {cryptoAmount}*{actualPrice} = {floor(100 * (float(cryptoAmount) * actualPrice)) / 100} => 0.98*{floor(100 * (float(cryptoAmount) * actualPrice)) / 100} = {floor(100 * 0.98*(float(fiatAmount) / actualPrice)) / 100}")
            # print(
            #     f"order sell = {floor(100 * (float(fiatAmount) / actualPrice)) / 100 * 0.98} * {actualPrice} = {floor(100 * (float(fiatAmount) / actualPrice)) / 100 * 0.98 * actualPrice} USDT")
            quantityToSell = floor(100*float(cryptoAmount * actualPrice) * 0.98)/100
            sellOrder = client.order_market_sell(
                symbol=pairSymbol,
                quantity=f"{quantityToSell}")
            fiatAmount = float(client.get_asset_balance(asset=fiatSymbol)['free'])
            cryptoAmount = float(client.get_asset_balance(asset=cryptoSymbol)['free'])
            ticker = exchangeWallet.fetch_ticker(pairsSymbol)
            crypto_wallet_value = fiatAmount + (cryptoAmount * ticker['last'])
            con.insert_balence(datetime.now(),
                               f"Trix : {i[4]}_len{i[5]}_sign{i[6]}_top{i[7]}_bottom{i[8]}_RSI{i[9]}",
                               crypto_wallet_value, i[10], "ONN", "sell","insuffience balance")
            print("SELL")
            iterations = True
        else:
            fiatAmount = float(client.get_asset_balance(asset=fiatSymbol)['free'])
            cryptoAmount = float(client.get_asset_balance(asset=cryptoSymbol)['free'])
            ticker = exchangeWallet.fetch_ticker(pairsSymbol)
            crypto_wallet_value = fiatAmount + (cryptoAmount * ticker['last'])
            con.insert_balence(datetime.now(),
                               f"Trix : {i[4]}_len{i[5]}_sign{i[6]}_top{i[7]}_bottom{i[8]}_RSI{i[9]}",
                               crypto_wallet_value, i[10], "ONN", "sell","insuffience balance")
            print("If you give me more", cryptoSymbol, "I will sell it")
            iterations = True
    else:
        print("No opportunity to take")
        fiatAmount = float(client.get_asset_balance(asset=fiatSymbol)['free'])
        cryptoAmount = float(client.get_asset_balance(asset=cryptoSymbol)['free'])
        ticker = exchangeWallet.fetch_ticker(pairsSymbol)
        crypto_wallet_value = fiatAmount + (cryptoAmount * ticker['last'])
        last_status_trix = con.get_last_status_trix(i[10])[0]
        con.insert_balence(datetime.now(),
                           f"Trix : {i[4]}_len{i[5]}_sign{i[6]}_top{i[7]}_bottom{i[8]}_RSI{i[9]}",
                           crypto_wallet_value, i[10], "ONN", str(last_status_trix),"insuffience balance")
        iterations = True


for i in myresult :
    if i[12] :
        con = ConnectBbd('localhost', '3306', 'root', pwd, 'cryptos', 'mysql_native_password')
        iterations = False
        try :
            processus(i,con,iterations)
        except Exception as ex:
            if str(ex).startswith("APIError(code=-2010)"):

                iterations = False
                Nbiterations = 100
                for l in range(Nbiterations):
                    if iterations:
                        break
                    try :
                        time.sleep(1)
                        print("")
                        print(f"Itération N°{l+1} a commencé")
                        processus2(i,con,iterations)
                    except Exception :
                        print(f"Itération N°{l+1} echoué")
                    if l == Nbiterations-1:
                        name_bot = i[11]
                        con.insert_balence(datetime.now(),
                                           f"Trix : {i[4]}_len{i[5]}_sign{i[6]}_top{i[7]}_bottom{i[8]}_RSI{i[9]}",
                                           "0", i[10], "OFF", "none", 'Insuffisance Balence')
                        ex = "Insuffisance Balence Iteration 100 separe par 1s atteint."
                        emailing.send_mail("hadjsassiscompany@gmail.com ", name_bot, "Trix Binance", ex,"")
                        emailing.send_mail("helmichiha@gmail.com ", name_bot, "Trix Binance", ex,"")
                        emailing.send_mail("aitmoummad.anisse@gmail.com", name_bot, "Trix Binance", ex,"")
                        emailing.send_mail("aitmoummad.yassine@gmail.com", name_bot, "Trix Binance", ex,"")
            else :
                print(f"----Exception of {i[11]}----")
                con.insert_balence(datetime.now(),
                                   f"Trix : {i[4]}_len{i[5]}_sign{i[6]}_top{i[7]}_bottom{i[8]}_RSI{i[9]}",
                                   "0", i[10], "OFF", "none",str(ex))
                name_bot = i[11]
                emailing.send_mail("hadjsassiscompany@gmail.com", name_bot, "Trix Binance", ex,
                                   traceback.format_exc())
                emailing.send_mail("helmichiha@gmail.com ", name_bot, "Trix Binance", ex,
                                   traceback.format_exc())
                emailing.send_mail("aitmoummad.anisse@gmail.com", name_bot, "Trix Binance", ex,
                                   traceback.format_exc())
                emailing.send_mail("aitmoummad.yassine@gmail.com", name_bot, "Trix Binance", ex,
                                   traceback.format_exc())
                print(ex)
                print("-----------------")



print("")
print("--- End Execution Time ---")
print("")






