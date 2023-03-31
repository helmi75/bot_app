import mysql.connector
import sys
import numpy as np
import pandas as pd
from datetime import datetime
from datetime import timedelta
import streamlit as st
import plotly.graph_objects as go
import string
import ccxt
import ftx
from math import *
from binance.client import Client
from pass_secret import mot_de_passe

lowerCase = string.ascii_lowercase
upperCase = string.ascii_uppercase


class ConnectBbd:
    def __init__(self, host, port, user, password, database, auth_plugin):
        self.host = host
        self.port = port
        self.user = user
        self.password = password
        self.database = database
        self.auth_plugin = auth_plugin
        self.cnx = mysql.connector.connect(host=self.host,
                                           user=self.user,
                                           password=self.password,
                                           port=self.port,
                                           database=self.database,
                                           auth_plugin=self.auth_plugin)

    def insert_new_user(self, user_name, email, password):
        cursor = self.cnx.cursor()
        query = """INSERT INTO users (username, email, password) VALUES ('%s', '%s', '%s')""" % (
            user_name, email, password)
        cursor.execute(query)
        self.cnx.commit()
        cursor.close()
        # self.cnx.close()

    def insertTime(self, dates, id_bot):
        cursor = self.cnx.cursor()
        query = f"insert into get_balence (dates, crypto_name, crypto_wallet, id_bot, crypto_wallet_pourcentage, crypto_pourcentage)values ('{dates}','USDT/USDT',0,{id_bot},0,0);"
        cursor.execute(query)
        self.cnx.commit()
        cursor.close()

    def delete_user(self, user_name):
        cursor = self.cnx.cursor()
        query = """ DELETE FROM users WHERE username = ('%s')""" % (user_name)
        cursor.execute(query)
        self.cnx.commit()
        cursor.close()
        # self.cnx.close()

    def delete_bot(self, bot_id):
        cursor = self.cnx.cursor()
        query = """ DELETE FROM bots WHERE bot_id = ('%s')""" % (bot_id)
        cursor.execute(query)
        self.cnx.commit()
        cursor.close()
        # self.cnx.close()

    def insert_new_cocotier_bot(self, selection, bot_name, api_key, secret_key, sub_account,
                                pair_symbol, delta_hour, n_i):
        cursor = self.cnx.cursor()
        query = """Insert into bots (nom_bot,type_bot) values ('%s','%s')""" % (bot_name, selection)
        cursor.execute(query)
        idd = cursor.lastrowid
        self.cnx.commit()
        api_key, secret_key = generateApiSecret(api_key, secret_key, idd)
        query = """ INSERT INTO Params_bot_Cocotier (api_key, secret_key, sub_account, 
                pair_symbol, delta_hour, type_computing, bot_id)
                                   VALUES ('%s', '%s', '%s','%s', '%s', '%s', '%s') """ % (
            api_key, secret_key, sub_account, pair_symbol, delta_hour, n_i, idd)
        cursor.execute(query)
        self.cnx.commit()
        cursor.close()

    def insert_new_trix_bot(self, selection_bot, bot_name, user_mail,
                            api_key, secret_key, sub_account, pair_symbol,
                            trix_lenght, trix_signal, stoch_top, stoch_bottom, stoch_rsi):
        cursor = self.cnx.cursor()
        query = """Insert into bots (nom_bot,type_bot) values ('%s','%s')""" % (bot_name, selection_bot)
        cursor.execute(query)
        idd = cursor.lastrowid
        self.cnx.commit()
        api_key, secret_key = generateApiSecret(api_key, secret_key, idd)
        query = """ INSERT INTO params_bot_trix (api_key, secret_key, sub_account, 
        pair_symbol, trix_length, trix_signal, stoch_top, stoch_bottom, stoch_RSI ,bot_id)
                           VALUES ('%s', '%s', '%s','%s', '%s', '%s', '%s', '%s', '%s', '%s') """ % (
            api_key, secret_key, sub_account, pair_symbol, trix_lenght, trix_signal, stoch_top, stoch_bottom,
            stoch_rsi, idd)
        cursor.execute(query)
        self.cnx.commit()
        cursor.close()
        # self.cnx.close()

    def update_trix_bot(self, bot_id, api_key, secret_key, sub_account, pair_symbol,
                        trix_lenght, trix_signal, stoch_top, stoch_bottom, stoch_rsi):
        cursor = self.cnx.cursor()
        query = f'''update params_bot_trix set
                           api_key = '{api_key}',
                           secret_key = '{secret_key}',
                           sub_account = '{sub_account}',
                           pair_symbol = '{pair_symbol}',
                           trix_length = '{trix_lenght}',
                           trix_signal = '{trix_signal}',
                           stoch_top = '{stoch_top}',
                           stoch_bottom = '{stoch_bottom}',
                           stoch_RSI = '{stoch_rsi}' where bot_id = {bot_id} ;'''
        cursor.execute(query)
        self.cnx.commit()
        cursor.close()
        self.cnx.close()

    def update_Cocotier_bot(self, bot_id, api_key, secret_key, sub_account, pair_symbol,
                            delta_hour, n_i):
        cursor = self.cnx.cursor()
        query = f'''update Params_bot_Cocotier set
                           api_key = '{api_key}',
                           secret_key = '{secret_key}',
                           sub_account = '{sub_account}',
                           pair_symbol = '{pair_symbol}',
                           delta_hour = '{delta_hour}',
                           type_computing = '{n_i}'
                           where bot_id = {bot_id} ;'''
        cursor.execute(query)
        self.cnx.commit()
        cursor.close()
        self.cnx.close()

    def insert_balence(self, date, crypto_name, crypto_wallet, id_bot, status, transaction, notes):
        cursor = self.cnx.cursor()
        query = """Insert into get_balence (dates, crypto_name,crypto_wallet,id_bot,status_bot,transaction,notes) values ('%s','%s','%s','%s','%s','%s','%s')""" % (
            date, crypto_name, crypto_wallet, id_bot, status, transaction, notes)
        cursor.execute(query)
        self.cnx.commit()
        idd = cursor.lastrowid
        cursor.close()
        self.insert_balence_pourcentage(idd)
        self.insert_balence_crypto_pourcentage(idd)

    def insert_balence_pourcentage(self, idd):
        cursor = self.cnx.cursor()
        # recupére the last get_balence id
        # get the id_bot
        query = f"SELECT id_bot  FROM get_balence where id_get_balence={idd} ;"
        cursor.execute(query)
        bot_id = cursor.fetchall()[0][0]
        # get the max crypto_wallet
        query = f"SELECT max(crypto_wallet)  FROM get_balence where id_bot={bot_id} ;"
        cursor.execute(query)
        max = cursor.fetchall()[0][0]
        if (max == 0):
            max = 0.0001
        # add the crypto wallet pourcentage to the get_ballence
        query = f'''update get_balence set crypto_wallet_pourcentage = crypto_wallet/{max}
         where  id_get_balence = {idd};'''
        cursor.execute(query)
        self.cnx.commit()
        cursor.close()
        # self.cnx.close()

    def insert_balence_crypto_pourcentage(self, idd):
        cursor = self.cnx.cursor()
        query = f"SELECT id_bot  FROM get_balence where id_get_balence={idd} ;"
        cursor.execute(query)
        bot_id = cursor.fetchall()[0][0]
        query = f"SELECT crypto_wallet  FROM get_balence where id_bot= {bot_id} order by dates limit 1;"
        cursor.execute(query)
        max = cursor.fetchall()[0][0]
        if (max == 0):
            max = 0.0001
        query = f'''update get_balence set crypto_pourcentage = crypto_wallet/{max}
         where  id_get_balence = {idd};'''
        cursor.execute(query)
        self.cnx.commit()
        cursor.close()
        # self.cnx.close()

    def insert_log_info(self, date, pair_symbol, status_bot, transaction, bot_id):
        cursor = self.cnx.cursor()
        query = """Insert into log_execution (date, pair_symbol, status_bot, transaction, bot_id) values ('%s','%s','%s','%s','%s')""" % (
            date, pair_symbol, status_bot, transaction, bot_id)
        cursor.execute(query)
        self.cnx.commit()
        cursor.close()

    def get_info(self):
        cursor = self.cnx.cursor()
        query = " SELECT password  FROM users ;"
        cursor.execute(query)
        result = cursor.fetchall()
        # self.cnx.close()
        return result

    def nombreTrixActive(self):
        cursor = self.cnx.cursor()
        query = "select count(*) from bots where working = 1 and type_bot like upper('TRIX%') ;"
        cursor.execute(query)
        result = cursor.fetchall()
        return result

    def listeTrixActive(self):
        cursor = self.cnx.cursor()
        query = "select bot_id from bots where working = 1 and type_bot like upper('TRIX%') ;"
        cursor.execute(query)
        result = cursor.fetchall()
        return result

    def nombreTrixInActive(self):
        cursor = self.cnx.cursor()
        query = "select count(*) from bots where working = 0 and type_bot like upper('TRIX%') ;"
        cursor.execute(query)
        result = cursor.fetchall()
        return result

    def nombreCocotierActive(self):
        cursor = self.cnx.cursor()
        query = "select count(*) from bots where working = 1 and type_bot like upper('COCOTIER%') ;"
        cursor.execute(query)
        result = cursor.fetchall()
        return result

    def listeCocotierActive(self):
        cursor = self.cnx.cursor()
        query = "select bot_id from bots where working = 1 and type_bot like upper('COCOTIER%') ;"
        cursor.execute(query)
        result = cursor.fetchall()
        return result

    def nombreCocotierInActive(self):
        cursor = self.cnx.cursor()
        query = "select count(*) from bots where working = 0 and type_bot like upper('COCOTIER%') ;"
        cursor.execute(query)
        result = cursor.fetchall()
        return result

    def isONNorOFF(self, idd):
        cursor = self.cnx.cursor()
        query = f"select status_bot from get_balence where id_bot = {idd} order by dates desc limit 1;"
        cursor.execute(query)
        result = cursor.fetchall()
        return result

    def get_bots(self):
        cursor = self.cnx.cursor()
        query = " SELECT bot_id, nom_bot  FROM bots ;"
        cursor.execute(query)
        result = cursor.fetchall()
        # self.cnx.close()
        return result

    def get_botsCocotier(self):
        cursor = self.cnx.cursor()
        query = " SELECT bot_id, nom_bot,type_bot  FROM bots where type_bot like 'Cocotier%' ;"
        cursor.execute(query)
        result = cursor.fetchall()
        # self.cnx.close()
        return result

    def get_botsTrix(self):
        cursor = self.cnx.cursor()
        query = " SELECT bot_id, nom_bot,type_bot  FROM bots where type_bot like 'Trix%'  ;"
        cursor.execute(query)
        result = cursor.fetchall()
        # self.cnx.close()
        return result

    def get_trix_bot(self, bot_id):
        cursor = self.cnx.cursor()
        query = f"select params_bot_trix.*, bots.nom_bot from params_bot_trix , bots where bots.bot_id = params_bot_trix.bot_id and params_bot_trix.bot_id = {bot_id};"
        cursor.execute(query)
        result = cursor.fetchall()
        # self.cnx.close()
        return result

    def get_cocotier_bot(self, bot_id):
        cursor = self.cnx.cursor()
        query = f"select Params_bot_Cocotier.*, bots.nom_bot from Params_bot_Cocotier , bots where bots.bot_id = Params_bot_Cocotier.bot_id and Params_bot_Cocotier.bot_id = {bot_id};"
        cursor.execute(query)
        result = cursor.fetchall()
        # self.cnx.close()
        return result

    def get_trix_details_bot(self):
        cursor = self.cnx.cursor()
        query = f"select params_bot_trix.*, bots.nom_bot from params_bot_trix , bots where bots.bot_id = params_bot_trix.bot_id "
        cursor.execute(query)
        result = cursor.fetchall()
        # self.cnx.close()
        return result

    def get_cocotier_details_bot(self):
        cursor = self.cnx.cursor()
        query = f"select Params_bot_Cocotier.*, bots.nom_bot from Params_bot_Cocotier , bots where bots.bot_id = Params_bot_Cocotier.bot_id "
        cursor.execute(query)
        result = cursor.fetchall()
        # self.cnx.close()
        return result

    def update_cocotier_details_bot(self, id, api, secret):
        cursor = self.cnx.cursor()
        query = f"update Params_bot_Cocotier set api_key = '{api}', secret_key = '{secret}' where bot_id = {id};"
        cursor.execute(query)
        self.cnx.commit()
        cursor.close()

    def update_trix_details_bot(self, id, api, secret):
        cursor = self.cnx.cursor()
        query = f"update params_bot_trix set api_key = '{api}', secret_key = '{secret}' where bot_id = {id};"
        cursor.execute(query)
        self.cnx.commit()
        cursor.close()

    def get_type_bot(self, bot_id):
        cursor = self.cnx.cursor()
        query = f"select type_bot from bots where bot_id={bot_id};"
        cursor.execute(query)
        result = cursor.fetchall()
        # self.cnx.close()
        return result

    def get_balences(self):
        cursor = self.cnx.cursor()
        query = "select dates, crypto_wallet,nom_bot from get_balence, bots where (get_balence.id_bot = bots.bot_id);"
        cursor.execute(query)
        myresult = cursor.fetchall()
        return myresult

    def get_balencesCocotier(self):
        cursor = self.cnx.cursor()
        query = "select dates, crypto_wallet,nom_bot from get_balence, bots where get_balence.id_bot = bots.bot_id and type_bot like 'Cocotier%';"
        cursor.execute(query)
        myresult = cursor.fetchall()
        return myresult

    def get_balencesTrix(self):
        cursor = self.cnx.cursor()
        query = "select dates, crypto_wallet,nom_bot from get_balence, bots where get_balence.id_bot = bots.bot_id and type_bot like 'Trix%';"
        cursor.execute(query)
        myresult = cursor.fetchall()
        return myresult

    def get_balences_Normalization(self):
        cursor = self.cnx.cursor()
        query = "select dates, crypto_wallet_pourcentage,nom_bot from get_balence, bots where (get_balence.id_bot = bots.bot_id);"
        cursor.execute(query)
        myresult = cursor.fetchall()
        return myresult

    def get_crypto_pourcentage(self):
        cursor = self.cnx.cursor()
        query = "select dates, crypto_pourcentage,nom_bot from get_balence, bots where (get_balence.id_bot = bots.bot_id and bots.type_bot like 'Trix %');"
        cursor.execute(query)
        myresult = cursor.fetchall()
        return myresult

    def get_maintenance_setting(self):
        cursor = self.cnx.cursor()
        query = "select value_setting_boolean from settings where name_setting='maintenance';"
        cursor.execute(query)
        myresult = cursor.fetchall()
        return myresult

    def update_maintenance_setting(self):
        cursor = self.cnx.cursor()
        query = "update settings set value_setting_boolean = not value_setting_boolean where name_setting = 'maintenance';"
        cursor.execute(query)
        self.cnx.commit()
        cursor.close()
        # self.cnx.close()

    def bot_statusTrix(self, pairSymbol, side, id_bot):
        """
           insert status bot data to the database
        """
        try:
            self.insert_log_info(datetime.now(), pairSymbol, "ONN", side, id_bot)
        except BaseException as ex:
            ex_type, ex_value, ex_traceback = sys.exc_info()
            self.insert_log_info(datetime.now(), pairSymbol, "ex_value", side, id_bot)

    def bot_statusCocotier(self, pairSymbol, side, id_bot):
        """
           insert status bot data to the database
        """
        try:
            self.insert_log_info(datetime.now(), pairSymbol, "ONN", side, id_bot)
        except BaseException as ex:
            ex_type, ex_value, ex_traceback = sys.exc_info()
            self.insert_log_info(datetime.now(), pairSymbol, "ex_value", side, id_bot)

    def get_statusTrix(self):
        """
           get bots status information from bdd
        """
        cursor = self.cnx.cursor()
        # query = "select * from log_execution;"
        query = "select g.dates,g.crypto_wallet,g.status_bot,g.transaction,b.nom_bot,b.type_bot,p.pair_symbol,g.notes from get_balence as g, bots as b, params_bot_trix as p where p.bot_id = g.id_bot and g.id_bot = b.bot_id;"
        cursor.execute(query)
        result = cursor.fetchall()
        wallets = {}
        # self.cnx.close()
        return result

    def get_last_status_trix(self, id_bot):
        cursor = self.cnx.cursor()
        query = f"select transaction, dates from get_balence where id_bot = {id_bot} order by  dates desc limit 1;"
        cursor.execute(query)
        result = cursor.fetchall()
        return result[0]

    def get_statusTrixById(self, idBot):
        """
           get bots status information from bdd
        """
        cursor = self.cnx.cursor()
        # query = "select * from log_execution;"
        query = f"select g.dates,g.crypto_wallet,g.status_bot,g.transaction,b.nom_bot,b.type_bot,p.pair_symbol from get_balence as g, bots as b, params_bot_trix as p where p.bot_id = g.id_bot and g.id_bot = b.bot_id and b.bot_id = {idBot};"
        cursor.execute(query)
        result = cursor.fetchall()
        wallets = {}
        # self.cnx.close()
        return result

    def get_statusCocotierById(self, idBot):
        """
           get bots status information from bdd
        """
        cursor = self.cnx.cursor()
        # query = "select * from log_execution;"
        query = f"select g.dates,g.crypto_wallet,g.status_bot,b.nom_bot,b.type_bot,p.pair_symbol,g.crypto_name,p.delta_hour,p.type_computing from get_balence as g, bots as b, Params_bot_Cocotier as p where p.bot_id = g.id_bot and g.id_bot = b.bot_id and b.bot_id = {idBot} order by g.dates desc limit 1;"
        cursor.execute(query)
        result = cursor.fetchone()
        wallets = {}
        # self.cnx.close()
        return result

    def status_bots(self, df_result):
        # df_result = df_result[df_result["transaction"] != "none"]
        list_satus_bot = [df_result[df_result['nom_bot'] == bot].iloc[-1:] for bot in df_result['nom_bot'].unique()]
        df_status_bot = pd.concat(list_satus_bot)[
            ['date', 'nom_bot', 'pair_symbol', 'status_bot', 'transaction', 'type_bot', 'wallet']]
        for i, transaction in zip(df_status_bot["transaction"].index, df_status_bot["transaction"]):
            if transaction == "none":
                df_status_bot["transaction"].loc[i] = "USDT"
            else:
                df_status_bot["transaction"].loc[i] = transaction
            if transaction == "sell":
                df_status_bot["pair_symbol"].loc[i] = "USDT"
        # df_status_bot = df_status_bot.rename(columns={"transaction": "status_trix"})
        # df_status_bot = df_status_bot.rename(columns={"type_bot": "exchange"})
        return df_status_bot["pair_symbol"].iloc[0]

    def get_state_OFF_ONN_Cocotier_By_id(self, idbot):
        cursor = self.cnx.cursor()
        # query = "select * from log_execution;"
        query = f"select g.status_bot, g.id_get_balence from get_balence as g where g.id_bot = {idbot} order by id_get_balence desc limit  1;"
        cursor.execute(query)
        result = cursor.fetchone()
        wallets = {}
        # self.cnx.close()
        return result[0]

    def get_state_vente_achat_trix_By_id(self, idbot):
        result = self.get_statusTrixById(idbot)
        df_result = pd.DataFrame(result, columns=['date', 'wallet', 'status_bot',
                                                  'transaction', 'nom_bot', 'type_bot', 'pair_symbol'])
        df_result['type_bot'] = df_result['type_bot'].str[5:]

        return self.status_bots(df_result)

    def vendreTrixFtx(self, idbot):
        exchangeWallet = ccxt.binance()
        cursor = self.cnx.cursor()
        query = f"select params_bot_trix.* from params_bot_trix where  params_bot_trix.bot_id  ={idbot};"
        cursor.execute(query)
        result = cursor.fetchone()
        apiKey = result[1]
        secret = result[2]
        apiKey, secret = degenerateApiSecret(apiKey, secret, idbot)
        cryptoSymbol = (result[4] + "").upper()
        pairSymbol = cryptoSymbol + '/USD'
        fiatSymbol = 'USD'
        pairsSymbol = cryptoSymbol + '/USDT'
        client = ftx.FtxClient(
            api_key=apiKey,
            api_secret=secret,
            subaccount_name=result[3]
        )
        myTruncate = 3
        cryptoAmount = getBalance(client, cryptoSymbol)
        sellOrder = client.place_order(
            market=pairSymbol,
            side="sell",
            price=None,
            size=truncate(cryptoAmount, myTruncate),
            type='market')
        fiatAmount = getBalance(client, fiatSymbol)
        cryptoAmount = getBalance(client, cryptoSymbol)
        ticker = exchangeWallet.fetch_ticker(pairsSymbol)
        crypto_wallet_value = fiatAmount + (cryptoAmount * ticker['last'])
        cursor = self.cnx.cursor()
        query = f"select dates,id_get_balence from get_balence where id_bot ={idbot} order by dates desc limit 1;"
        cursor.execute(query)
        result = cursor.fetchall()[0]
        lastDate = datetime.strptime(str(result[0]), '%Y-%m-%d %H:%M:%S')
        self.insert_balence(lastDate,
                            f"Trix : {result[4]}_len{result[5]}_sign{result[6]}_top{result[7]}_bottom{result[8]}_RSI{result[9]}",
                            crypto_wallet_value, result[10], "OFF", "sell", "No Problem")

    def vendreTrixBinance(self, idbot):
        exchangeWallet = ccxt.binance()
        cursor = self.cnx.cursor()
        query = f"select params_bot_trix.* from params_bot_trix where  params_bot_trix.bot_id  ={idbot};"
        cursor.execute(query)
        result = cursor.fetchone()
        apiKey = result[1]
        secret = result[2]
        apiKey, secret = degenerateApiSecret(apiKey, secret, idbot)
        decimal_count = 8
        fiatSymbol = 'USDT'
        cryptoSymbol = (result[4] + "").upper()
        pairSymbol = cryptoSymbol + 'USDT'
        pairsSymbol = cryptoSymbol + '/USDT'
        client = Client(api_key=apiKey, api_secret=secret)
        cryptoAmount = float(client.get_asset_balance(asset=cryptoSymbol)['free'])
        sellOrder = client.order_market_sell(
            symbol=pairSymbol,
            quantity=f"{float(convert_amount_to_precision(client, pairSymbol, cryptoAmount)):.{decimal_count}f}")
        fiatAmount = float(client.get_asset_balance(asset=fiatSymbol)['free'])
        cryptoAmount = float(client.get_asset_balance(asset=cryptoSymbol)['free'])
        ticker = exchangeWallet.fetch_ticker(pairsSymbol)
        crypto_wallet_value = fiatAmount + (cryptoAmount * ticker['last'])
        cursor = self.cnx.cursor()
        query = f"select dates,id_get_balence from get_balence where id_bot ={idbot} order by dates desc limit 1;"
        cursor.execute(query)
        result = cursor.fetchall()[0]
        lastDate = datetime.strptime(str(result[0]), '%Y-%m-%d %H:%M:%S')
        self.insert_balence(lastDate,
                            f"Trix Binance: ",
                            crypto_wallet_value, idbot, "OFF", "sell", "No Problem")

    def vendreTrixBybit(self, idbot):
        exchangeWallet = ccxt.binance()
        cursor = self.cnx.cursor()
        query = f"select params_bot_trix.* from params_bot_trix where  params_bot_trix.bot_id  ={idbot};"
        cursor.execute(query)
        result = cursor.fetchone()
        apiKey = result[1]
        secret = result[2]
        apiKey, secret = degenerateApiSecret(apiKey, secret, idbot)
        fiatSymbol = 'USDT'
        cryptoSymbol = (result[4] + "").upper()
        pairSymbol = cryptoSymbol + 'USDT'
        pairsSymbol = cryptoSymbol + '/USDT'
        client = ccxt.bybit({
            'apiKey': apiKey,
            'secret': secret,
            'password': result[3],
            'enableRateLimit': True
        })
        montant = client.fetch_spot_balance()['total'][pairSymbol[:-4]]
        sellOrder = client.create_spot_order(pairsSymbol, "market", "sell", montant, 1)
        fiatAmount = float(client.fetch_spot_balance()['total']['USDT'])
        cryptoAmount = float(client.fetch_spot_balance()['total'][pairSymbol[:-4]])
        ticker = exchangeWallet.fetch_ticker(pairsSymbol)
        crypto_wallet_value = fiatAmount + (cryptoAmount * ticker['last'])
        cursor = self.cnx.cursor()
        query = f"select dates,id_get_balence from get_balence where id_bot ={idbot} order by dates desc limit 1;"
        cursor.execute(query)
        result = cursor.fetchall()[0]
        lastDate = datetime.strptime(str(result[0]), '%Y-%m-%d %H:%M:%S')
        self.insert_balence(lastDate,
                            f"Trix Bybit :",
                            crypto_wallet_value, idbot, "OFF", "sell", "No Problem")

    def vendreCocotierBinance(self, idbot):
        cursor = self.cnx.cursor()
        query = f"select * from Params_bot_Cocotier where bot_id  ={idbot};"
        cursor.execute(query)
        result = cursor.fetchone()
        apiKey = result[1]
        secret = result[2]
        market = result[4].split(',')
        apiKey, secret = degenerateApiSecret(apiKey, secret, idbot)
        exchange = ccxt.binance({
            'apiKey': apiKey,
            'secret': secret,
            'enableRateLimit': True
        })
        balence = exchange.fetchBalance()
        nom_crypto_vente = crypto_a_vendre(exchange, market)
        sell = vente(exchange, nom_crypto_vente, balence['total'])
        wallet = get_wallet(exchange)
        cursor = self.cnx.cursor()
        query = f"select dates,id_get_balence from get_balence where id_bot ={idbot} order by dates desc limit 1;"
        cursor.execute(query)
        result = cursor.fetchall()[0]
        lastDate = datetime.strptime(str(result[0]), '%Y-%m-%d %H:%M:%S')
        self.insert_balence(lastDate, "USDT", wallet, idbot, "OFF", "sell", "No Problem")

    def vendreCocotierBybit(self, idbot):
        cursor = self.cnx.cursor()
        query = f"select * from Params_bot_Cocotier where bot_id  ={idbot};"
        cursor.execute(query)
        result = cursor.fetchone()
        apiKey = result[1]
        secret = result[2]
        password = result[3]
        apiKey, secret = degenerateApiSecret(apiKey, secret, idbot)
        exchange = ccxt.bybit({
            'apiKey': apiKey,
            'secret': secret,
            'password': password,
            'enableRateLimit': True
        })
        nom_crypto_vente = crypto_a_vendreBybit(exchange, result[7])
        balence = exchange.fetch_spot_balance()
        sell = vente(exchange, nom_crypto_vente, balence['total'])
        wallet = get_walletBybit(exchange)
        cursor = self.cnx.cursor()
        query = f"select dates,id_get_balence from get_balence where id_bot ={idbot} order by dates desc limit 1;"
        cursor.execute(query)
        result = cursor.fetchall()[0]
        lastDate = datetime.strptime(str(result[0]), '%Y-%m-%d %H:%M:%S')
        self.insert_balence(lastDate, "USDT", wallet, idbot, "OFF", "sell", "No Problem")

    def get_statusCocotier(self):
        """
           get bots status information from bdd
        """
        cursor = self.cnx.cursor()
        # query = "select * from log_execution;"
        query = "select g.dates,g.crypto_wallet,g.status_bot,b.nom_bot,b.type_bot,p.pair_symbol,g.crypto_name,p.delta_hour,p.type_computing,g.notes from get_balence as g, bots as b, Params_bot_Cocotier as p where p.bot_id = g.id_bot and g.id_bot = b.bot_id;"
        cursor.execute(query)
        result = cursor.fetchall()
        # self.cnx.close()
        return result

    def getAllPairSymbolsBinance(self):
        cursor = self.cnx.cursor()
        query = "select value_setting from settings where id_setting = 2"
        cursor.execute(query)
        result = cursor.fetchall()
        return result

    def updatePairSymbolsBinance(self, pairSymbols):
        cursor = self.cnx.cursor()
        query = f"update settings set value_setting = '{pairSymbols}' where id_setting = 2;"
        cursor.execute(query)
        self.cnx.commit()

    def getAllPairSymbolsBybit(self):
        cursor = self.cnx.cursor()
        query = "select value_setting from settings where id_setting = 3"
        cursor.execute(query)
        result = cursor.fetchall()
        return result

    def updatePairSymbolsBybit(self, pairSymbols):
        cursor = self.cnx.cursor()
        query = f"update settings set value_setting = '{pairSymbols}' where id_setting = 3;"
        cursor.execute(query)
        self.cnx.commit()

    def getStopMarche(self, idbot):
        cursor = self.cnx.cursor()
        query = f"select working from bots where bot_id = {idbot}"
        cursor.execute(query)
        result = cursor.fetchall()
        return result[0][0]

    def previousOneHour(self, idBot):
        cursor = self.cnx.cursor()
        query = f"select dates,id_get_balence from get_balence where id_bot ={idBot} order by dates desc limit 1;"
        cursor.execute(query)
        result = cursor.fetchall()[0]
        lastDate = datetime.strptime(str(result[0]), '%Y-%m-%d %H:%M:%S') - timedelta(hours=5)
        query = f"update get_balence set dates = '{lastDate}' where id_get_balence = {str(result[1])};"
        cursor.execute(query)
        self.cnx.commit()

    def updateStopMarche(self, idbot, state):
        # if state == 1:
        #     self.previousOneHour(idbot)
        cursor = self.cnx.cursor()
        query = f"update bots set working = '{state}' where bot_id = {idbot};"
        cursor.execute(query)
        self.cnx.commit()


def convert_time(dataframe):
    temps = []
    for elm in dataframe['timestamp']:
        temps.append(datetime.fromtimestamp(elm / 1000))
    dataframe['timestamp'] = pd.DatetimeIndex(pd.to_datetime(temps)).tz_localize('UTC').tz_convert('UTC')
    return dataframe


def detection_mauvais_shape(dictionaire_crypto):
    liste_shape = []
    liste_crypto = []
    boulean = []
    for elm in dictionaire_crypto:
        liste_shape.append(dictionaire_crypto[elm].shape[0])
        liste_crypto.append(elm)
    for elm in liste_shape:
        if elm < np.max(liste_shape):
            boulean.append(True)
        else:
            boulean.append(False)
    boulean, liste_crypto = np.array(boulean), np.array(liste_crypto)
    return liste_crypto[boulean]


def correction_shape(dictionaire_crypto, array):
    max_shape = []
    shape_a_manque = []
    liste_final = []
    nom_shape_a_manque = []

    # onc cherche le shape maximun dans tous le array
    for elm in dictionaire_crypto:
        max_shape.append(dictionaire_crypto[elm].shape[0])
    max_shape = np.max(max_shape)

    # on calcul le shape manquant dans le array
    for elm1 in array:
        shape_a_manque.append(max_shape - dictionaire_crypto[elm1].shape[0])
        nom_shape_a_manque.append(elm1)
    for shape, nom in zip(shape_a_manque, nom_shape_a_manque):
        liste_final = [np.ones(shape), np.zeros(shape)]
        df_liste_final = pd.DataFrame(np.transpose(liste_final), columns=[nom[:3] + '_open', nom[:3] + '_close'])
        dictionaire_crypto[nom] = pd.concat((df_liste_final, dictionaire_crypto[nom]), axis=0)
    return dictionaire_crypto


def generation_date(dataframe, delta_pas):
    test_list = []
    pas = timedelta(hours=delta_pas)
    date_ini = dataframe.index[::-1][0]
    inverse_time = dataframe.index[::-1]
    for i in range(len(inverse_time)):
        test_list.append(date_ini - pas * i)
    test_list = test_list[::-1]
    return test_list


def to_timestamp(date):
    element = datetime.strptime(date, "%Y-%m-%d")
    timestamp = int(datetime.timestamp(element)) * 1000
    return timestamp


def choix_market():
    con = ConnectBbd('localhost', '3306', 'root', mot_de_passe, 'cryptos', 'mysql_native_password')
    new_title = f'<p style="font-family:sans-serif; font-size: 25px;">Pool Binance</p>'
    st.markdown(new_title, unsafe_allow_html=True)
    # liste_crypto = np.array(
    #     ['BTC/USDT', 'ETH/USDT', 'ADA/USDT', 'DOGE/USDT', 'BNB/USDT', 'UNI/USDT', 'SOL/USDT', 'KSM/USDT',
    #      'LTC/USDT', 'BCH/USDT', 'LINK/USDT', 'VET/USDT', 'XLM/USDT', 'FIL/USDT', 'TRX/USDT',
    #      'NEO/USDT', 'EOS/USDT', 'DOT/USDT', 'AAVE/USDT', 'MATIC/USDT', 'LUNA/USDT', 'THETA/USDT',
    #      'AXS/USDT', 'ENJ/USDT', 'SAND/USDT', 'WIN/USDT', 'SLP/USDT', 'XRP/USDT', 'EGLD/USDT', 'ATOM/USDT'])
    #
    # cols3 = st.columns(3)
    # btc = cols3[0].checkbox('BTC/USDT')
    # eth = cols3[0].checkbox('ETH/USDT')
    # ada = cols3[0].checkbox('ADA/USDT')
    # doge = cols3[0].checkbox('DOGE/USDT')
    # bnb = cols3[0].checkbox('BNB/USDT')
    # uni = cols3[1].checkbox('UNI/USDT')
    # bch = cols3[1].checkbox('BCH/USDT')
    # link = cols3[1].checkbox('LINK/USDT')
    # vet = cols3[1].checkbox('VET/USDT')
    # xlm = cols3[1].checkbox('XLM/USDT')
    # fil = cols3[2].checkbox('FIL/USDT')
    # ltc = cols3[2].checkbox('LTC/USDT')
    # trx = cols3[2].checkbox('TRX/USDT')
    # neo = cols3[2].checkbox('NEO/USDT')
    # eos = cols3[2].checkbox('EOS/USDT')
    # dot = cols3[2].checkbox('DOT/USDT')
    #
    # aave = cols3[0].checkbox('AAVE/USDT')
    # matic = cols3[1].checkbox('MATIC/USDT')
    # luna = cols3[0].checkbox('LUNA/USDT')
    # theta = cols3[1].checkbox('THETA/USDT')
    # sol = cols3[1].checkbox('SOL/USDT')
    # ksm = cols3[0].checkbox('KSM/USDT')
    #
    # axs = cols3[2].checkbox('AXS/USDT')
    # enj = cols3[2].checkbox('ENJ/USDT')
    # sand = cols3[0].checkbox('SAND/USDT')
    # win = cols3[1].checkbox('WIN/USDT')
    # slp = cols3[2].checkbox('SLP/USDT')
    # xrp = cols3[0].checkbox('XRP/USDT')
    #
    # egld = cols3[1].checkbox('EGLD/USDT')
    # atom = cols3[2].checkbox('ATOM/USDT')
    #
    # liste_boolean = np.array(
    #     [btc, eth, ada, doge, bnb, uni, sol, ksm, ltc, bch, link, vet, xlm, fil, trx, neo, eos, dot, aave, matic,
    #      luna,
    #      theta,
    #      axs, enj, sand, win, slp, xrp, egld, atom])
    #
    # return liste_crypto[liste_boolean]
    listacrypto = con.getAllPairSymbolsBinance()[0][0].split(',')
    liste_crypto = np.array(listacrypto)
    cols3 = st.columns(5)
    lista = [x for x in liste_crypto]
    for i in range(len(liste_crypto)):
        lista[i] = cols3[i % 5].checkbox(liste_crypto[i])
    liste_boolean = np.array(lista)
    return liste_crypto[liste_boolean]


def plot_courbes2(df_tableau_multi):
    fig = go.Figure()
    for elm in df_tableau_multi.columns:
        fig.add_trace(go.Scatter(x=df_tableau_multi[elm].index,
                                 y=df_tableau_multi[elm],
                                 mode='lines',
                                 name=elm,
                                 ))
    return st.plotly_chart(fig)


def variationN(cryptos, ni):
    ni = ni.upper()
    if (ni == 'N'):
        for crypto in cryptos:
            cryptos[crypto]["Variation_" + crypto[:-5]] = cryptos[crypto][crypto[:-5] + "_close"] / cryptos[crypto][
                crypto[:-5] + "_open"]
            cryptos[crypto]["Variation_N_" + crypto[:-5]] = cryptos[crypto][crypto[:-5] + "_close"] / cryptos[crypto][
                crypto[:-5] + "_open"]
    elif (ni == 'N-1'):
        for crypto in cryptos:
            cryptos[crypto]["Variation_N_" + crypto[:-5]] = cryptos[crypto][crypto[:-5] + "_close"] / cryptos[crypto][
                crypto[:-5] + "_open"]
            cryptos[crypto]["Variation_" + crypto[:-5]] = 0.0
            cryptos[crypto]["Variation_" + crypto[:-5]][0] = float(cryptos[crypto][crypto[:-5] + "_close"][0]) / float(
                cryptos[crypto][crypto[:-5] + "_open"][0])
            for j in range(1, len(cryptos[crypto])):
                cryptos[crypto]["Variation_" + crypto[:-5]][j] = cryptos[crypto][crypto[:-5] + "_close"][j] / \
                                                                 cryptos[crypto][crypto[:-5] + "_open"][j - 1]
    elif (ni == 'N-2'):
        for crypto in cryptos:
            cryptos[crypto]["Variation_N_" + crypto[:-5]] = cryptos[crypto][crypto[:-5] + "_close"] / cryptos[crypto][
                crypto[:-5] + "_open"]
            cryptos[crypto]["Variation_" + crypto[:-5]] = 0.0
            cryptos[crypto]["Variation_" + crypto[:-5]][0] = float(cryptos[crypto][crypto[:-5] + "_close"][0]) / float(
                cryptos[crypto][crypto[:-5] + "_open"][0])
            cryptos[crypto]["Variation_" + crypto[:-5]][1] = float(cryptos[crypto][crypto[:-5] + "_close"][1]) / float(
                cryptos[crypto][crypto[:-5] + "_open"][0])
            for j in range(2, len(cryptos[crypto])):
                cryptos[crypto]["Variation_" + crypto[:-5]][j] = cryptos[crypto][crypto[:-5] + "_close"][j] / \
                                                                 cryptos[crypto][crypto[:-5] + "_open"][j - 2]
    return (cryptos)


def coeffMulti(cryptos):
    for crypto in cryptos:
        for i in range(len(cryptos[crypto].index)):
            if (i == 0):
                cryptos[crypto]["Coeff_mult_" + crypto[:-5]] = cryptos[crypto][crypto[:-5] + "_close"][0] / \
                                                               cryptos[crypto][crypto[:-5] + "_open"][0]
            else:
                cryptos[crypto]["Coeff_mult_" + crypto[:-5]][i] = cryptos[crypto]["Variation_N_" + crypto[:-5]][i] * \
                                                                  cryptos[crypto]["Coeff_mult_" + crypto[:-5]][i - 1]
                # print(cryptos[crypto]["Variation_N_" + crypto[:-5]][i]," * ",  cryptos[crypto]["Coeff_mult_" + crypto[:-5]][i - 1] ," = ",cryptos[crypto]["Coeff_mult_" + crypto[:-5]][i] )

    return cryptos


def mergeCryptoTogether(cryptos):
    for i in cryptos:
        cryptos["BOT_MAX"] = cryptos[i].copy()
        cryptos["BOT_MAX"].rename(columns={"Variation_" + i[:-5]: "Variation_BOTMAX"}, inplace=True)
        cryptos["BOT_MAX"].rename(columns={i[:-5] + "_close": "Variation2BOTMAX"}, inplace=True)
        cryptos["BOT_MAX"].rename(columns={"Coeff_mult_" + i[:-5]: "Coeff_mult_BOTMAX"}, inplace=True)
        cryptos["BOT_MAX"].rename(columns={"Variation_N_" + i[:-5]: "Variation_BOTMAX_N"}, inplace=True)
        break
    cryptos = pd.concat(cryptos, axis=1)
    return cryptos


def botMax(cryptos):
    maxis = []
    for i in range(len(cryptos)):
        v = []
        k = 0
        for j in range(len(cryptos.iloc[i])):
            if (k == 3):
                v.append(cryptos.iloc[i].iloc[j])
            elif (k == 4):
                k = -1
            k += 1
        maxx = max(v)
        maxis.append(v.index(maxx))
        cryptos["BOT_MAX"]["Variation_BOTMAX"][i] = maxx
    return cryptos, maxis


def botMaxVariation2(cryptos, maxis):
    botNames = []
    for crypto in cryptos:
        if (crypto[0] not in botNames):
            botNames.append(crypto[0])
    for i in range(len(cryptos)):
        botName = botNames[maxis[i]]
        cryptos["BOT_MAX"]["Variation_BOTMAX_N"][i] = cryptos[botName]["Variation_N_" + botName[:-5]][i]
    for i in range(0, len(cryptos) - 1):
        botName = botNames[maxis[i]]
        cryptos["BOT_MAX"]["Variation2BOTMAX"][i + 1] = cryptos[botName]["Variation_N_" + botName[:-5]][i + 1]
    cryptos["BOT_MAX"]["Variation2BOTMAX"][0] = 0

    return cryptos


def coeffMultiBotMax(cryptos):
    cryptos["BOT_MAX"]["Coeff_mult_BOTMAX"][0] = 1.000
    for i in range(1, len(cryptos)):
        cryptos["BOT_MAX"]["Coeff_mult_BOTMAX"][i] = cryptos["BOT_MAX"]["Coeff_mult_BOTMAX"][i - 1] * \
                                                     cryptos["BOT_MAX"]["Variation2BOTMAX"][i]
    return cryptos


def coefmultiFinal(cryptos):
    tabe = {}
    for crypto in cryptos:
        if (crypto[1].find("Coeff_mult_") == 0):
            tabe[crypto[1]] = cryptos[crypto]

    tabe = pd.DataFrame(tabe)
    return tabe


def VariationFinal(cryptos):
    tabe = {}
    for crypto in cryptos:
        if (crypto[1].find("Variation") == 0):
            tabe[crypto[1]] = cryptos[crypto]

    tabe = pd.DataFrame(tabe)
    return tabe


'''
Process ! 
After submitting
get the inserted row
updated it how ?!
cypher encoding with the key of the id for both api and secret
then the api = api+secret
and the secret = secret + api + secret

for the decrypting
secret = secret - api
api = api - secret
decrypting with cypher
'''


def encypt_func(txt, s):
    result = ""
    for i in range(len(txt)):
        char = txt[i]
        if (char in upperCase):
            result += chr((ord(char) + s - 64) % 26 + 65)
        elif (char in lowerCase):
            result += chr((ord(char) + s - 96) % 26 + 97)
        else:
            result += chr((ord(char) - 3))
    return result


def decypt_func(mesage, key):
    decrypted_message = ""

    for c in mesage:
        if c in lowerCase:
            position = lowerCase.find(c)
            new_position = (position - key - 1) % 26
            new_character = lowerCase[new_position]
            decrypted_message += new_character
        elif c in upperCase:
            position = upperCase.find(c)
            new_position = (position - key - 1) % 26
            new_character = upperCase[new_position]
            decrypted_message += new_character
        else:
            decrypted_message += chr(ord(c) + 3)
    return decrypted_message


def generateApiSecret(api, secret, key):
    api = encypt_func(api, key)
    secret = encypt_func(secret, key)
    api = api + secret
    secret = secret + api
    return api, secret


def degenerateApiSecret(api, secret, key):
    secret = secret[:secret.rfind(api)]
    api = api[:api.rfind(secret)]
    api = decypt_func(api, key)
    secret = decypt_func(secret, key)
    return api, secret


def truncate(n, decimals):
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


def get_step_size(client, symbol):
    stepSize = None
    for filter in client.get_symbol_info(symbol)['filters']:
        if filter['filterType'] == 'LOT_SIZE':
            stepSize = float(filter['stepSize'])
    return stepSize


def convert_amount_to_precision(client, symbol, amount):
    stepSize = get_step_size(client, symbol)
    return (amount // stepSize) * stepSize


def vente(exchange, var1, balence_total):
    sell_1 = exchange.create_market_sell_order(var1, balence_total[var1[:-5]])
    return sell_1


def get_wallet(exchange):
    balence = exchange.fetch_balance()['total']
    usdtt = balence['USDT']
    df_balence = pd.DataFrame([balence]).transpose().rename(columns={0: "balence"})
    df_balence = df_balence[df_balence['balence'] > 0]
    crypto_index = [elm + "/USDT" for elm in df_balence['balence'].index]
    crypto_index.remove('USDT/USDT')
    dict_balence_usdt = {}
    for elm in crypto_index:
        try:
            dict_balence_usdt[elm] = exchange.fetchTickers([elm])[elm]['ask'] * exchange.fetch_balance()['total'][
                elm[:-5]]
        except Exception as e:
            print(e)
    return sum(dict_balence_usdt.values()) + usdtt


def get_walletBybit(exchange):
    balence = exchange.fetch_spot_balance()['total']
    usdtt = balence['USDT']
    df_balence = pd.DataFrame([balence]).transpose().rename(columns={0: "balence"})
    df_balence = df_balence[df_balence['balence'] > 0]
    crypto_index = [elm + "/USDT:USDT" for elm in df_balence['balence'].index]
    crypto_index.remove('USDT/USDT:USDT')
    dict_balence_usdt = {}
    for elm in crypto_index:
        try:
            dict_balence_usdt[elm] = exchange.fetchTickers([elm])[elm]['ask'] * exchange.fetch_spot_balance()['total'][
                elm[:-10]]
        except Exception as e:
            print(e)
    return sum(dict_balence_usdt.values()) + usdtt


def acheter_2(exchange, var2, balence_total, pourcentage):
    montant_USDT = float(exchange.fetch_balance().get('USDT').get('free'))
    dict = exchange.fetchTicker(var2)
    last = dict['last']
    # Prevent error divide by zero
    while last == 0:
        try:
            last = exchange.fetchTicker(var2)['last']
        except:
            pass
    buy = exchange.create_market_buy_order(var2, (montant_USDT * pourcentage) / last)
    return buy


def last_crypto_buyed(exchange, market1):
    for elm in market1:
        etat = pd.DataFrame.from_dict(exchange.fetchMyTrades(elm)).iloc[-1:]
        try:
            if etat['side'].values[0] == 'buy':
                crypto_a_vendre = etat['symbol']
                return crypto_a_vendre.values[0]
        except KeyError:
            pass


def isEmptyDict(di):
    for i in di:
        if not (di[i].empty):
            return False
    return True


def crypto_a_vendre(exchange, market):
    try:
        x = (datetime.now() - timedelta(days=365)).timestamp() * 1000
        df_hystoric_order = {}
        liste_df = []
        liste_name_crypto = []
        for name_crypto in market:
            name_crypto_up = name_crypto.upper()
            timing = 0
            while True:
                try:
                    x = exchange.fetchMyTrades(name_crypto)
                    break
                except:
                    timing += 1
                    print("ERROR CONNEXTION RECUPERATION fetchmyTrades Crypto: ", name_crypto)
                    if (timing == 5):
                        break
            df_hystoric_order[name_crypto_up] = pd.DataFrame.from_dict(x)
            index_dernier_ordre = df_hystoric_order[name_crypto_up].index.max()
            if not (df_hystoric_order[name_crypto_up].empty):
                liste_df.append(df_hystoric_order[name_crypto_up].loc[index_dernier_ordre])
            elif isEmptyDict(df_hystoric_order):
                var1 = name_crypto
                montant_USDT = float(exchange.fetch_balance().get('USDT').get('free'))
                # exchange.create_spot_order(var1,"market","buy",montant_USDT,1)
                dict = exchange.fetchTicker(var1)
                last = dict['last']
                while last == 0:
                    try:
                        last = exchange.fetchTicker(var1)['last']
                    except:
                        pass
                try:
                    exchange.create_market_buy_order(var1, (montant_USDT) / last)
                except:
                    # you need to sell all your credit and buy new ones
                    pass
                x = exchange.fetchMyTrades(name_crypto)
                df_hystoric_order[name_crypto_up] = pd.DataFrame.from_dict(x)
                index_dernier_ordre = df_hystoric_order[name_crypto_up].index.max()
                liste_df.append(df_hystoric_order[name_crypto_up].loc[index_dernier_ordre])
        pd.set_option('display.max_columns', None)
        df_log = pd.DataFrame(liste_df).set_index('symbol')
        df_datetime_side_cost = df_log[['datetime', 'side', 'cost']]
        global crypto_a_vendre
        try:
            balence = exchange.fetchBalance()
            crypto_a_vendre = df_log[df_log['side'] == 'buy'].index[0]
        except IndexError as e:
            print(f"# Warning  : {e} we buy BTC by default")
            acheter_2(exchange, "BTC/USDT", balence['total'], 0.97)
            cryptos_a_vendre = "BTC/USDT"
        return crypto_a_vendre
    except IndexError:
        return '0'


def findUsedCrypto(exchange):
    lista = []
    a = exchange.fetch_balance()['total']
    for i in a:
        if a[i] != 0 and i != 'USDT':
            try :
                lista.append((i, a[i] * exchange.fetchTickers([i + "/USDT"])[i + "/USDT"]['ask']))
            except:
                pass
    return lista


def findCurrentCrypto(exchange):
    lista = findUsedCrypto(exchange)
    max = lista[0]
    for i in lista:
        if i[1] > max[1]:
            max = i
    maxi = max[0]
    if (maxi == "USDT"):
        montant_USDT = float(exchange.fetch_balance().get('USDT').get('free'))
        dict = exchange.fetchTicker("BTC/USDT")
        last = dict['last']
        exchange.create_market_buy_order("BTC/USDT", (montant_USDT) / last)
        maxi = "BTC/USDT"
    return maxi


def get_pair_symbol_for_last_balence_by_id(id):
    con = ConnectBbd('localhost', '3306', 'root', mot_de_passe, 'cryptos', 'mysql_native_password')
    cursor = con.cnx.cursor()
    query = f"select crypto_name from get_balence where id_bot = {id} order by id_get_balence desc limit 1;"
    cursor.execute(query)
    myresult = cursor.fetchall()
    return myresult


def crypto_a_vendreBybit(exchange, idbot):
    try:
        crypto_name = get_pair_symbol_for_last_balence_by_id(idbot)[0][0]
    except Exception as exx:
        crypto_name = "BTC/USDT"
        print("We'll buy btc for now just for the start !")
        montant_USDT = float(exchange.fetch_spot_balance().get('USDT').get('free'))
        exchange.create_spot_order("BTC/USDT", "market", "buy", montant_USDT, 1)
    return crypto_name
