import mysql.connector
import sys
import numpy as np
import pandas as pd
from datetime import datetime
from datetime import timedelta
import streamlit as st
import plotly.graph_objects as go

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

    def insertTime(self,dates,id_bot):
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

    def insert_new_cocotier_bot(self,selection ,bot_name, api_key, secret_key, sub_account,
                                pair_symbol, delta_hour, n_i):
        cursor = self.cnx.cursor()
        query = """Insert into bots (nom_bot,type_bot) values ('%s','%s')""" % (bot_name,selection)
        cursor.execute(query)
        idd = cursor.lastrowid
        self.cnx.commit()

        query = """ INSERT INTO Params_bot_Cocotier (api_key, secret_key, sub_account, 
                pair_symbol, delta_hour, type_computing, bot_id)
                                   VALUES ('%s', '%s', '%s','%s', '%s', '%s', '%s') """ % (
            api_key, secret_key, sub_account, pair_symbol, delta_hour, n_i,idd)
        cursor.execute(query)
        self.cnx.commit()
        cursor.close()

    def insert_new_trix_bot(self, selection_bot, bot_name, user_mail,
                            api_key, secret_key, sub_account, pair_symbol,
                            trix_lenght, trix_signal, stoch_top, stoch_bottom, stoch_rsi):
        cursor = self.cnx.cursor()
        query = """Insert into bots (nom_bot,type_bot) values ('%s','%s')""" % (bot_name,selection_bot)
        cursor.execute(query)
        idd = cursor.lastrowid
        self.cnx.commit()

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

    def insert_balence(self, date, crypto_name, crypto_wallet, id_bot,status,transaction):
        cursor = self.cnx.cursor()
        query = """Insert into get_balence (dates, crypto_name,crypto_wallet,id_bot,status_bot,transaction) values ('%s','%s','%s','%s','%s','%s')""" % (
            date, crypto_name, crypto_wallet, id_bot,status,transaction)
        cursor.execute(query)
        self.cnx.commit()
        idd = cursor.lastrowid
        cursor.close()
        self.insert_balence_pourcentage(idd)
        self.insert_balence_crypto_pourcentage(idd)


    def insert_balence_pourcentage(self, idd):
        cursor = self.cnx.cursor()
        # recupére the last get_balence id
        print("idd : ", idd)
        # get the id_bot
        query = f"SELECT id_bot  FROM get_balence where id_get_balence={idd} ;"
        cursor.execute(query)
        bot_id = cursor.fetchall()[0][0]
        print("bot_id : ", bot_id)
        # get the max crypto_wallet
        query = f"SELECT max(crypto_wallet)  FROM get_balence where id_bot={bot_id} ;"
        cursor.execute(query)
        max = cursor.fetchall()[0][0]
        print("max : ", max);
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

    def get_bots(self):
        cursor = self.cnx.cursor()
        query = " SELECT bot_id, nom_bot  FROM bots ;"
        cursor.execute(query)
        result = cursor.fetchall()
        # self.cnx.close()
        return result


    def get_botsCocotier(self):
        cursor = self.cnx.cursor()
        query = " SELECT bot_id, nom_bot  FROM bots where type_bot like 'Cocotier%' ;"
        cursor.execute(query)
        result = cursor.fetchall()
        # self.cnx.close()
        return result


    def get_botsTrix(self):
        cursor = self.cnx.cursor()
        query = " SELECT bot_id, nom_bot  FROM bots where type_bot like 'Trix%'  ;"
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
        query = "select g.dates,g.crypto_wallet,g.status_bot,g.transaction,b.nom_bot,b.type_bot,p.pair_symbol from get_balence as g, bots as b, params_bot_trix as p where p.bot_id = g.id_bot and g.id_bot = b.bot_id;"
        cursor.execute(query)
        result = cursor.fetchall()
        wallets = {}
        # self.cnx.close()
        return result

    def get_statusCocotier(self):
        """
           get bots status information from bdd
        """
        cursor = self.cnx.cursor()
        # query = "select * from log_execution;"
        query = "select g.dates,g.crypto_wallet,g.status_bot,b.nom_bot,b.type_bot,p.pair_symbol,g.crypto_name,p.delta_hour,p.type_computing from get_balence as g, bots as b, Params_bot_Cocotier as p where p.bot_id = g.id_bot and g.id_bot = b.bot_id;"
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
    liste_crypto = np.array(
        ['BTC/USDT', 'ETH/USDT', 'ADA/USDT', 'DOGE/USDT', 'BNB/USDT', 'UNI/USDT', 'SOL/USDT', 'KSM/USDT',
         'LTC/USDT', 'BCH/USDT', 'LINK/USDT', 'VET/USDT', 'XLM/USDT', 'FIL/USDT', 'TRX/USDT',
         'NEO/USDT', 'EOS/USDT', 'DOT/USDT', 'AAVE/USDT', 'MATIC/USDT', 'LUNA/USDT', 'THETA/USDT',
         'AXS/USDT', 'ENJ/USDT', 'SAND/USDT', 'WIN/USDT', 'SLP/USDT', 'XRP/USDT', 'EGLD/USDT', 'ATOM/USDT'])

    cols3 = st.columns(3)
    btc = cols3[0].checkbox('BTC/USDT')
    eth = cols3[0].checkbox('ETH/USDT')
    ada = cols3[0].checkbox('ADA/USDT')
    doge = cols3[0].checkbox('DOGE/USDT')
    bnb = cols3[0].checkbox('BNB/USDT')
    uni = cols3[1].checkbox('UNI/USDT')
    bch = cols3[1].checkbox('BCH/USDT')
    link = cols3[1].checkbox('LINK/USDT')
    vet = cols3[1].checkbox('VET/USDT')
    xlm = cols3[1].checkbox('XLM/USDT')
    fil = cols3[2].checkbox('FIL/USDT')
    ltc = cols3[2].checkbox('LTC/USDT')
    trx = cols3[2].checkbox('TRX/USDT')
    neo = cols3[2].checkbox('NEO/USDT')
    eos = cols3[2].checkbox('EOS/USDT')
    dot = cols3[2].checkbox('DOT/USDT')

    aave = cols3[0].checkbox('AAVE/USDT')
    matic = cols3[1].checkbox('MATIC/USDT')
    luna = cols3[0].checkbox('LUNA/USDT')
    theta = cols3[1].checkbox('THETA/USDT')
    sol = cols3[1].checkbox('SOL/USDT')
    ksm = cols3[0].checkbox('KSM/USDT')

    axs = cols3[2].checkbox('AXS/USDT')
    enj = cols3[2].checkbox('ENJ/USDT')
    sand = cols3[0].checkbox('SAND/USDT')
    win = cols3[1].checkbox('WIN/USDT')
    slp = cols3[2].checkbox('SLP/USDT')
    xrp = cols3[0].checkbox('XRP/USDT')

    egld = cols3[1].checkbox('EGLD/USDT')
    atom = cols3[2].checkbox('ATOM/USDT')

    liste_boolean = np.array(
        [btc, eth, ada, doge, bnb, uni, sol, ksm, ltc, bch, link, vet, xlm, fil, trx, neo, eos, dot, aave, matic,
         luna,
         theta,
         axs, enj, sand, win, slp, xrp, egld, atom])

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
            cryptos[crypto]["Variation_" + crypto[:-5]][0] = float(cryptos[crypto][crypto[:-5] + "_close"][0]) /float(cryptos[crypto][crypto[:-5] + "_open"][0])
            for j in range(1,len(cryptos[crypto])):
                cryptos[crypto]["Variation_" + crypto[:-5]][j] = cryptos[crypto][crypto[:-5] + "_close"][j] / cryptos[crypto][crypto[:-5] + "_open"][j-1]
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
