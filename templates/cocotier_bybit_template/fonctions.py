# -*- coding: utf-8 -*-
import plotly.graph_objects as go
from datetime import datetime
from time import time
from datetime import timedelta
import numpy as np
import pandas as pd
from pass_secret import mot_de_passe
import time as tm
import mysql.connector
from bdd_communication import *


# Calcul  de la variation
# ENtRE => dataframe   exemple crypto['eth/usdt']
# SORTIE =>  pandas.core.series.Series
def variation(dataframe):
    open_ = dataframe[dataframe.columns[0]]
    close = dataframe[dataframe.columns[1]]
    serie_variation = ((close) / open_)

    df_serie_variation = pd.DataFrame(serie_variation, dataframe.index, columns=[dataframe.columns[0][:3] + '_var'])
    return df_serie_variation


def variation_computing(dataframe, type_computing):
    open_ = dataframe[dataframe.columns[0]]
    close = dataframe[dataframe.columns[1]]

    df_cumputing = pd.DataFrame([
        [dataframe.index[-1] - dataframe.index[-3], close[-2] / open_[-3]],
        [dataframe.index[-1] - dataframe.index[-4], close[-2] / open_[-4]]],
        columns=['delt_compt', dataframe.columns[0][:-5] + '_var_compt']).set_index('delt_compt')
    return df_cumputing


#  recoi en entré dataframe
def contact_var_computing(dataframe):
    return dataframe


# Calcul du coef_multiplicateur
# entre =>  Dataframe  exemple crypto['eth/usdt']
# sortie => pandas.Series du coeffitient multiplicateur
def coef_multi(dataframe):
    liste_finale = []
    for i in range(len(dataframe.index)):
        if dataframe[dataframe.columns[2]][i] == 0:
            liste_finale.append(0)
        else:
            break
    var_zeros = dataframe[dataframe.columns[2]][:i]
    var_sans_zero = dataframe.iloc[i:][dataframe.columns[2]]
    var_sans_z_cumprod = var_sans_zero.cumprod()
    coef_multi = pd.concat([var_zeros, var_sans_z_cumprod])
    return coef_multi


#
# converti timestamp en datatime
# entrée dataframe
# Sortie dataframe
def convert_time(dataframe):
    temps = []
    for elm in dataframe['timestamp']:
        temps.append(datetime.fromtimestamp(elm / 1000))
    dataframe['timestamp'] = pd.DatetimeIndex(pd.to_datetime(temps)).tz_localize('UTC').tz_convert('UTC')
    return dataframe


# foction pour détecter les mauvai shape
# entrée dictionnaire
# Sortie array
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


# corrections des shape en ajoutant une colonne de zero et une colonnes de ones
# entrée dictionnaire  et array
# Sortie dictionnaire
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


# génération de datatime en fontion du pas
# entre  dataframe  + timedelta
# sortie liste datatime
def generation_date(dataframe, delta_pas):
    test_list = []
    pas = timedelta(hours=delta_pas)
    date_ini = dataframe.index[::-1][0]
    inverse_time = dataframe.index[::-1]
    for i in range(len(inverse_time)):
        test_list.append(date_ini - pas * i)
    test_list = test_list[::-1]
    return test_list


# entrée  name_crypto ,star_time, end_time
# Sorite Dataframe

def down_all_coin(name_crypto, star_time, end_time, delta_hour, exchange):
    all_coin = []
    for time in range(star_time, end_time, int(28857600000)):
        all_coin.append(exchange.fetch_ohlcv(name_crypto, limit=1000, since=time, timeframe=delta_hour))
        con_all_coin = np.concatenate(all_coin)
    df_all_coin = pd.DataFrame(con_all_coin, columns=['timestamp', name_crypto[:3].lower() + '_open', 'high', 'low',
                                                      name_crypto[:3].lower() + '_close', 'volume'])
    df_all_coin = convert_time(df_all_coin).drop_duplicates()
    return df_all_coin


def fonction_cumul(dataframe, name_crypto):
    dataframe['cumul_' + name_crypto[:-5]] = ((dataframe['coef_multi_' + name_crypto[:-5]]) * 100) - 100
    return dataframe


def coef_multi2(dataframe, fontion_variation):
    variation = fontion_variation.values
    ini_varia = fontion_variation[0]
    coef_multi = [ini_varia]
    for elm, i in zip(variation, variation.index):
        coef_multi[i] = elm * coef_multi[i - 1]
        coef_multi.append(coef_multi[i])
    return coef_multi[:-1]


def plotly(dataframe, cumul):
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=dataframe.index, y=dataframe[cumul], mode='lines', name='test affichage'))
    return fig


def to_timestamp(date):
    element = datetime.strptime(date, "%Y-%m-%d")
    timestamp = int(datetime.timestamp(element)) * 1000
    return timestamp


def fonction_tableau_var(dictionnaire_crypto):
    liste_var = []
    liste_crypto = []
    index = []
    for nom_crypto in dictionnaire_crypto:
        liste_var.append(dictionnaire_crypto[nom_crypto][nom_crypto[:3] + '_var'])
        liste_crypto.append(nom_crypto[:3] + '_var')
    index = dictionnaire_crypto[nom_crypto].index
    # print(np.transpose(liste_var))
    df_liste_var = pd.DataFrame(np.transpose(liste_var), columns=liste_crypto).set_index(index)
    return df_liste_var


# algorithme  qui cherche la meilleur valeur d'une crypto à  un instant t
# ENtrée dataframe
# sortie dataframe 2 colinnes
def meilleur_varaition(dataframe):
    max_var = dataframe.max(axis=1)
    name_max_var = dataframe.idxmax(axis=1)
    concat_meilleur_var = pd.concat([max_var, name_max_var], axis=1)
    concat_meilleur_var = pd.concat([dataframe, concat_meilleur_var], axis=1)
    concat_meilleur_var.rename(columns={0: 'var_max', 1: 'meilleur_var'}, inplace=True)
    return concat_meilleur_var


# entrée dataframe
def meilleur_var_computing(dataframe, type_computing):
    if type_computing == 'n-1':
        max_var_computing = dataframe.iloc[:1].max(axis=1)
        name_max_var_computing = dataframe.iloc[:1].idxmax(axis=1)
        return max_var_computing.values[0], name_max_var_computing.values[0]

    if type_computing == 'n-2':
        max_var_computing = dataframe.iloc[1:].max(axis=1)
        name_max_var_computing = dataframe.iloc[1:].idxmax(axis=1)
        return max_var_computing.values[0], name_max_var_computing.values[0]


def concat_meilleur_var(concat_meilleur_var):
    concat_meilleur_var['variation_bx1'] = (concat_meilleur_var[0] * 100) - 100
    concat_meilleur_var['cumul_bx1'] = concat_meilleur_var['variation_bx1'].cumsum()
    return concat_meilleur_var


# entré dataaframe des varaibles
def algo(concat_meilleur_var):
    tempo = []
    list_valeur_algo = []
    nbr_colon = len(concat_meilleur_var.columns) - 2
    df_utile = concat_meilleur_var.iloc[:, :nbr_colon]
    serie_var_max = concat_meilleur_var['var_max']
    df_utile['index'] = range(len(serie_var_max))
    df_utile.set_index('index', inplace=True)
    nom_init = df_utile[df_utile.index == 0].idxmax(axis=1).values[0]
    tempo.append(df_utile[df_utile.index == 0][nom_init].values)
    for i in range(0, len(df_utile) - 1):
        name_i_max = df_utile[df_utile.index == i].idxmax(axis=1).values[0]
        tempo.append(df_utile[df_utile.index == i + 1][name_i_max].values)
    for elm in tempo:
        list_valeur_algo.append(elm[0])
    return list_valeur_algo


# entré dataframe  le tableau de variation
# sortie le nom de la crypto
def nom_crypto_achat_vente(tableau_var):
    # print(tableau_var.iloc[:,:5])
    if tableau_var['meilleur_var'].iloc[0] == tableau_var['meilleur_var'].iloc[1]:
        return False
    else:
        name_cryptos = tableau_var['meilleur_var'].iloc[0][:3].upper() + '/USDT'
        if name_cryptos == 'DOG/USDT':
            name_cryptos = 'DOGE/USDT'
        elif name_cryptos == 'LIN/USDT':
            name_cryptos = 'LINK/USDT'
        elif name_cryptos == 'AAV/USDT':
            name_cryptos = 'AAVE/USDT'
        elif name_cryptos == 'MAT/USDT':
            name_cryptos = 'MATIC/USDT'
        elif name_cryptos == 'LUN/USDT':
            name_cryptos = 'LUNA/USDT'
        elif name_cryptos == 'THE/USDT':
            name_cryptos = 'THETA/USDT'

        else:
            pass
        return name_cryptos


# Achat


# entrée nom crypto un string ex :  'DOGE/USDT'
def algo_achat_vente(exchange, nom_crypto_vente, nom_crypto_achat):
    balence = exchange.fetch_spot_balance()
    print('## Wallet amount (USDT)', balence['total']['USDT'])
    if (nom_crypto_achat == False) or (nom_crypto_achat == nom_crypto_vente):
        print('## Staying on the same cryptocurency')
        pass
    else:
        # buy
        if (nom_crypto_vente != 'none'):
            sell = vente(exchange, nom_crypto_vente, balence['total'])
        print('vendage : ', nom_crypto_vente)

        def acheter(exchange, var2, pourcentage):
            montant_USDT = float(exchange.fetch_spot_balance().get('USDT').get('free'))
            dict = exchange.fetchTicker(var2)
            last = dict['last']
            # Prevent error divide by zero
            while last == 0:
                try:
                    last = exchange.fetchTicker(var2)['last']
                except:
                    pass
            buy = exchange.create_spot_order(var2, "market", "buy", montant_USDT, pourcentage)
            return buy

        # sell
        while True:
            try:
                acheter = acheter(exchange, nom_crypto_achat, 1)
                break
            except:
                print('EXECUTION AVEC EXEPTION', nom_crypto_achat)
                acheter = acheter(exchange, nom_crypto_achat, 0.97)
                break


def vente(exchange, var1, balence_total):
    sell_1 = exchange.create_market_sell_order(var1, balence_total[var1[:-5]])
    return sell_1


def acheter_2(exchange, var2, balence_total, pourcentage):
    montant_USDT = float(exchange.fetch_spot_balance().get('USDT').get('free'))
    dict = exchange.fetchTicker(var2)
    last = dict['last']
    # Prevent error divide by zero
    while last == 0:
        try:
            last = exchange.fetchTicker(var2)['last']
        except:
            pass
    buy = exchange.create_spot_order(var2,"market","buy",montant_USDT,pourcentage)
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

    def insert(self, data):
        cursor = self.cnx.cursor()
        query = "INSERT INTO  get_balence (dates, crypto_name, crypto_wallet,id_bot) VALUES  (%s, %s , %s,%s)"
        cursor.execute(query, data)
        self.cnx.commit()
        cursor.close()
        self.cnx.close()
        return print("value added to database ", data)


def sleep_time(sec):
    for elm in range(sec):
        print(elm)
        tm.sleep(sec)


def get_wallet(exchange):
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
    return sum(dict_balence_usdt.values())+usdtt


# mahdi from here!

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


def getBotMax(crypto, market, type_computing):
    crr = {}
    for elm in market:
        for i in crypto[elm.lower()]:
            if (i == "Variation_" + elm.lower()[:-5]):
                crr[i] = crypto[elm.lower()][i]
    crr = pd.DataFrame(crr)
    crr = crr.iloc[-2].idxmax()
    crr = crr[len("Variation_"):]
    return ((crr + "/usdt").upper())


def isEmptyDict(di):
    for i in di :
        if not (di[i].empty):
            return False
    return True

def crypto_a_vendre2(exchange, market):
    try:
        df_hystoric_order = {}
        liste_df = []
        liste_name_crypto = []

        for name_crypto in market:
            x = (datetime.now() - timedelta(days=365)).timestamp() * 1000
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
            elif isEmptyDict(df_hystoric_order) :
                var1 = name_crypto
                montant_USDT = float(exchange.fetch_spot_balance().get('USDT').get('free'))
                exchange.create_spot_order(var1,"market","buy",montant_USDT,1)
                x = exchange.fetchMyTrades(name_crypto)
                df_hystoric_order[name_crypto_up] = pd.DataFrame.from_dict(x)
                index_dernier_ordre = df_hystoric_order[name_crypto_up].index.max()
                liste_df.append(df_hystoric_order[name_crypto_up].loc[index_dernier_ordre])
        pd.set_option('display.max_columns', None)
        df_log = pd.DataFrame(liste_df).set_index('symbol')
        df_datetime_side_cost = df_log[['datetime', 'side', 'cost']]
        global crypto_a_vendre
        try:
            balence = exchange.fetch_spot_balance()
            crypto_a_vendre = df_log[df_log['side'] == 'buy'].index[0]
        except IndexError as e:
            print(f"# Warning  : {e} we buy BTC by default")
            acheter_2(exchange, "BTC/USDT", balence['total'], 1)
            cryptos_a_vendre = "BTC/USDT"
        return crypto_a_vendre
    except IndexError:
        return '0'

def get_pair_symbol_for_last_balence_by_id(id):
    pwd = mot_de_passe
    con = ConnectBbd('localhost', '3306', 'root', pwd, 'cryptos', 'mysql_native_password')
    cursor = con.cnx.cursor()
    query = f"select crypto_name from get_balence where id_bot = {id} order by id_get_balence desc limit 2;"
    cursor.execute(query)
    myresult = cursor.fetchall()
    return myresult
def crypto_a_vendre(exchange,idbot):
    try :
        crypto_name = get_pair_symbol_for_last_balence_by_id(idbot)[0][0]
        if (crypto_name == "USDT"):
            crypto_name = get_pair_symbol_for_last_balence_by_id(idbot)[1][0]
            print(f"We'll buy {crypto_name} for now just for the start !")
            montant_USDT = float(exchange.fetch_spot_balance().get('USDT').get('free'))
            exchange.create_spot_order(crypto_name, "market", "buy", montant_USDT, 1)
    except Exception as exx :
        crypto_name = "BTC/USDT"
        print("We'll buy btc for now just for the start !")
        montant_USDT = float(exchange.fetch_spot_balance().get('USDT').get('free'))
        exchange.create_spot_order("BTC/USDT", "market", "buy", montant_USDT, 1)
    return crypto_name

def affichageDataFrameLog(crypto):
    crypto = pd.concat(crypto, axis=1)
    return crypto
