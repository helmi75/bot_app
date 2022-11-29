import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import sys
sys.path.insert(0,"/home/anisse9/bot_app")
import ccxt
from fonctions import *
from pass_secret import mot_de_passe
from bdd_communication import ConnectBbd
import mysql.connector
from binance.client import Client
import ta



pwd = mot_de_passe
cnx = mysql.connector.connect(host='localhost', user='root', password=pwd, port='3306', database='cryptos',
                              auth_plugin='mysql_native_password')
cursor = cnx.cursor()
query = "select * from Params_bot_Cocotier;"
cursor.execute(query)
myresult = cursor.fetchall()

for i in myresult:
    con = ConnectBbd('localhost', '3306', 'root', pwd, 'cryptos', 'mysql_native_password')
    apiKey = i[1]
    secret = i[2]
    market = i[4].split(',')
    for j in range(len(market)):
        market[j] = market[j].upper() + "/USDT"
    d_hour = i[5]
    delta_hour = str(i[5])+'h'
    type_computing = i[6]

    # verify the time for the crontab

    query = f"select dates from get_balence where id_bot ={i[7]} order by dates desc limit 1;"
    cursor.execute(query)
    lastDate = datetime.strptime(cursor.fetchall()[0][0],'%Y-%m-%d %H:%M:%S')
    currentDate = datetime.now() - timedelta(hours=d_hour)
    if(currentDate >= lastDate):
        start_time = datetime.now() - timedelta(2)
        crypto = {}
        exchange = ccxt.binance({
            'apiKey': apiKey,
            'secret': secret,
            'enableRateLimit': True
        })


        #Get the values
        stt = datetime.strftime(start_time, '%Y-%m-%d %H:%M:%S')
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
        crypto = variationN(crypto, type_computing)
        crypto = coeffMulti(crypto)
        crypto = mergeCryptoTogether(crypto)
        del crypto['BOT_MAX']
        nom_crypto_achat = getBotMax(crypto, market, type_computing)
        print(nom_crypto_achat)
        #Sell Then Buy maybe here we need to do an exception management
        try :
            nom_crypto_vente = crypto_a_vendre(exchange, market)
            algo_achat_vente(exchange, nom_crypto_vente, nom_crypto_achat)

            # Save the wallet value
            wallet = get_wallet(exchange)
            con.insert_balence(datetime.now(),nom_crypto_achat , wallet, i[7])
        except Exception as exceptions :
            print(exceptions)