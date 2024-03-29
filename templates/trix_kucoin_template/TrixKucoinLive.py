import sys
import time
import traceback
from time import sleep


sys.path.insert(0, "/home/anisse9/bot_app")
import emailing

import warnings

warnings.simplefilter(action='ignore', category=FutureWarning)

from utilities.bdd_communication import *
import ta
import ccxt

exchangeWallet = ccxt.kucoin()

now = datetime.now()
current_time = now.strftime("%d/%m/%Y %H:%M:%S")
print("")
print("--- Start Execution Time :", current_time, "---")
print("")
pwd = mot_de_passe
cnx = mysql.connector.connect(host='localhost', user='root', password=pwd, port='3306', database='cryptos',
                              auth_plugin='mysql_native_password')
cursor = cnx.cursor()
query = "select p.* , b.nom_bot, b.working from params_bot_trix as p ,bots as b where b.bot_id = p.bot_id and b.type_bot ='Trix Kucoin';"
cursor.execute(query)
myresult = cursor.fetchall()


def getHistorical(client, symbol):
    sleep(10)
    klinesT = client.fetch_ohlcv(symbol, '1h', since=(pd.Timestamp('now') - pd.Timedelta(days=5)).timestamp() * 1000)
    sleep(10)
    dataT = pd.DataFrame(klinesT, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
    dataT['timestamp'] = pd.to_datetime(dataT['timestamp'], unit='ms')
    dataT.set_index('timestamp', inplace=True)
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


def get_step_size(client, symbol):
    stepSize = None
    for filter in client.get_symbol_info(symbol)['filters'].copy():
        if filter['filterType'] == 'LOT_SIZE':
            stepSize = float(filter['stepSize'])
    return stepSize


def get_price_step(client, symbol):
    stepSize = None
    for filter in client.get_symbol_info(symbol)['filters'].copy():
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
        montant = client.fetch_balance()['total'][pairSymbol[:-4]]
        
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

def processus(i,con,iterations,fiatAmount,cryptoAmount):
    if sellCondition(df.iloc[-2], df.iloc[-3], stoch_bottom):
        if float(cryptoAmount) > minToken:
            montant = client.fetch_balance()['total'][pairSymbol[:-4]]

            sellOrder = client.create_order(pairsSymbol, "market", "sell", montant, 1)

            fiatAmount = float(client.fetch_balance()['total']['USDT'])

            cryptoAmount = float(get_wallet(client, pairSymbol))

            ticker = exchangeWallet.fetch_ticker(pairsSymbol)

            crypto_wallet_value = fiatAmount + (cryptoAmount * ticker['last'])
            con.insert_balence(datetime.now(),
                               f"Trix : {i[4]}_len{i[5]}_sign{i[6]}_top{i[7]}_bottom{i[8]}_RSI{i[9]}",
                               crypto_wallet_value, i[10], "ONN", "sell", "No Problem")
            print("SELL")
            iterations = True
        else:
            fiatAmount = float(client.fetch_balance()['total']['USDT'])

            cryptoAmount = float(get_wallet(client, pairSymbol))

            ticker = exchangeWallet.fetch_ticker(pairsSymbol)

            crypto_wallet_value = fiatAmount + (cryptoAmount * ticker['last'])
            con.insert_balence(datetime.now(),
                               f"Trix : {i[4]}_len{i[5]}_sign{i[6]}_top{i[7]}_bottom{i[8]}_RSI{i[9]}",
                               crypto_wallet_value, i[10], "ONN", "sell", "No Problem")
            print("If you give me more", cryptoSymbol, "I will sell it")
            iterations = True
    elif buyCondition(df.iloc[-2], df.iloc[-3], stoch_top):
        if float(fiatAmount) > 5:
            try:
                while (True):
                    buyOrder = client.create_order(pairsSymbol, "market", "buy", fiatAmount, 1)

                    fiatAmount = float(client.fetch_balance()['total']['USDT'])

            except:
                pass
            # buyOrder = client.create_order(pairsSymbol, "market", "buy", fiatAmount, 1)
            fiatAmount = float(client.fetch_balance()['total']['USDT'])

            cryptoAmount = float(get_wallet(client, pairSymbol))

            ticker = exchangeWallet.fetch_ticker(pairsSymbol)

            crypto_wallet_value = fiatAmount + (cryptoAmount * ticker['last'])
            con.insert_balence(datetime.now(),
                               f"Trix : {i[4]}_len{i[5]}_sign{i[6]}_top{i[7]}_bottom{i[8]}_RSI{i[9]}",
                               crypto_wallet_value, i[10], "ONN", "buy", "No Problem")
            print("BUY")
            iterations = True
        else:
            fiatAmount = float(client.fetch_balance()['total']['USDT'])

            cryptoAmount = float(get_wallet(client, pairSymbol))

            ticker = exchangeWallet.fetch_ticker(pairsSymbol)

            crypto_wallet_value = fiatAmount + (cryptoAmount * ticker['last'])
            con.insert_balence(datetime.now(),
                               f"Trix : {i[4]}_len{i[5]}_sign{i[6]}_top{i[7]}_bottom{i[8]}_RSI{i[9]}",
                               crypto_wallet_value, i[10], "ONN", "buy", "No Problem")
            print("If you  give me more USD I will buy more", cryptoSymbol)
            iterations = True
    else:
        print("No opportunity to take")
        fiatAmount = float(client.fetch_balance()['total']['USDT'])

        cryptoAmount = float(get_wallet(client, pairSymbol))

        ticker = exchangeWallet.fetch_ticker(pairsSymbol)

        crypto_wallet_value = fiatAmount + (cryptoAmount * ticker['last'])
        last_status_trix = con.get_last_status_trix(i[10])[0]
        con.insert_balence(datetime.now(),
                           f"Trix : {i[4]}_len{i[5]}_sign{i[6]}_top{i[7]}_bottom{i[8]}_RSI{i[9]}",
                           crypto_wallet_value, i[10], "ONN", str(last_status_trix), "No Problem")
        iterations = True


for i in myresult:
    if i[12]:
        con = ConnectBbd('localhost', '3306', 'root', pwd, 'cryptos', 'mysql_native_password')
        iterations = False
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
        client = ccxt.kucoin({
            'apiKey': bybit_api_key,
            'secret': bybit_api_secret,
            'password': password_api_secret,
            'enableRateLimit': True
        })
        df = getHistorical(client, pairsSymbol)

        df['TRIX'] = ta.trend.ema_indicator(
            ta.trend.ema_indicator(ta.trend.ema_indicator(close=df['close'], window=trixLength), window=trixLength),
            window=trixLength)
        df['TRIX_PCT'] = df["TRIX"].pct_change() * 100
        df['TRIX_SIGNAL'] = ta.trend.sma_indicator(df['TRIX_PCT'], trixSignal)
        df['TRIX_HISTO'] = df['TRIX_PCT'] - df['TRIX_SIGNAL']
        df['STOCH_RSI'] = ta.momentum.stochrsi(close=df['close'], window=stoch_rsi, smooth1=3, smooth2=3)

        actualPrice = df['close'].iloc[-1]
        fiatAmount = float(client.fetch_balance()['total']['USDT'])

        # fiatAmount = float(client.get_asset_balance(asset=fiatSymbol)['free'])  # 23.45
        cryptoAmount = float(get_wallet(client, pairSymbol))

        # cryptoAmount = float(client.get_asset_balance(asset=cryptoSymbol)['free'])  # 5.24e-05
        minToken = 5 / actualPrice
        print(" ")
        print(f"{i[11]} : usd balance = {fiatAmount} ")
        try:
            processus(i,con,iterations,fiatAmount,cryptoAmount)
        except Exception as ex:
            if "429000" in str(ex):
                iterations = False
                Nbiterations = 6
                for l in range(Nbiterations):
                    if iterations :
                        break
                    try :
                        time.sleep(10)
                        print("")
                        print(f"Itération N°{l + 1} a commencé")
                        processus(i,con,iterations,fiatAmount,cryptoAmount)
                    except Exception:
                        print(f"Itération N°{l + 1} echoué")
                    if l == Nbiterations :
                        con.insert_balence(datetime.now(),
                                           f"Trix : {i[4]}_len{i[5]}_sign{i[6]}_top{i[7]}_bottom{i[8]}_RSI{i[9]}",
                                           "0", i[10], "OFF", "none", str(ex))
                        name_bot = i[11]
                        emailing.send_mail("helmichiha@gmail.com", name_bot, "Trix Kucoin", ex,
                                           traceback.format_exc())
                        emailing.send_mail("aitmoummad.anisse@gmail.com", name_bot, "Trix Kucoin", ex,
                                           traceback.format_exc())
                        emailing.send_mail("aitmoummad.yassine@gmail.com", name_bot, "Trix Kucoin", ex,
                                           traceback.format_exc())
            else :
                print(f"----Exception of {i[11]}----")
                print(ex)
                traceback.print_exc()
                con.insert_balence(datetime.now(),
                                   f"Trix : {i[4]}_len{i[5]}_sign{i[6]}_top{i[7]}_bottom{i[8]}_RSI{i[9]}",
                                   "0", i[10], "OFF", "none",str(ex))
                name_bot = i[11]
                emailing.send_mail("helmichiha@gmail.com", name_bot, "Trix Kucoin", ex,
                                   traceback.format_exc())
                emailing.send_mail("aitmoummad.anisse@gmail.com", name_bot, "Trix Kucoin", ex,
                                   traceback.format_exc())
                emailing.send_mail("aitmoummad.yassine@gmail.com", name_bot, "Trix Kucoin", ex,
                                   traceback.format_exc())
                print("-----------------")

print("")
print("--- End Execution Time ---")
print("")
