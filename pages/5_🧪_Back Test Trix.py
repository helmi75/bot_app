import streamlit as st
import ta
import matplotlib.pyplot as plt
from binance.client import Client
import plotly.graph_objs as go
from bdd_communication import *
import seaborn as sns
import plotly.express as px

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


def plot_courbes2(df_tableau_multi, namee, rcolor):
    fig = go.Figure()
    for elm in df_tableau_multi.columns:
        fig.add_trace(go.Scatter(x=df_tableau_multi[elm].index,
                                 y=df_tableau_multi[elm],
                                 mode='lines',
                                 name=elm,
                                 line=dict(color=rcolor)
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
        klinesT = client.get_historical_klines(pair_symbol, timeInterval, str(star_date))
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
        dfTest = None
        # dfTest = df.copy()

        if str(end_date) == "":
            end_date = None
        dfTest = df[str(star_date): str(end_date)]
        dt = pd.DataFrame(
            columns=['date', 'position', 'reason', 'price', 'frais', 'fiat', 'coins', 'wallet', 'drawBack'])
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
        BuyandHoldperformance = lastClose / iniClose
        try:
            tradesPerformance = round(dt.loc[(dt['tradeIs'] == 'Good') | (dt['tradeIs'] == 'Bad'), 'resultat%'].sum()
                                      / dt.loc[
                                          (dt['tradeIs'] == 'Good') | (dt['tradeIs'] == 'Bad'), 'resultat%'].count(),
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
        fadit = start_balance * (1 + holdPercentage / 100)

        new_title = f'<p style="font-family:sans-serif; font-size: 25px;">{"Pair Symbol :" + pair_symbol}</p>'
        st.markdown(new_title, unsafe_allow_html=True)
        # st.text("Pair Symbol :" + pair_symbol)
        new_title = f'<p style="font-family:sans-serif; font-size: 25px;">{"Period : [" + str(dfTest.index[0]) + "] -> [" + str(dfTest.index[len(dfTest) - 1]) + "]"}</p>'
        st.markdown(new_title, unsafe_allow_html=True)
        # st.text("Period : [" + str(dfTest.index[0]) + "] -> [" +
        #         str(dfTest.index[len(dfTest) - 1]) + "]")
        new_title = f'<p style="font-family:sans-serif; font-size: 25px;">{"Starting balance :" + str(initalWallet) + "$"}</p>'
        st.markdown(new_title, unsafe_allow_html=True)
        # st.text("Starting balance :" + str(initalWallet) + "$")
        new_title = f'<p style="font-family:sans-serif; font-size: 25px;"><br>{"----- General Informations -----"}</p>'
        st.markdown(new_title, unsafe_allow_html=True)
        # st.text("\n----- General Informations -----")
        new_title = f'<p style="font-family:sans-serif; font-size: 25px;">{"Final balance :" + str(round(wallet, 2)) + "$"}</p>'
        st.markdown(new_title, unsafe_allow_html=True)
        # st.text("Final balance :" + str(round(wallet, 2)) + "$")

        new_title = f'<p style="font-family:sans-serif; font-size: 25px;">{"Performance Trix :" + str(round(algoPercentage, 2)) + "%"}</p>'
        st.markdown(new_title, unsafe_allow_html=True)

        new_title = f'<p style="font-family:sans-serif; font-size: 25px;">{"Performance Buy And hold (Dollars) :" + str(round(fadit, 2)) + "$"}</p>'
        st.markdown(new_title, unsafe_allow_html=True)

        # st.text("Performance vs US Dollar :" + str(round(algoPercentage, 2)) + "%")
        new_title = f'<p style="font-family:sans-serif; font-size: 25px;">{"Buy and Hold Performance :" + str(round(holdPercentage, 2)) + "%"}</p>'
        st.markdown(new_title, unsafe_allow_html=True)
        # st.text("Buy and Hold Performence :" + str(round(holdPercentage, 2)) + "%")
        new_title = f'<p style="font-family:sans-serif; font-size: 25px;"><b>{"Trix vs Buy and Hold :" + str(round(wallet / (fadit), 2))}</b></p>'
        st.markdown(new_title, unsafe_allow_html=True)
        # st.text(f"FinalBalance({round(wallet,2)})/PerformanceBuyAndHoldPerformance({start_balance}*{round(holdPercentage,2)}%={round(fadit,2)}) #{round(wallet/(fadit),2)}%")

        # st.text("Performance vs Buy and Hold :" + str(round(vsHoldPercentage, 2)) + "%")
        new_title = f'<p style="font-family:sans-serif; font-size: 25px;">{"Best trade : " + str(bestTrade) + "%, the" + str(idbest)}</p>'
        st.markdown(new_title, unsafe_allow_html=True)
        # st.text("Best trade : " + str(bestTrade) + "%, the" + str(idbest))
        new_title = f'<p style="font-family:sans-serif; font-size: 25px;">{"Worst trade :" + str(worstTrade) + "%, the" + str(idworst)}</p>'
        st.markdown(new_title, unsafe_allow_html=True)
        # st.text("Worst trade :" + str(worstTrade) + "%, the" + str(idworst))
        lllili = str(100 * round(dt['drawBack'].min(), 2))
        new_title = f'<p style="font-family:sans-serif; font-size: 25px;">{"Worst drawBack :" + lllili + "%"} </p>'
        st.markdown(new_title, unsafe_allow_html=True)
        # st.text("Worst drawBack :" + str(100 * round(dt['drawBack'].min(), 2)) + "%")
        lllili = str(round(dt['frais'].sum(), 2))
        new_title = f'<p style="font-family:sans-serif; font-size: 25px;">{"Total fees : " + lllili + "$"}</p>'
        st.markdown(new_title, unsafe_allow_html=True)
        # st.text("Total fees : " + str(round(dt['frais'].sum(), 2)) + "$")
        new_title = f'<p style="font-family:sans-serif; font-size: 25px;"><br>{"---- Trades Informations -----"}</p>'
        st.markdown(new_title, unsafe_allow_html=True)

        # st.text("\n----- Trades Informations -----")
        new_title = f'<p style="font-family:sans-serif; font-size: 25px;">{"Total trades on period :" + str(totalTrades)}</p>'
        st.markdown(new_title, unsafe_allow_html=True)
        # st.text("Total trades on period :" + str(totalTrades))
        new_title = f'<p style="font-family:sans-serif; font-size: 25px;">{"Number of positive trades :" + str(totalGoodTrades)}</p>'
        st.markdown(new_title, unsafe_allow_html=True)
        # st.text("Number of positive trades :" + str(totalGoodTrades))
        new_title = f'<p style="font-family:sans-serif; font-size: 25px;">{"Number of negative trades : " + str(totalBadTrades)}</p>'
        st.markdown(new_title, unsafe_allow_html=True)
        # st.text("Number of negative trades : " + str(totalBadTrades))
        new_title = f'<p style="font-family:sans-serif; font-size: 25px;">{"Trades win rate ratio :" + str(round(winRateRatio, 2)) + "%"}</p>'
        st.markdown(new_title, unsafe_allow_html=True)
        # st.text("Trades win rate ratio :" + str(round(winRateRatio, 2)) + '%')
        new_title = f'<p style="font-family:sans-serif; font-size: 25px;">{"Average trades performance :" + str(tradesPerformance) + "%"}</p>'
        st.markdown(new_title, unsafe_allow_html=True)
        # st.text("Average trades performance :" + str(tradesPerformance) + "%")
        new_title = f'<p style="font-family:sans-serif; font-size: 25px;">{"Average positive trades :" + str(AveragePercentagePositivTrades) + "%"}</p>'
        st.markdown(new_title, unsafe_allow_html=True)
        # st.text("Average positive trades :" + str(AveragePercentagePositivTrades) + "%")
        new_title = f'<p style="font-family:sans-serif; font-size: 25px;">{"Average negative trades :" + str(AveragePercentageNegativTrades) + "%"}</p>'
        st.markdown(new_title, unsafe_allow_html=True)
        # st.text("Average negative trades :" + str(AveragePercentageNegativTrades) + "%")
        new_title = f'<p style="font-family:sans-serif; font-size: 25px;"><br>{"----- Trades Reasons -----"}</p>'
        st.markdown(new_title, unsafe_allow_html=True)

        # st.text("\n----- Trades Reasons -----")

        reasons = dt['reason'].unique()
        for r in reasons:
            lllili = (r + " number :" + str(dt.groupby('reason')['date'].nunique()[r]))
            new_title = f'<p style="font-family:sans-serif; font-size: 25px;">{lllili}</p>'
            st.markdown(new_title, unsafe_allow_html=True)

        # st.text("\n----- Plot -----")
        new_title = f'<p style="font-family:sans-serif; font-size: 25px;"><br>{"----- Plot -----"}</p>'
        st.markdown(new_title, unsafe_allow_html=True)
        container = st.container()
        x = dt['date']
        y = dt['wallet']
        z = dt['price']

        # fig = plt.figure()
        # fig.set_figwidth(10)
        # fig.set_figheight(4)
        # ax = fig.add_subplot(111)
        # ax.plot(x, y, color="blue", label='Wallet')
        #
        # ax2 = ax.twinx()
        # ax2.plot(x, z, color="red", label='Price')
        # fig.legend(loc="upper right")
        #
        # ax.set_xlabel("Temps")
        # ax.set_ylabel(r"Wallet")
        # ax.yaxis.label.set_color('Blue')
        # ax.tick_params(axis='y', colors='blue')
        # ax2.set_ylabel(r"Price")
        # ax2.yaxis.label.set_color('red')
        # ax2.tick_params(axis='y', colors='red')
        #
        # st.pyplot(fig)

        st.dataframe(dt.iloc[[0, 1, 2, 3, 5, -5, -4, -3, -2, -1], :])
        # plot_courbes2(dt[['wallet']], 'wallet','Red')

        # fig2, ax2 = plt.subplots()
        # fig2.set_figwidth(10)
        # fig2.set_figheight(4)
        # fig2.suptitle("price", fontsize=25)
        # ax2.plot(x, z, linewidth=2.0, color="blue")
        # st.pyplot(fig2)
        # plot_courbes2(dt[['price']], 'price','Blue')

        dd = dt.copy()
        months = ["Jan", "Fev", "Mar", "Avr", "Mai", "Juin", "Juillet", "Aou", "Sep", "Oct", "Nov", "Dec"]
        dd.drop(['frais', 'fiat', 'coins', 'drawBack', 'resultat', 'resultat%', 'tradeIs', 'position', 'reason'],
                axis=1, inplace=True)
        dd["day"] = 0
        dd["year"] = 0
        dd["month"] = ""
        for i, j in enumerate(dd['date']):
            dd["day"][i] = dd["date"][i].day
            dd["year"][i] = dd["date"][i].year
            dd["month"][i] = months[dd["date"][i].month - 1]
        dd['Buy And Hold (%)'] = 100 * (dt.iloc[:, 3] - (dt.iloc[0, 3])) / dt.iloc[0, 3]
        dd['Buy And Hold ($)'] = initalWallet * (1 + dd['Buy And Hold (%)'] / 100)
        custom_palette = {'positive': 'green', 'negative': 'red'}

        performanceDict = {}
        for i in range(dd["date"][0].year, dd["date"][-1].year + 1):
            performanceDict[i] = {}
        for i in performanceDict:
            performanceDict[i] = dd.loc[dd['year'] == i, :]
        performYear = {}
        for i in performanceDict:
            performYear[i] = {"Performance": 0, "date start": 0, "date end": 0}
        res = list(performYear.keys())[0]
        performYear[res]['date start'] = performanceDict[res]['wallet'][0]
        performYear[res]['date end'] = performanceDict[res]['wallet'][-1]
        performYear[res]['Performance'] = 100 * (performYear[res]['date end'] - performYear[res]['date start']) / \
                                          performYear[res]['date start']
        for i, j in enumerate(performYear):
            if i == 0:
                pass
            else:
                performYear[j]['date start'] = performanceDict[j - 1]['wallet'][-1]
                performYear[j]['date end'] = performanceDict[j]['wallet'][-1]
                performYear[j]['Performance'] = 100 * (performYear[j]['date end'] - performYear[j]['date start']) / \
                                                performYear[j]['date start']

        performanceDictM = {}
        for i in range(dd["date"][0].year, dd["date"][-1].year + 1):
            performanceDictM[i] = {}

        for i in performanceDictM:
            for j in performanceDict[i]["month"]:
                performanceDictM[i][j] = dd.loc[(dd['month'] == j) & (dd['year'] == i), :]
        performMonth = {}
        for i in performanceDict:
            performMonth[i] = {}
        res = list(performMonth.keys())[0]

        for i in performMonth:
            for j in performanceDict[i]["month"]:
                performMonth[i][j] = {"Performance": 0, "date start": 0, "date end": 0}
        resi = list(performMonth[res].keys())[0]
        performMonth[res][resi]['date start'] = performanceDictM[res][resi]['wallet'][0]
        performMonth[res][resi]['date end'] = performanceDictM[res][resi]['wallet'][-1]
        performMonth[res][resi]['Performance'] = 100 * (
                performMonth[res][resi]['date end'] - performMonth[res][resi]['date start']) / \
                                                 performMonth[res][resi]['date start']
        xx = 0
        for i, j in enumerate(performMonth):
            for l, k in enumerate(performMonth[j]):
                if (l == 0 and i == 0):
                    xx = performMonth[j][k]['date end']
                else:
                    performMonth[j][k]['date start'] = xx
                    performMonth[j][k]['date end'] = performanceDictM[j][k]['wallet'][-1]
                    performMonth[j][k]['Performance'] = 100 * (
                            performMonth[j][k]['date end'] - performMonth[j][k]['date start']) / performMonth[j][k][
                                                            'date start']
                    xx = performMonth[j][k]['date end']

        dfYY = pd.DataFrame.from_dict(performYear).T
        dfYY["years"] = dfYY.index
        dfY = dfYY.loc[:, ["Performance", "years"]]
        # fig, ax_left = plt.subplots(figsize=(15, 20), nrows=4, ncols=1)
        # sns.set(font_scale=0.8)
        # fig, ax = plt.subplots(figsize=(10, 5), dpi=100)
        # custom_palette = {'positive': 'green', 'negative': 'red'}
        #
        # sns.barplot(data=dfY, y="Performance", x="years", ax=ax, palette=custom_palette,
        #             hue=np.where(dfY['Performance'] >= 0, 'positive', 'negative'))
        # for index, row in dfY.iterrows():
        #     if row.Performance >= 0:
        #         ax.text(row.name - res, row.Performance, '+' + str(round(row.Performance)) + '%', color='black',
        #                 ha="center", va="bottom")
        #     else:
        #         ax.text(row.name - res, row.Performance, '-' + str(round(row.Performance)) + '%', color='black',
        #                 ha="center", va="top")
        # ax.set_title('years performance in %')
        # ax.legend_.remove()
        # st.pyplot(fig)


        # Create a custom palette for positive and negative values
        custom_palette = {'positive': 'green', 'negative': 'red'}

        # Create a trace for positive values
        positive_trace = go.Bar(
            x=dfY[dfY['Performance'] >= 0]['years'],
            y=dfY[dfY['Performance'] >= 0]['Performance'],
            marker=dict(color=custom_palette['positive']),
            name='+'
        )

        # Create a trace for negative values
        negative_trace = go.Bar(
            x=dfY[dfY['Performance'] < 0]['years'],
            y=dfY[dfY['Performance'] < 0]['Performance'],
            marker=dict(color=custom_palette['negative']),
            name='-'
        )

        # Combine the traces
        data = [positive_trace, negative_trace]

        # Add the text annotations to the positive and negative bars
        for index, row in dfY.iterrows():
            if row.Performance >= 0:
                text = '+' + str(round(row.Performance)) + '%'
                text_position = 'bottom center'
            else:
                text = '-' + str(round(row.Performance)) + '%'
                text_position = 'top center'
            data.append(
                go.Scatter(
                    x=[row.years],
                    y=[row.Performance],
                    text=text,
                    textposition=text_position,
                    mode='text'
                )
            )

        # Define the layout
        layout = go.Layout(
            title='years performance in %',
            showlegend=False
        )

        # Create the figure
        fig = go.Figure(data=data, layout=layout)

        # Show the figure
        st.plotly_chart(fig)

        for i in performMonth:
            dfMM = pd.DataFrame.from_dict(performMonth[i]).T
            dfMM["months"] = dfMM.index
            dfMMM = dfMM.loc[:, ["Performance", "months"]]
            # sns.set(font_scale=0.8)
            # fig, ax = plt.subplots(figsize=(10, 5), dpi=100)
            # custom_palette = {'positive': 'green', 'negative': 'red'}
            # firstMonth = list(dfMMM.months)[0]
            # firstMonhtPos = months.index(firstMonth)
            # sns.barplot(data=dfMMM, y="Performance", x="months", ax=ax, palette=custom_palette,
            #             hue=np.where(dfMMM['Performance'] >= 0, 'positive', 'negative'))
            # for index, row in dfMMM.iterrows():
            #     if row.Performance >= 0:
            #         ax.text(months.index(row.months) - firstMonhtPos, row.Performance,
            #                 '+' + str(round(row.Performance)) + '%', color='black', ha="center", va="bottom")
            #     else:
            #         ax.text(months.index(row.months) - firstMonhtPos, row.Performance,
            #                 '-' + str(round(row.Performance)) + '%', color='black', ha="center", va="top")
            # ax.set_title(f'{i} performance in %\n{round(performYear[i]["Performance"])}%')
            # ax.legend_.remove()
            # st.pyplot(fig)

            # Create a custom palette for positive and negative values
            custom_palette = {'positive': 'green', 'negative': 'red'}

            # Determine the first month in the dataset
            first_month = list(dfMMM.months)[0]

            # Determine the index of the first month in the months list
            first_month_pos = months.index(first_month)

            # Create traces for positive and negative values
            traces = []
            for month in months:
                df_month = dfMMM[dfMMM['months'] == month]
                if len(df_month) == 1:
                    performance = df_month['Performance'].iloc[0]
                    if performance >= 0:
                        trace = go.Bar(
                            x=[month],
                            y=[performance],
                            marker=dict(color=custom_palette['positive']),
                            name='+'
                        )
                    else:
                        trace = go.Bar(
                            x=[month],
                            y=[performance],
                            marker=dict(color=custom_palette['negative']),
                            name='-'
                        )
                    traces.append(trace)

            # Add the text annotations to the positive and negative bars
            for index, row in dfMMM.iterrows():
                if row.Performance >= 0:
                    text = '+' + str(round(row.Performance)) + '%'
                    text_position = 'bottom center'
                else:
                    text = '' + str(round(row.Performance)) + '%'
                    text_position = 'top center'
                trace = go.Scatter(
                    x=[row.months],
                    y=[row.Performance],
                    text=text,
                    textposition=text_position,
                    mode='text'
                )
                traces.append(trace)

            # Define the layout
            layout = go.Layout(
                title=f'{i} performance in %\n{round(performYear[i]["Performance"])}%',
                showlegend=False
            )

            # Create the figure
            fig = go.Figure(data=traces, layout=layout)
            st.plotly_chart(fig)


        x = dd['date']
        y = dd['wallet']
        z = dd['Buy And Hold ($)']
        with container:
            fig = plt.figure()
            fig.set_figwidth(10)
            fig.set_figheight(4)
            ax = fig.add_subplot(111)
            ax.plot(x, y, color="blue", label='Wallet ($)')

            # ax2 = ax.twinx()
            ax2 = ax
            ax2.plot(x, z, color="red", label='Buy And Hold ($)')
            fig.legend(loc="upper right")

            ax.set_xlabel("Temps")
            ax.set_ylabel(r"Value en ($)")
            # ax.yaxis.label.set_color('Blue')
            # ax.tick_params(axis='y', colors='blue')
            # ax2.set_ylabel(r"Buy And Hold ($)")
            # ax2.yaxis.label.set_color('black')
            # ax2.tick_params(axis='y', colors='red')
            ax.set_title('Wallet VS Buy and Hold')
            # st.pyplot(fig)

            # dynamic plot with plotly
            fig1 = go.Figure()
            fig1.add_trace(go.Scatter(x=x, y=y, mode='lines', name='Wallet ($)'))
            fig1.add_trace(go.Scatter(x=x, y=z, mode='lines', name='Buy And Hold ($)'))
            # fig_.set_title('Wallet VS Buy and Hold')
            fig1.update_layout(title={
                'text': 'Wallet VS Buy and Hold',
                'x': 0.5,
                'xanchor': 'center'},
                xaxis_title="Temps",
                yaxis_title="Value en ($)")
            st.plotly_chart(fig1)
