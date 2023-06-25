import auth
from utilities.bdd_communication import *
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
st.title("Gestion Des Bot Trix")


def delBot(bot_id):
    con = ConnectBbd('localhost', '3306', 'root', pwd, 'cryptos', 'mysql_native_password')
    con.delete_bot(bot_id)


def modifierTrixBot(bot_id):
    con = ConnectBbd('localhost', '3306', 'root', pwd, 'cryptos', 'mysql_native_password')
    trix_bot = con.get_trix_bot(bot_id)
    st.title(f"Modifing  : {trix_bot[0][11]}")
    apii = trix_bot[0][1]
    secrets = trix_bot[0][2]
    apii, secrets = degenerateApiSecret(apii, secrets, bot_id)
    apiii  = apii[0]+apii[1]+"**************"+apii[-2]+apii[-1]
    secretss = secrets[0]+secrets[1]+"**************"+secrets[-2]+secrets[-1]
    api_key = st.text_input("enter your api_key", key="api_key_trix", value=apiii)
    secret_key = st.text_input("enter  secret key", key="secret_key_trix", value=secretss)
    sub_account = st.text_input("Subaccount", key="sub_account_trix", value=trix_bot[0][3])
    col1, col2, col3 = st.columns(3)
    pair_symbol = col1.text_input("Pair symbol", value=f"{trix_bot[0][4].upper()}/USDT",
                                  placeholder="i.e  BTC/USDT",
                                  key="pair_symbol_trix")
    trix_lenght = col2.number_input("Trix Lenght", value=trix_bot[0][5], key="trix_length_trix")
    trix_signal = col3.number_input("Trix Signal", value=trix_bot[0][6], key="trix_signal_trix")
    stoch_top = col1.number_input("Stoch Top", value=trix_bot[0][7], key="stoch_top_trix")
    stoch_bottom = col2.number_input("Stoch Bottom", value=trix_bot[0][8], key="stoch_bottom_trix")
    stoch_rsi = col3.number_input("Stoch RSI", value=trix_bot[0][9], key="stoch_rsi_trix")
    col01, col02 = st.columns([9, 4])
    delta_hour = "None"
    n_i = "None"
    if col01.button("Apply Changes"):
        con = ConnectBbd('localhost', '3306', 'root', pwd, 'cryptos', 'mysql_native_password')
        pair_symbol = pair_symbol[:-5].lower()
        if (api_key == apiii):
            api_key = apii
        if (secret_key == secretss):
            secret_key = secrets
        api_key, secret_key = generateApiSecret(api_key, secret_key, bot_id)
        con.update_trix_bot(bot_id, api_key, secret_key, sub_account, pair_symbol,
                            trix_lenght, trix_signal, stoch_top, stoch_bottom, stoch_rsi)
        # pyautogui.hotkey("ctrl", "F5")
        st.success("vos changements ont été enregistrés ")
        st.warning("Recharger la page")
    if col02.button("Cancel Changes"):
        # pyautogui.hotkey("ctrl", "F5")
        st.warning("Recharger la page")


if authentication_status:
    if con.get_maintenance_setting()[0][0]:
        st.warning('''The page is in maintenance!''')
    if not maintenance:
        try:
            botsTrix = con.get_botsTrix()
            botTrix = [bot_itemTrix[1] for bot_itemTrix in botsTrix]
            if botsTrix not in st.session_state:
                st.session_state.my_list = botTrix

            for index, item in enumerate(st.session_state.my_list):
                emplacement = st.empty()
                col1, col2, col22, col222 = emplacement.columns([6, 3, 3, 3])
                emplacement2 = st.empty()
                col3, col4 = emplacement2.columns([5, 4])

                stopMarche = con.getStopMarche(botsTrix[index][0])

                if f'{item}' not in st.session_state:
                    st.session_state[f'{item}'] = False
                    st.session_state[f'E{item}'] = False

                if col2.button("Delete this bot", key=f"but{index}") or st.session_state[f'{item}']:
                    st.warning(f"Do you really want to delete {item}")
                    st.session_state[f'{item}'] = True
                    st.session_state[f'E{item}'] = False
                    if col3.button("Confirm Delete"):
                        del st.session_state.my_list[index]
                        st.success(f"bot {item} deleted!")
                        delBot(botsTrix[index][0])
                        # pyautogui.hotkey("ctrl", "F5")
                    if col4.button("Cancel"):
                        pass
                        # pyautogui.hotkey("ctrl", "F5")
                if col22.button("Edit this bot", key=f"ed{index}") or st.session_state[f'E{item}']:
                    modifierTrixBot(botsTrix[index][0])
                    st.session_state[f'E{item}'] = True
                    st.session_state[f'{item}'] = False

                if stopMarche and col222.button("Stop", key=f"stop{index}"):
                    usdtCrypto = con.get_state_vente_achat_trix_By_id(botsTrix[index][0])
                    if usdtCrypto.lower() != "usdt":
                        if botsTrix[index][2].lower() == "Trix FTX".lower():
                            con.vendreTrixFtx(botsTrix[index][0])
                        elif botsTrix[index][2].lower() == "Trix Binance".lower():
                            con.vendreTrixBinance(botsTrix[index][0])
                        elif botsTrix[index][2].lower() == "Trix Bybit".lower():
                            con.vendreTrixBybit(botsTrix[index][0])
                        elif botsTrix[index][2].lower() == "Trix Kucoin".lower():
                            con.vendreTrixKucoin(botsTrix[index][0])
                    con.updateStopMarche(botsTrix[index][0], 0)
                    st.error(f"Le bot {item} est stoppé {usdtCrypto}")
                elif not stopMarche and col222.button("Work", key=f"marche{index}"):
                    con.updateStopMarche(botsTrix[index][0], 1)
                    st.success(f"Le bot {item} est en marche ")

                if len(st.session_state.my_list) > index:
                    col1.markdown(f'Bot : **{item}**.', unsafe_allow_html=True)
                else:
                    emplacement.empty()
        except Exception as e:

            st.error("This is an exception ")
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
