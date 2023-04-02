import ccxt
import pandas as pd
import os
import numpy as np
import pickle as pk
import matplotlib.pyplot as plt
from datetime import datetime
from datetime import time
from datetime import timedelta
import plotly.express as px
import streamlit as st
import plotly.graph_objects as go
import base64
from binance.client import Client
from bdd_communication import *
from ProjectSettings import  *

st.set_page_config(
    page_title= page_title,
    page_icon= page_icon,
)

st.title(page_title)


st.title("Back Test Cocotier")



date_init = datetime.now() - timedelta(days=180)

exchange = ccxt.binance({'enableRateLimit': True})
exchange.load_markets()

liste_crypto1 = np.array(['BTC/USDT', 'ETH/USDT', 'ADA/USDT', 'DOGE/USDT', 'BNB/USDT', 'UNI/USDT',
                          'LTC/USDT', 'BCH/USDT', 'LINK/USDT', 'VET/USDT', 'XLM/USDT', 'FIL/USDT', 'TRX/USDT',
                          'NEO/USDT', 'EOS/USDT', 'DOT/USDT'])

liste_crypto = np.array(['ADA/USDT', 'DOGE/USDT', 'BNB/USDT', 'ETH/USDT', 'DOT/USDT'])


def main():
    #input
    emplacement = st.empty()
    col1, col2 = emplacement.columns([5, 5])
    star_time = col1.date_input('date de début', date_init)
    end_time = col2.date_input('date de fin')
    star_hour = col1.time_input("Start Time",time(0,0))
    end_hour = col2.time_input("End Time",time(23,0))
    sttDate = f"{star_time} {star_hour}"
    ennDate = f"{end_time} {end_hour}"
    delta_hour = st.selectbox('selectionner une plage auraire', ['4h', '6h', '8h', '12h'])
    n_i = st.radio("Selectionner l'algorithmique qu'on va travailler avec",("N","N-1","N-2"),horizontal=True)
    market = choix_market()

    client = Client()
    crypto = {}
    if 'searching' not in st.session_state:
        st.session_state.searching = False
    if (st.button("Submit")or st.session_state.searching):
        st.session_state.searching = True
        for elm in market :

            #get the values from binance as they are and convert them to a dataframe we can work with
            x = elm.lower()+'/usdt'

            crypto[x] = client.get_historical_klines(x.replace("/", "").upper(), delta_hour, sttDate, ennDate)
            crypto[x] = pd.DataFrame(data=crypto[x],
                                     columns=['timestamp', x[:-5] + '_open', 'high', 'low', x[:-5] + '_close', 'volume',
                                              'close_time', 'quote_av', 'trades', 'tb_base_av', 'tb_quote_av', 'ignore'])
            crypto[x] = crypto[x][['timestamp', x[:-5] + '_open', x[:-5] + '_close']]
            crypto[x] = convert_time(crypto[x])
            crypto[x] = crypto[x].astype({x[:-5] + '_open': 'float64',
                                          x[:-5] + '_close': 'float64'
                                          })
            crypto[x] = crypto[x].set_index('timestamp')

        #Correction wrong values
        array_mauvais_shape = detection_mauvais_shape(crypto)
        crypto = correction_shape(crypto, array_mauvais_shape)
        for elm in array_mauvais_shape:
            crypto[elm]['timestamp'] = generation_date(crypto[elm], int(delta_hour[:1]))
            crypto[elm] = crypto[elm].set_index('timestamp')
        crypto = variationN(crypto, n_i)
        crypto = coeffMulti(crypto)
        crypto = mergeCryptoTogether(crypto)
        crypto, maxis = botMax(crypto)
        crypto = botMaxVariation2(crypto, maxis)
        crypto = coeffMultiBotMax(crypto)
        coefMulti = coefmultiFinal(crypto)
        plot_courbes2(coefMulti)
        st.write(coefMulti.tail(1))
        if st.checkbox('Voir tableau coef multi'):
            st.write(coefMulti)
        if st.checkbox('Voir tableau de variation'):
            crypto = VariationFinal(crypto)
            st.write(crypto)

if __name__ == '__main__':
    main()
