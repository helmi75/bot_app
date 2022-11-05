import streamlit as st
import auth
from bdd_communication import ConnectBbd
import pandas as pd
import plotly.express as px
from pass_secret import mot_de_passe
import pyautogui

pwd = mot_de_passe
authenticator = auth.auth_data()
name, authentication_status, username = authenticator.login('Login', 'main')
con = ConnectBbd('localhost', '3306', 'root', pwd, 'cryptos', 'mysql_native_password')
maintenance = con.get_maintenance_setting()[0][0] and username != "helmichiha"
st.title("Gestion Des Bot")


def delBot(bot_id):
    con = ConnectBbd('localhost', '3306', 'root', pwd, 'cryptos', 'mysql_native_password')
    con.delete_bot(bot_id)


def modifBot(bot_id):
    con = ConnectBbd('localhost', '3306', 'root', pwd, 'cryptos', 'mysql_native_password')
    type_bot = con.get_type_bot(bot_id)[0][0]
    if type_bot == "trix":
        modifierTrixBot(bot_id)
    elif type_bot == "cocotier":
        st.warning("Still in developping")


def modifierTrixBot(bot_id):
    con = ConnectBbd('localhost', '3306', 'root', pwd, 'cryptos', 'mysql_native_password')
    trix_bot = con.get_trix_bot(bot_id)
    st.title(f"Modifing  : {trix_bot[0][11]}")
    api_key = st.text_input("enter your api_key", key="api_key_trix", value=trix_bot[0][1])
    secret_key = st.text_input("enter  secret key", key="secret_key_trix", value=trix_bot[0][2])
    sub_account = st.text_input("Subaccount", key="sub_account_trix", value=trix_bot[0][3])
    col1, col2, col3 = st.columns(3)
    pair_symbol = col1.text_input("FTX Pair symbol", value=f"{trix_bot[0][4].upper()}/USDT",
                                  placeholder="i.e  BTC/USDT",
                                  key="pair_symbol_trix")
    trix_lenght = col2.number_input("Trix Lenght", value=trix_bot[0][5], key="trix_length_trix")
    trix_signal = col3.number_input("Trix Signal", value=trix_bot[0][6], key="trix_signal_trix")
    stoch_top = col1.number_input("Stoch Top", value=trix_bot[0][7], key="stoch_top_trix")
    stoch_bottom = col2.number_input("Stoch Bottom", value=trix_bot[0][8], key="stoch_bottom_trix")
    stoch_rsi = col3.number_input("Stoch RSI", value=trix_bot[0][9], key="stoch_rsi_trix")
    col01, col02 = st.columns([9, 4])
    if col01.button("Apply Changes"):
        con = ConnectBbd('localhost', '3306', 'root', pwd, 'cryptos', 'mysql_native_password')
        pair_symbol = pair_symbol[:-5].lower()
        con.update_trix_bot(bot_id, api_key, secret_key, sub_account, pair_symbol,
                            trix_lenght, trix_signal, stoch_top, stoch_bottom, stoch_rsi)
        pyautogui.hotkey("ctrl", "F5")
    if col02.button("Cancel Changes"):
        pyautogui.hotkey("ctrl", "F5")
        pass


if authentication_status:
    if con.get_maintenance_setting()[0][0]:
        st.warning('''The page is in maintenance!''')
    if not maintenance:
        try:
            bots = con.get_bots()
            bot = [bot_item[1] for bot_item in bots]
            if 'my_list' not in st.session_state:
                st.session_state.my_list = bot

            for index, item in enumerate(st.session_state.my_list):
                emplacement = st.empty()
                col1, col2, col22 = emplacement.columns([9, 3, 3])
                emplacement2 = st.empty()
                col3, col4 = emplacement2.columns([9, 4])

                if f'{item}' not in st.session_state:
                    st.session_state[f'{item}'] = False
                    st.session_state[f'E{item}'] = False

                if col2.button("Delete this bot", key=f"but{index}") or st.session_state[f'{item}']:
                    st.warning(f"Do you really want to delete {item}")
                    st.session_state[f'{item}'] = True
                    st.session_state[f'E{item}'] = False
                    if col3.button("Confirm Delete"):
                        del st.session_state.my_list[index]
                        st.write(f"bot {item} deleted!")
                        delBot(bots[index][0])
                        pyautogui.hotkey("ctrl", "F5")
                    if col4.button("Cancel"):
                        pyautogui.hotkey("ctrl", "F5")
                if col22.button("Edit this bot", key=f"ed{index}") or st.session_state[f'E{item}']:
                    modifBot(bots[index][0])
                    st.session_state[f'E{item}'] = True
                    st.session_state[f'{item}'] = False
                if len(st.session_state.my_list) > index:
                    col1.markdown(f'Bot : **{item}**.', unsafe_allow_html=True)
                else:
                    emplacement.empty()
        except Exception as e:
            print(e)
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