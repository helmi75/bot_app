import streamlit as st
from createbot import Users, CreateBot
import auth
from bdd_communication import ConnectBbd
from pass_secret import mot_de_passe
# import pyautogui

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

st.title("Creation D'un Bot")

if authentication_status:
    if not maintenance :
        if con.get_maintenance_setting()[0][0]:
            st.warning('''The page is in maintenance!''')
        with st.expander("Creat a new bot", expanded=True):
            try:
                name_robot = ["Trix", "Cocotier"]
                selection_bot = st.selectbox("choose your Bot", name_robot, key="selection_bot")

                if selection_bot == "Trix":
                    # front entry
                    bot_name = st.text_input("Entrer the bot name ", key="trix_name")
                    email = st.text_input("Entrer your email ", key="email",
                                          value=authenticator.credentials['usernames'][username]['email'])
                    api_key = st.text_input("enter your api_key", key="api_key")
                    secret_key = st.text_input("enter  secret key", key="secret_key")
                    sub_account = st.text_input("Subaccount", key="sub_account")
                    col1, col2, col3 = st.columns(3)
                    pair_symbol = col1.text_input("FTX Pair symbol", value="ETH/USD", placeholder="i.e  BTC/USD",
                                                  key="pair_symbol")
                    trix_lenght = col2.number_input("Trix Lenght", value=9, key="trix_length")
                    trix_signal = col3.number_input("Trix Signal", value=21, key="trix_signal")
                    stoch_top = col1.number_input("Stoch Top", value=0.88, key="stoch_top")
                    stoch_bottom = col2.number_input("Stoch Bottom", value=0.15, key="stoch_bottom")
                    stoch_rsi = col3.number_input("Stoch RSI", value=13, key="stoch_rsi")

                if selection_bot == "Cocotier":
                    bot_name = st.text_input("Entrer the bot name ", key="cocotier_name")
                    email = st.text_input("Entrer your email ", key="cocotier_email")
                    api_key = st.text_input("enter your api_key", key="cocotier_api_key")
                    secret_key = st.text_input("enter  secret key", key="secret_key")

                user = Users(name, email)
                bot = CreateBot(user, bot_name, selection_bot, con)

                if st.button('Create this bot', key="createBot"):
                    #  create  bot with a personal data
                    st.write("nom:", user.name)
                    st.write("email:", user.email)
                    # encode_message(self, password)
                    # bot.encrypt_message(frenet_key, message)
                    st.write("secret key:", secret_key)
                    st.write("secret key:", api_key)

                    bot.create__bot(
                        selection_bot, bot_name, user.get_email(),
                        api_key, secret_key, sub_account, pair_symbol, trix_lenght, trix_signal, stoch_top,
                        stoch_bottom,
                        stoch_rsi)
                    # pyautogui.hotkey('ctrl', 'F5')
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
