from Users import Users
import auth
from utilities.bdd_communication import *
from pass_secret import mot_de_passe
import numpy as np
from ProjectSettings import *

pwd = mot_de_passe
con = ConnectBbd('localhost', '3306', 'root', pwd, 'cryptos', 'mysql_native_password')

def choix_market():
    listacrypto = con.getAllPairSymbolsBinance()[0][0].split(',')
    liste_crypto = np.array(listacrypto)
    cols3 = st.columns(5)
    lista = [x for x in liste_crypto]
    for i in range(len(liste_crypto)):
        lista[i] = cols3[i % 5].checkbox(liste_crypto[i])
    liste_boolean = np.array(lista)
    return liste_crypto[liste_boolean]

def choix_marketBybit():
    listacrypto = con.getAllPairSymbolsBybit()[0][0].split(',')
    liste_crypto = np.array(listacrypto)
    cols3 = st.columns(5)
    lista = [x for x in liste_crypto]
    for i in range(len(liste_crypto)):
        lista[i] = cols3[i % 5].checkbox(liste_crypto[i])
    liste_boolean = np.array(lista)
    return liste_crypto[liste_boolean]

def convertListToString(lista):
    ch = ""
    for i in lista :
        ch+=i+","
    return ch[:-1]

def addTrixForm():
    bot_name = st.text_input("Entrer the bot name ", key="trix_name")
    email = st.text_input("Entrer your email ", key="email",
                          value=authenticator.credentials['usernames'][username]['email'])
    api_key = st.text_input("enter your api_key", key="api_key")
    secret_key = st.text_input("enter  secret key", key="secret_key")
    sub_account = st.text_input("Subaccount", key="sub_account")
    col1, col2, col3 = st.columns(3)
    pair_symbol = col1.text_input("Pair symbol", value="ETH/USDT", placeholder="i.e  BTC/USDT",
                                  key="pair_symbol")
    trix_lenght = col2.number_input("Trix Lenght", value=9, key="trix_length")
    trix_signal = col3.number_input("Trix Signal", value=21, key="trix_signal")
    stoch_top = col1.number_input("Stoch Top", value=0.88, key="stoch_top")
    stoch_bottom = col2.number_input("Stoch Bottom", value=0.15, key="stoch_bottom")
    stoch_rsi = col3.number_input("Stoch RSI", value=13, key="stoch_rsi")
    delta_hour = "None"
    n_i = "None"
    return bot_name,email,api_key,secret_key,sub_account,pair_symbol,trix_lenght,trix_signal,stoch_top,stoch_bottom,stoch_rsi,delta_hour,n_i

def addCocotierForm(selection_bot):
    bot_name = st.text_input("Entrer the bot name ", key="cocotier_name")
    email = st.text_input("Entrer your email ", key="cocotier_email",
                          value=authenticator.credentials['usernames'][username]['email'])
    api_key = st.text_input("enter your api_key", key="cocotier_api_key")
    secret_key = st.text_input("enter  secret key", key="secret_key")
    sub_account = st.text_input("Subaccount", key="sub_account")
    st.write("Selectionner le pair symbol")
    if selection_bot == "Cocotier ByBit":
        pair_symbol = convertListToString(choix_marketBybit())
    else :
        pair_symbol = convertListToString(choix_market())
    delta_hour = st.selectbox('Selectionner une plage horaire', ['2h', '4h', '6h', '8h', '12h'],
                              key="delta_hour")
    n_i = st.radio("Selectionner le type computing", ("N", "N-1", "N-2"),
                   horizontal=True, key="n_i")
    trix_lenght = "None"
    trix_signal = "None"
    stoch_top = "None"
    stoch_bottom = "None"
    stoch_rsi = "None"
    return bot_name,email,api_key,secret_key,sub_account,pair_symbol,delta_hour,n_i,trix_lenght,trix_signal,stoch_top,stoch_bottom,stoch_rsi

st.set_page_config(
    page_title= page_title,
    page_icon= page_icon,
)

st.title(page_title)

authenticator = auth.auth_data()
name, authentication_status, username = authenticator.login('Login', 'main')
maintenance = con.get_maintenance_setting()[0][0] and username != "helmichiha"

st.title("Creation D'un Bot")

if authentication_status:
    if not maintenance:
        if con.get_maintenance_setting()[0][0]:
            st.warning('''The page is in maintenance!''')
        with st.expander("Creat a new bot", expanded=True):
            try:
                name_robot = ["Cocotier Binance","Cocotier ByBit","Trix Binance","Trix Bybit","Trix FTX","Trix Kucoin"]
                selection_bot = st.selectbox("choose your Bot", name_robot, key="selection_bot")

                if selection_bot == "Trix FTX":
                    bot_name, email, api_key, secret_key, sub_account, pair_symbol, trix_lenght, \
                        trix_signal, stoch_top, stoch_bottom, stoch_rsi, \
                        delta_hour, n_i = addTrixForm()
                if selection_bot == "Trix Binance":
                    bot_name, email, api_key, secret_key, sub_account, pair_symbol, trix_lenght, \
                        trix_signal, stoch_top, stoch_bottom, stoch_rsi, \
                        delta_hour, n_i = addTrixForm()
                if selection_bot == "Trix Bybit":
                    bot_name, email, api_key, secret_key, sub_account, pair_symbol, trix_lenght, \
                        trix_signal, stoch_top, stoch_bottom, stoch_rsi, \
                        delta_hour, n_i = addTrixForm()
                if selection_bot == "Trix Kucoin":
                    bot_name, email, api_key, secret_key, sub_account, pair_symbol, trix_lenght, \
                        trix_signal, stoch_top, stoch_bottom, stoch_rsi, \
                        delta_hour, n_i = addTrixForm()
                if selection_bot == "Cocotier Binance":
                    bot_name,email,api_key,secret_key,sub_account,pair_symbol,delta_hour,n_i,\
                        trix_lenght,trix_signal,stoch_top,stoch_bottom,stoch_rsi = addCocotierForm(selection_bot)
                if selection_bot == "Cocotier ByBit":
                    bot_name, email, api_key, secret_key, sub_account, pair_symbol, delta_hour, n_i, \
                        trix_lenght, trix_signal, stoch_top, stoch_bottom, stoch_rsi = addCocotierForm(selection_bot)

                user = Users(name, email)
                # bot = CreateBot(user, bot_name, selection_bot, con)

                if st.button('Create this bot', key="createBot"):
                    #  create  bot with a personal data
                    st.write("Nom:", user.name)
                    st.write("Email:", user.email)
                    # encode_message(self, password)
                    # bot.encrypt_message(frenet_key, message)
                    st.write("Pair Symbol:", pair_symbol)

                    statut_creat_bot = con.create__bot(selection_bot, bot_name, user.get_email(),
                                                       api_key, secret_key, sub_account, pair_symbol,
                                                       trix_lenght, trix_signal, stoch_top, stoch_bottom,
                                                       stoch_rsi, delta_hour, n_i)
                    if statut_creat_bot:
                        st.success("Bot created")
                    else:
                        st.error("Ouch /:\nThere is some problem! Please contact the Engineer!")

            except Exception as e:
                st.exception(e)
    else:
        st.title('''Please Hold on and visit us next time!''')
        st.warning('''The page is in maintenance!''')

        st.image(
            "https://img.freepik.com/premium-vector/robot-android-with-claw-hands-interface-isolated-cartoon-icon-vector-digital-character-kids-toy-white-robotic-friendly-bot-repair-machine-artificial-intelligence-electronic-space-automaton_53500-1001.jpg",
            use_column_width=False)
elif not authentication_status:
    st.error('Username/password is incorrect')
elif authentication_status is None:
    st.warning('Please enter your username and password')
