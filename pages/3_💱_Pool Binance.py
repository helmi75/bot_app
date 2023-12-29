import streamlit as st
from binance.client import Client
from utilities.bdd_communication import ConnectBbd
from ProjectSettings import *
from pass_secret import mot_de_passe
import ccxt

st.set_page_config(
    page_title= page_title,
    page_icon= page_icon,
)

st.title(page_title)

st.title("Pool Binance Pairs Symbol")


con = ConnectBbd('localhost', '3306', 'root', mot_de_passe, 'cryptos', 'mysql_native_password')
liste_crypto = con.getAllPairSymbolsBinance()[0][0].split(',')

@st.cache
def getAllPairSymbolsOfBinance_old():
    cryptoss = []
    client = Client()
    exchange_info = client.get_exchange_info()
    for s in exchange_info['symbols']:
        if s['symbol'].endswith('USDT'):
            cryptoss.append(s['symbol'])
    return cryptoss

@st.cache
def getAllPairSymbolsOfBinance():
    binance = ccxt.binance()
    symbols = list(binance.load_markets().keys())
    symbols = [symbol.replace('/', '') for symbol in symbols if symbol.endswith('USDT')]
    return symbols

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
        st.warning(f"La crypto {crr} n’existe pas")
    else :
        if(liste_crypto.count(crr[:-4])):
            if(cols2[2].button("Delete it from List")):
                liste_crypto.remove(crr[:-4])
                newcrr = ','.join(liste_crypto)
                con.updatePairSymbolsBinance(newcrr)
                st.success(f"{crr[:-4]} a été supprimé de la liste")

        else:
            if (cols2[2].button("Add it to List")):
                liste_crypto.append(crr[:-4])
                newcrr = ','.join(liste_crypto)
                con.updatePairSymbolsBinance(newcrr)
                st.success(f"{crr[:-4]} a été ajouté à la liste")




cols3 = st.columns(7)
for i in range(len(liste_crypto)):
    cols3[i%7].write(liste_crypto[i])

