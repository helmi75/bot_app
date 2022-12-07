#alter table settings modify value_setting text ;
# insert into settings values (2,'pair_symbols',0,'ETH,ADA,DOGE,BNB,DOT');

import streamlit as st
import numpy as np
from binance.client import Client
from bdd_communication import ConnectBbd
from pass_secret import mot_de_passe

con = ConnectBbd('localhost', '3306', 'root', mot_de_passe, 'cryptos', 'mysql_native_password')
liste_crypto = con.getAllPairSymbols()[0][0].split(',')
@st.cache
def getAllPairSymbolsOfBinance():
    cryptoss = []
    client = Client()
    exchange_info = client.get_exchange_info()
    for s in exchange_info['symbols']:
        if s['symbol'].endswith('USDT'):
            cryptoss.append(s['symbol'])
    return cryptoss
cryptoss = getAllPairSymbolsOfBinance()
cols2 = st.columns(4)
newCrypto = cols2[0].text_input("Write the pair symbol here!")
searching = cols2[3].button("Search")
if 'searching' not in st.session_state:
    st.session_state.searching = False
if (searching or st.session_state.searching):
    st.session_state.searching = True
    crr = newCrypto.upper().replace('/', '')
    if not (len(crr) > 4 and crr[-4:] == 'USDT'):
        crr += 'USDT'
    countt = cryptoss.count(crr)
    if (countt == 0):
        st.warning("cette crypto n’existe pas")
    else :
        if(liste_crypto.count(crr[:-4])):
            if(cols2[2].button("Delete it from List")):
                liste_crypto.remove(crr[:-4])
                newcrr = ','.join(liste_crypto)
                con.updatePairSymbols(newcrr)
                st.success(f"{crr[:-4]} a été supprimé de la liste")

        else:
            if (cols2[2].button("Add it to List")):
                liste_crypto.append(crr[:-4])
                newcrr = ','.join(liste_crypto)
                con.updatePairSymbols(newcrr)
                st.success(f"{crr[:-4]} a été ajouté à la listse")




cols3 = st.columns(7)
for i in range(len(liste_crypto)):
    cols3[i%7].write(liste_crypto[i])

