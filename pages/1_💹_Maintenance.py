# espace disque  restant + caracteriques du processus
#
# nombre de bot trix actives / nb de bot trix non actives
#
# nb de bot cocotier active / nb de bot cocotier non actives

import streamlit as st
from bdd_communication import ConnectBbd
from pass_secret import mot_de_passe
import psutil

st.set_page_config(
    page_title="Cocobots",
    page_icon="code.png",
)
st.title("Cocobots")
st.title ("Maintenance")


hdd = psutil.disk_usage('/')

st.header (f"Total: {round(hdd.total / (2**30),3)} GB")
st.header  (f"Used: {round(hdd.used / (2**30),3)} GB")
st.header  (f"Free: {round(hdd.free / (2**30),3)} GB")

st.title("-"*30)
con = ConnectBbd('localhost', '3306', 'root', mot_de_passe, 'cryptos', 'mysql_native_password')

nbTrixActive = 0
nbTrixInactive = con.nombreTrixInActive()[0][0]
TrixActive = con.listeTrixActive()
for i in TrixActive :
    try :
        if (con.isONNorOFF(i[0])[0][0] == "OFF"):
            nbTrixInactive+=1
        else:
            nbTrixActive += 1
    except Exception :
        nbTrixInactive += 1
nbCocotierActive = 0
CocotierActive = con.listeCocotierActive()
nbCocotierInActive = con.nombreCocotierInActive()[0][0]
for i in CocotierActive :
    try :
        if (con.isONNorOFF(i[0])[0][0] == "OFF"):
            nbCocotierInActive+=1
        else:
            nbCocotierActive += 1
    except Exception :
        nbCocotierInActive += 1

st.header(f"Nombre de Bot Trix Active : {nbTrixActive}")
st.header(f"Nombre de Bot Trix InActive : {nbTrixInactive}")
st.header(f"Nombre de Bot Cocotier Active : {nbCocotierActive}")
st.header(f"Nombre de Bot Cocotier InActive : {nbCocotierInActive}")
