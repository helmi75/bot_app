import streamlit as st
import ccxt
import pandas as pd
import os
import ta
import numpy as np
import pickle as pk
from math import *
import matplotlib.pyplot as plt
from datetime import datetime
from time import time
from datetime import timedelta
from IPython.display import clear_output
import plotly.express as px
import plotly.graph_objects as go
import base64
from mpl_toolkits.mplot3d import Axes3D
from matplotlib import cm
from binance.client import Client
from bdd_communication import *

st.set_page_config(
    page_title="Cocobots",
    page_icon="code.png",
)
st.title("Cocobots")
st.title("Back Test Trix")


@st.cache
def getAllPairSymbolsOfBinance():
    cryptoss = []
    client = Client()
    exchange_info = client.get_exchange_info()
    for s in exchange_info['symbols']:
        if s['symbol'].endswith('USDT'):
            cryptoss.append(s['symbol'])
    return cryptoss


def buyCondition(row, previousRow):
    if row['TRIX_HISTO'] > 0 and row['STOCH_RSI'] < stoch_top:
        return True
    else:
        return False


def sellCondition(row, previousRow):
    if row['TRIX_HISTO'] < 0 and row['STOCH_RSI'] > stoch_bottom:
        return True
    else:
        return False


def plot_courbes2(df_tableau_multi, namee,rcolor):
    fig = go.Figure()
    for elm in df_tableau_multi.columns:
        fig.add_trace(go.Scatter(x=df_tableau_multi[elm].index,
                                 y=df_tableau_multi[elm],
                                 mode='lines',
                                 name=elm,
                                 line=dict(color = rcolor)
                                 ))
    fig.update_layout(
        title={
            'text': namee,
            'y': 0.9,
            'x': 0.5,
            'xanchor': 'center',
            'yanchor': 'top'},
    )
    return st.plotly_chart(fig)


date_init = datetime.now() - timedelta(days=180)
timeInterval = '1h'
ema200 = 200
dfTest = None
# Plage des paramettres pour le OPTIMIZER  des paramettres
stochTop_plage = [85, 90, 1]
stochBottom_plage = [25, 30, 1]
stoch_rsi_plage = [12, 16, 1]
trixLength_plage = [9, 11, 1]
trixSignal_plage = [20, 25, 1]

st.text("The format of the Pair symbol can be either the name+USDT like 'BTCUSDT'"
        "\nor name+/+USDT like 'BTC/USDT' "
        "\nor simply just the name like 'BTC'\t no problem of the uppercase or lowercase")
emplacement = st.empty()
col1, col2, col3 = emplacement.columns([5, 5, 5])
pair_symbol = col1.text_input("Pair Symbol", value="...USDT")
star_date = col2.date_input('Date de début', date_init)
stDate = to_timestamp(str(star_date))
end_date = col3.date_input('Date de fin')
enDate = to_timestamp(str(end_date))

start_balance = col1.number_input("Start Balance", value=1000)
trix_length = col2.number_input("Trix Length", value=9)
trix_signal = col3.number_input("Trix Signal", value=21)
stoch_top = col1.number_input("Stoch Top", value=0.8)
stoch_bottom = col2.number_input("Stoch Bottom", value=0.24)
stoch_rsi = col3.number_input("Stoch RSI", value=15)

cryptoss = getAllPairSymbolsOfBinance()
crr = pair_symbol.upper().replace('/', '')
if not (len(crr) > 4 and crr[-4:] == 'USDT'):
    crr += 'USDT'
countt = cryptoss.count(crr)
if st.button("Submit"):
    if (countt == 0):
        st.warning("cette crypto n’existe pas")
    else:
        pair_symbol = pair_symbol.upper()
        if len(pair_symbol) < 4 or pair_symbol[-4:] != 'USDT':
            pair_symbol = pair_symbol + 'USDT'
        st.success(pair_symbol)
        client = Client()
        klinesT = client.get_historical_klines(pair_symbol, timeInterval, stDate)
        # -- Define your dataset --
        df = pd.DataFrame(klinesT, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume', 'close_time',
                                            'quote_av', 'trades', 'tb_base_av', 'tb_quote_av', 'ignore'])
        df['close'] = pd.to_numeric(df['close'])
        df['high'] = pd.to_numeric(df['high'])
        df['low'] = pd.to_numeric(df['low'])
        df['open'] = pd.to_numeric(df['open'])
        df = df.set_index(df['timestamp'])
        df.index = pd.to_datetime(df.index, unit='ms')
        del df['timestamp']
        df.drop(df.columns.difference(['open', 'high', 'low', 'close', 'volume']), 1, inplace=True)
        df['EMA200'] = ta.trend.ema_indicator(close=df['close'], window=ema200)
        df['TRIX'] = ta.trend.ema_indicator(
            ta.trend.ema_indicator(ta.trend.ema_indicator(close=df['close'], window=trix_length), window=trix_length),
            window=trix_length)
        df['TRIX_PCT'] = df["TRIX"].pct_change() * 100
        df['TRIX_SIGNAL'] = ta.trend.sma_indicator(df['TRIX_PCT'], trix_signal)
        df['TRIX_HISTO'] = df['TRIX_PCT'] - df['TRIX_SIGNAL']
        df['STOCH_RSI'] = ta.momentum.stochrsi(close=df['close'], window=stoch_rsi, smooth1=3, smooth2=3)
        dfTest = df[star_date: end_date]
        dt = pd.DataFrame(columns=['date', 'position', 'reason', 'price', 'frais', 'fiat', 'coins', 'wallet', 'drawBack'])
        usdt = 1000
        makerFee = 0.0002
        takerFee = 0.0007
        # -- Do not touch these values --
        initalWallet = usdt
        wallet = usdt
        coin = 0
        lastAth = 0
        previousRow = dfTest.iloc[0]
        stopLoss = 0
        takeProfit = 500000
        buyReady = True
        sellReady = True
        for index, row in dfTest.iterrows():
            if buyCondition(row, previousRow) and usdt > 0 and buyReady == True:
                buyPrice = row['close']
                coin = usdt / buyPrice
                fee = takerFee * coin
                coin = coin - fee
                usdt = 0
                wallet = coin * row['close']
                if wallet > lastAth:
                    lastAth = wallet
                    myrow = {'date': index, 'position': "Buy", 'reason': 'Buy Market Order', 'price': buyPrice,
                             'frais': fee,
                             'fiat': usdt, 'coins': coin, 'wallet': wallet, 'drawBack': (wallet - lastAth) / lastAth}
                    dt = dt.append(myrow, ignore_index=True)
                elif row['low'] < stopLoss and coin > 0:
                    sellPrice = stopLoss
                    usdt = coin * sellPrice
                    fee = makerFee * usdt
                    usdt = usdt - fee
                    coin = 0
                    buyReady = False
                    wallet = usdt
                    if wallet > lastAth:
                        lastAth = wallet
                        myrow = {'date': index, 'position': "Sell", 'reason': 'Sell Stop Loss', 'price': sellPrice,
                                 'frais': fee,
                                 'fiat': usdt, 'coins': coin, 'wallet': wallet, 'drawBack': (wallet - lastAth) / lastAth}
                        dt = dt.append(myrow, ignore_index=True)
            elif sellCondition(row, previousRow) and coin > 0 and sellReady == True:
                sellPrice = row['close']
                usdt = coin * sellPrice
                fee = takerFee * usdt
                usdt = usdt - fee
                coin = 0
                buyReady = True
                wallet = usdt
                if wallet > lastAth:
                    lastAth = wallet
                    myrow = {'date': index, 'position': "Sell", 'reason': 'Sell Market Order', 'price': sellPrice,
                             'frais': fee,
                             'fiat': usdt, 'coins': coin, 'wallet': wallet, 'drawBack': (wallet - lastAth) / lastAth}
                    dt = dt.append(myrow, ignore_index=True)

            previousRow = row
        dt = dt.set_index(dt['date'])
        dt.index = pd.to_datetime(dt.index)
        dt['resultat'] = dt['wallet'].diff()
        dt['resultat%'] = dt['wallet'].pct_change() * 100
        dt.loc[dt['position'] == 'Buy', 'resultat'] = None
        dt.loc[dt['position'] == 'Buy', 'resultat%'] = None

        dt['tradeIs'] = ''
        dt.loc[dt['resultat'] > 0, 'tradeIs'] = 'Good'
        dt.loc[dt['resultat'] <= 0, 'tradeIs'] = 'Bad'

        iniClose = dfTest.iloc[0]['close']
        lastClose = dfTest.iloc[len(dfTest) - 1]['close']
        holdPercentage = ((lastClose - iniClose) / iniClose) * 100
        algoPercentage = ((wallet - initalWallet) / initalWallet) * 100
        vsHoldPercentage = ((algoPercentage - holdPercentage) / holdPercentage) * 100
        try:
            tradesPerformance = round(dt.loc[(dt['tradeIs'] == 'Good') | (dt['tradeIs'] == 'Bad'), 'resultat%'].sum()
                                      / dt.loc[(dt['tradeIs'] == 'Good') | (dt['tradeIs'] == 'Bad'), 'resultat%'].count(),
                                      2)
        except:
            tradesPerformance = 0
            # print("/!\ There is no Good or Bad Trades in your BackTest, maybe a problem...")
        try:
            totalGoodTrades = dt.groupby('tradeIs')['date'].nunique()['Good']
            AveragePercentagePositivTrades = round(dt.loc[dt['tradeIs'] == 'Good', 'resultat%'].sum()
                                                   / dt.loc[dt['tradeIs'] == 'Good', 'resultat%'].count(), 2)
            idbest = dt.loc[dt['tradeIs'] == 'Good', 'resultat%'].idxmax()
            bestTrade = str(
                round(dt.loc[dt['tradeIs'] == 'Good', 'resultat%'].max(), 2))
        except:
            totalGoodTrades = 0
            AveragePercentagePositivTrades = 0
            idbest = ''
            bestTrade = 0
            # print("/!\ There is no Good Trades in your BackTest, maybe a problem...")
        try:
            totalBadTrades = dt.groupby('tradeIs')['date'].nunique()['Bad']
            AveragePercentageNegativTrades = round(dt.loc[dt['tradeIs'] == 'Bad', 'resultat%'].sum()
                                                   / dt.loc[dt['tradeIs'] == 'Bad', 'resultat%'].count(), 2)
            idworst = dt.loc[dt['tradeIs'] == 'Bad', 'resultat%'].idxmin()
            worstTrade = round(dt.loc[dt['tradeIs'] == 'Bad', 'resultat%'].min(), 2)
        except:
            totalBadTrades = 0
            AveragePercentageNegativTrades = 0
            idworst = ''
            worstTrade = 0
            # print("/!\ There is no Bad Trades in your BackTest, maybe a problem...")
        totalTrades = totalBadTrades + totalGoodTrades
        winRateRatio = (totalGoodTrades / totalTrades) * 100
        st.text("Pair Symbol :" + pair_symbol)
        st.text("Period : [" + str(dfTest.index[0]) + "] -> [" +
                str(dfTest.index[len(dfTest) - 1]) + "]")
        st.text("Starting balance :" + str(initalWallet) + "$")

        st.text("\n----- General Informations -----")
        st.text("Final balance :" + str(round(wallet, 2)) + "$")
        st.text("Performance vs US Dollar :" + str(round(algoPercentage, 2)) + "%")
        st.text("Buy and Hold Performence :" + str(round(holdPercentage, 2)) + "%")
        st.text("Performance vs Buy and Hold :" + str(round(vsHoldPercentage, 2)) + "%")
        st.text("Best trade : " + str(bestTrade) + "%, the" + str(idbest))
        st.text("Worst trade :" + str(worstTrade) + "%, the" + str(idworst))
        st.text("Worst drawBack :" + str(100 * round(dt['drawBack'].min(), 2)) + "%")
        st.text("Total fees : " + str(round(dt['frais'].sum(), 2)) + "$")

        st.text("\n----- Trades Informations -----")
        st.text("Total trades on period :" + str(totalTrades))
        st.text("Number of positive trades :" + str(totalGoodTrades))
        st.text("Number of negative trades : " + str(totalBadTrades))
        st.text("Trades win rate ratio :" + str(round(winRateRatio, 2)) + '%')
        st.text("Average trades performance :" + str(tradesPerformance) + "%")
        st.text("Average positive trades :" + str(AveragePercentagePositivTrades) + "%")
        st.text("Average negative trades :" + str(AveragePercentageNegativTrades) + "%")

        st.text("\n----- Trades Reasons -----")
        reasons = dt['reason'].unique()
        for r in reasons:
            st.text(r + " number :" + str(dt.groupby('reason')['date'].nunique()[r]))

        st.text("\n----- Plot -----")
        x = dt['date']
        y = dt['wallet']
        fig, ax = plt.subplots()
        fig.set_figwidth(10)
        fig.set_figheight(4)
        fig.suptitle("wallet",fontsize=25)
        ax.plot(x, y, linewidth=2.0, color = "red")
        st.pyplot(fig)
        # plot_courbes2(dt[['wallet']], 'wallet','Red')

        z = dt['price']
        fig2, ax2 = plt.subplots()
        fig2.set_figwidth(10)
        fig2.set_figheight(4)
        fig2.suptitle("price",fontsize=25)
        ax2.plot(x, z, linewidth=2.0, color="blue")
        st.pyplot(fig2)
        # plot_courbes2(dt[['price']], 'price','Blue')
