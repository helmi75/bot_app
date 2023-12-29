import streamlit as st
import requests
from utilities.bdd_communication import ConnectBbd
from pass_secret import mot_de_passe
from binance.client import Client
from ProjectSettings import  *
import ccxt

st.set_page_config(
    page_title= page_title,
    page_icon= page_icon,
)

st.title(page_title)

st.title("Pool Bybit Pairs Symbol")

con = ConnectBbd('localhost', '3306', 'root', mot_de_passe, 'cryptos', 'mysql_native_password')
liste_crypto = con.getAllPairSymbolsBybit()[0][0].split(',')
@st.cache
def getAllPairSymbolsOfBybit_old():
    cryptoss = []
    url = 'https://api.bybit.com/v2/public/symbols'
    response = requests.get(url)
    exchange_info = response.json()
    for s in exchange_info['result']:
        if s['name'].endswith('USDT'):
            cryptoss.append(s['name'])
    return cryptoss

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
def getAllPairSymbolsOfBybit():
    url = "https://api.bybit.com/v2/public/symbols"
    response = requests.get(url)
    data = response.json()
    symbols = [symbol["name"] for symbol in data["result"]]
    return symbols

@st.cache
def getAllPairSymbolsOfBinance():
    binance = ccxt.binance()
    symbols = list(binance.load_markets().keys())
    symbols = [symbol.replace('/', '') for symbol in symbols if symbol.endswith('USDT')]
    return symbols

# Fonction pour obtenir les symboles spot de Bybit
def get_bybit_spot_symbols():
    bybit = ccxt.bybit({
        'apiKey': "YAhlHZJaBFFr6ixX33",
        'secret': "5zMAhtMZ6MXxtR2p5tcU15x3LyRkYR2jh8Px",
        'enableRateLimit': True,
    })
    markets = bybit.load_markets()
    spot_symbols = [symbol.replace('/', '') for symbol, market in markets.items() if (market['type'] == 'spot') and (symbol.endswith('USDT')) and (not any(char.isdigit() for char in symbol))]
  
    return spot_symbols

# Fonction pour mettre à jour la liste des cryptomonnaies communes
def update_common_symbols():
    binance_symbols = getAllPairSymbolsOfBinance()
    #bybit_symbols = getAllPairSymbolsOfBybit()
    bybit_symbols = get_bybit_spot_symbols()
    
    # Convertir les symboles en ensembles pour faciliter l'intersection
    binance_set = set([symbol[:-4] for symbol in binance_symbols])
    bybit_set = set([symbol[:-4] for symbol in bybit_symbols])

    # Trouver les symboles communs
    common_symbols = binance_set.intersection(bybit_set)

    # Convertir de nouveau au format d'origine si nécessaire
    common_symbols_format_original = sorted([f"{symbol}" for symbol in common_symbols])

    return common_symbols_format_original

# Bouton pour actualiser la liste des cryptomonnaies
if st.button("Actualiser la liste des cryptos"):
    liste_crypto = update_common_symbols()
    newcrr = ','.join(liste_crypto)
    con.updatePairSymbolsBybit(newcrr)
    st.success(f"La liste a été mise à jour avec succès")

# Afficher la liste mise à jour dans des colonnes
cols = st.columns(7)
for i, symbol in enumerate(liste_crypto):
    cols[i % 7].write(symbol)
