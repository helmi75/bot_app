import streamlit as st
import auth
from utilities.bdd_communication import ConnectBbd
import pandas as pd
from pass_secret import mot_de_passe
from ProjectSettings import  *

st.set_page_config(
    page_title= page_title,
    page_icon= page_icon,
)

st.title(page_title)

pwd = mot_de_passe
authenticator = auth.auth_data()
name, authentication_status, username = authenticator.login('Login', 'main')
con = ConnectBbd('localhost', '3306', 'root', pwd, 'cryptos', 'mysql_native_password')
maintenance = con.get_maintenance_setting()[0][0] and username != "helmichiha"

st.title("Etat des Bots Trix")


def status_bots(df_result):
    # df_result = df_result[df_result["transaction"] != "none"]
    list_satus_bot = [df_result[df_result['nom_bot'] == bot].iloc[-1:] for bot in df_result['nom_bot'].unique()]
    df_status_bot = pd.concat(list_satus_bot)[
        ['date', 'nom_bot', 'pair_symbol', 'status_bot', 'transaction', 'type_bot', 'wallet', 'creation', 'notes']]

    # Add 'min' and 'max' columns
    min_list = []
    max_list = []
    for bot in df_result['id_bot'].unique():
        min_balance = con.get_min_balance(bot)  # Call the new method to get min balance
        max_balance = con.get_max_balance(bot)  # Call the new method to get max balance
        min_list.append(min_balance)
        max_list.append(max_balance)
    df_status_bot['min'] = min_list
    df_status_bot['max'] = max_list

    for i, transaction in zip(df_status_bot["transaction"].index, df_status_bot["transaction"]):
        if transaction == "none":
            df_status_bot["transaction"].loc[i] = "none"
        else:
            df_status_bot["transaction"].loc[i] = transaction
        if transaction == "sell":
            df_status_bot["pair_symbol"].loc[i] = "USDT"
    df_status_bot = df_status_bot.rename(columns={"transaction": "status_trix"})
    df_status_bot = df_status_bot.rename(columns={"type_bot": "exchange"})
    return df_status_bot


def init():
    if authentication_status:
        if not maintenance:
            if con.get_maintenance_setting()[0][0]:
                st.warning('''The page is in maintenance!''')
            try:
                result = con.get_statusTrix()
                df_result = pd.DataFrame(result, columns=['date', 'wallet', 'status_bot',
                                                          'transaction', 'nom_bot', 'type_bot', 'pair_symbol','creation','notes','id_bot'])
                # display bot status
                df_result['type_bot'] = df_result['type_bot'].str[5:]
                st.dataframe(status_bots(df_result))
            except Exception as e:
                st.exception(e)
        else:
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
