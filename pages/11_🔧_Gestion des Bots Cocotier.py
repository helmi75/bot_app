import streamlit as st
import auth
from bdd_communication import *
from pass_secret import mot_de_passe
import numpy as np

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
st.title("Gestion Des Bot Cocotier")


def delBot(bot_id):
    con = ConnectBbd('localhost', '3306', 'root', pwd, 'cryptos', 'mysql_native_password')
    con.delete_bot(bot_id)


def choix_market(list):
    list = list.upper().split(',')
    listacrypto = con.getAllPairSymbolsBinance()[0][0].split(',')
    liste_crypto = np.array(listacrypto)
    cols3 = st.columns(5)
    lista = [x for x in liste_crypto]
    for i in range(len(liste_crypto)):
        lista[i] = cols3[i % 5].checkbox(liste_crypto[i], value=liste_crypto[i] in list)
    liste_boolean = np.array(lista)
    return liste_crypto[liste_boolean]



def convertListToString(lista):
    ch = ""
    for i in lista:
        ch += i + ","
    return ch[:-1]


def modifierCocotierBot(bot_id):
    con = ConnectBbd('localhost', '3306', 'root', pwd, 'cryptos', 'mysql_native_password')
    cocotier_bot = con.get_cocotier_bot(bot_id)
    st.title(f"Modifing  : {cocotier_bot[0][8]}")
    apii = cocotier_bot[0][1]
    secrets = cocotier_bot[0][2]
    apii,secrets = degenerateApiSecret(apii, secrets, bot_id)
    api_key = st.text_input("enter your api_key", key="cocotier_api_key", value=apii)
    secret_key = st.text_input("enter  secret key", key="secret_key", value=secrets)
    sub_account = st.text_input("Subaccount", key="sub_account", value=cocotier_bot[0][3])
    st.write("Selectionner le pair symbol")
    pair_symbol = convertListToString(choix_market(cocotier_bot[0][4]))
    delta_hour = st.selectbox('Selectionner une plage auraire', ['2h', '4h', '6h', '8h', '12h'],
                              key="delta_hour", index=[2, 4, 6, 8, 12].index(cocotier_bot[0][5]))
    n_i = st.selectbox('Selectionner le type computing', ["N", "N-1", "N-2"],
                       key="n_u", index=["n", "n-1", "n-2"].index(cocotier_bot[0][6]))
    trix_lenght = "None"
    trix_signal = "None"
    stoch_top = "None"
    stoch_bottom = "None"
    stoch_rsi = "None"
    col01, col02 = st.columns([9, 4])
    if col01.button("Apply Changes"):
        con = ConnectBbd('localhost', '3306', 'root', pwd, 'cryptos', 'mysql_native_password')
        pair_symbol = pair_symbol.lower()
        n_i = n_i.lower()
        delta_hour = (int)(delta_hour[:-1])
        api_key, secret_key = generateApiSecret(api_key, secret_key, bot_id)
        con.update_Cocotier_bot(bot_id, api_key, secret_key, sub_account, pair_symbol,
                                delta_hour, n_i)
        st.success("vos changements ont été enregistrés ")
        # pyautogui.hotkey("ctrl", "F5")
    if col02.button("Cancel Changes"):
        # pyautogui.hotkey("ctrl", "F5")
        st.warning("Recharger la page")
        pass

if authentication_status:
    if con.get_maintenance_setting()[0][0]:
        st.warning('''The page is in maintenance!''')
    if not maintenance:
        try:
            botsCocotier = con.get_botsCocotier()
            botCocotier = [bot_item[1] for bot_item in botsCocotier]
            if botsCocotier not in st.session_state:
                st.session_state.my_list = botCocotier

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
                        st.success(f"bot {item} deleted!")
                        delBot(botsCocotier[index][0])
                        # pyautogui.hotkey("ctrl", "F5")
                    if col4.button("Cancel"):
                        pass
                        # pyautogui.hotkey("ctrl", "F5")
                if col22.button("Edit this bot", key=f"ed{index}") or st.session_state[f'E{item}']:
                    modifierCocotierBot(botsCocotier[index][0])
                    st.session_state[f'E{item}'] = True
                    st.session_state[f'{item}'] = False
                if len(st.session_state.my_list) > index:
                    col1.markdown(f'Bot : **{item}**.', unsafe_allow_html=True)
                else:
                    emplacement.empty()
        except Exception as e:

            st.error("This is an exception ", e)
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
