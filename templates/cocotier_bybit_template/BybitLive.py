# import pandas as pd
# import numpy as np
# from datetime import datetime, timedelta
import sys

import pandas as pd

sys.path.insert(0, "/home/anisse9/bot_app")
import ccxt
from fonctions import *
from pass_secret import mot_de_passe
from bdd_communication import ConnectBbd
import mysql.connector
import bybit
from binance.client import Client

# import ta

print(" ")
print("-----Start the script------")

pwd = mot_de_passe
cnx = mysql.connector.connect(host='localhost', user='root', password=pwd, port='3306', database='cryptos',
                              auth_plugin='mysql_native_password')
cursor = cnx.cursor()
query = "select p.*, b.nom_bot from Params_bot_Cocotier as p, bots as b where p.bot_id = b.bot_id and b.type_bot = 'bybit';"
cursor.execute(query)
myresult = cursor.fetchall()

for i in myresult:
    try :
        con = ConnectBbd('localhost', '3306', 'root', pwd, 'cryptos', 'mysql_native_password')
        apiKey = i[1]
        secret = i[2]
        password = i[3]
        market = i[4].split(',')
        for j in range(len(market)):
            market[j] = market[j].upper() + "/USDT"
        d_hour = i[5]
        delta_hour = str(i[5]) + 'h'
        type_computing = i[6]
        name_bot = i[8]

        # verify the time for the crontab

        query = f"select dates from get_balence where id_bot ={i[7]} order by dates desc limit 1;"
        cursor.execute(query)
        datea = str(cursor.fetchall()[0][0])
        lastDate = datetime.strptime(datea, '%Y-%m-%d %H:%M:%S')
        currentDate = datetime.now() - timedelta(hours=(d_hour - 1))
        show_time = datetime.now()
        if (currentDate >= lastDate and int(show_time.hour) % d_hour == 0):
            start_time = datetime.now() - timedelta(2)
            crypto = {}
            exchange = ccxt.bybit({
                'apiKey': apiKey,
                'secret': secret,
                'password': password,
                'enableRateLimit': True
            })

            print(" ")
            print("///////////////")
            print(f"ByBit Bot : {name_bot}")
            print(" ")

            # Get the values
            stt = datetime.strftime(start_time, '%Y-%m-%d %H:%M:%S')
            show_time = datetime.strftime(show_time, '%Y-%m-%d %H:%M:%S')
            for elm in market:
                x = elm[:-5].lower()

                klinesT = Client().get_historical_klines(elm.replace("/", ""), delta_hour, stt)
                df = pd.DataFrame(klinesT,
                                  columns=['timestamp', x + '_open', 'high', 'low', x + '_close', 'volume', 'close_time',
                                           'quote_av', 'trades', 'tb_base_av', 'tb_quote_av', 'ignore'])
                df = df[['timestamp', x + '_open', x + '_close']]
                df[x + '_close'] = pd.to_numeric(df[x + '_close'])
                df[x + '_open'] = pd.to_numeric(df[x + '_open'])
                df = df.set_index('timestamp')
                df.index = pd.to_datetime(df.index, unit='ms')
                crypto[elm.lower()] = df

            # Get the best bot
            print("============= the dataframe=============")
            # print((crypto))
            print(affichageDataFrameLog(crypto).tail(4).head(3).to_string())
            print("============= the dataframe=============")
            crypto = variationN(crypto, type_computing)
            crypto = coeffMulti(crypto)
            crypto = mergeCryptoTogether(crypto)
            del crypto['BOT_MAX']
            nom_crypto_achat = getBotMax(crypto, market, type_computing)
            # Sell Then Buy maybe here we need to do an exception management
            try:
                nom_crypto_vente = crypto_a_vendre(exchange, market)
                algo_achat_vente(exchange, nom_crypto_vente, nom_crypto_achat)

                print(" ")
                print(f"Plage Horraire = {delta_hour}")
                print(" ")
                print(f"computing = {type_computing}")
                print(" ")
                print(
                    f"{show_time} , la meilleur crypto est {nom_crypto_achat}, je vends {nom_crypto_vente} et j'achete {nom_crypto_achat}")

                # Save the wallet value
                wallet = get_wallet(exchange)
                print(f"The new crypto wallet is {wallet}")
                con.insert_balence(datetime.now(), nom_crypto_achat, wallet, i[7])
            except Exception as exceptions:
                print("*****Exceptions*****")
                print(exceptions)
                print("********************")
    except Exception as eee :
        print(eee)
print("-----End of the script-----")
print(" ")
