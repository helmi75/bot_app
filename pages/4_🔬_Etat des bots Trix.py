import streamlit as st
import auth
from bdd_communication import ConnectBbd
import pandas as pd
import plotly.express as px
from pass_secret import mot_de_passe

st.set_page_config(
    page_title="Cocobots",
    page_icon="code.png",
)

st.title("Cocobots")


pwd = mot_de_passe
authenticator = auth.auth_data()
name, authentication_status, username = authenticator.login('Login', 'main')
con = ConnectBbd('localhost', '3306', 'root', pwd, 'cryptos', 'mysql_native_password')
maintenance = con.get_maintenance_setting()[0][0] and username != "helmichiha"

st.title("Etat des Bots")



def status_bots(df_result,wallet):
    df_result = df_result[df_result["transaction"]!="none"]
    list_satus_bot = [ df_result[df_result['nom_bot']==bot].iloc[-1:] for bot in df_result['nom_bot'].unique()]
    df_status_bot = pd.concat(list_satus_bot)[['date','nom_bot','pair_symbol','status_bot','transaction','user_id','type_bot']]
    for i ,transaction in zip(df_status_bot["transaction"].index , df_status_bot["transaction"]):
        if transaction=="buy":
            df_status_bot["transaction"].loc[i] = df_status_bot["pair_symbol"].loc[i][:-4]
        else:
            df_status_bot["transaction"].loc[i] = "USD"
    df_status_bot = df_status_bot.rename(columns ={"transaction":"status_trix"})
    df_status_bot["Exchange wallet"] = wallet.values()
    return df_status_bot
@st.cache(suppress_st_warning=True)
def init():
    if authentication_status:
        if not maintenance :
            if con.get_maintenance_setting()[0][0]:
                st.warning('''The page is in maintenance!''')
            try:
                result,wallet = con.get_status()
                df_result = pd.DataFrame(result, columns=['id_execution', 'date', 'pair_symbol', 'status_bot',
                                                          'transaction', 'log_execution.id_bot', 'bot.id_bot',
                                                          'nom_bot', 'user_id', 'type_bot'])
                # display bot status
                st.dataframe(status_bots(df_result,wallet))
            except Exception as e:
                st.write(e)
        else :
            st.title('''Please Hold on and visit us next time!''')
            st.warning('''The page is in maintenance!''')

            st.image(
                "https://img.freepik.com/premium-vector/robot-android-with-claw-hands-interface-isolated-cartoon-icon-vector-digital-character-kids-toy-white-robotic-friendly-bot-repair-machine-artificial-intelligence-electronic-space-automaton_53500-1001.jpg",
                use_column_width=False)
    elif authentication_status == False:
        st.error('Username/password is incorrect')
    elif authentication_status == None:
        st.warning('Please enter your username and password')

init()