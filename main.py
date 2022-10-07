import streamlit as st
from createbot import Users, CreateBot
import auth
from bdd_communication import ConnectBbd
import pandas as pd
import plotly.express as px
import pyautogui

def delBot(x):
    con = ConnectBbd('localhost', '3306', 'root', 'Magali_1984', 'cryptos', 'mysql_native_password')
    con.delete_bot(x)


def main():
    st.image(
        "https://upload.wikimedia.org/wikipedia/commons/thumb/c/c2/Gnome-stock_person_bot.svg/1200px-Gnome-stock_person_bot.svg.png",
        width=200,
        use_column_width=False)
    st.title("Cocobots")
    authenticator = auth.auth_data()
    con = ConnectBbd('localhost', '3306', 'root', 'Magali_1984', 'cryptos', 'mysql_native_password')
    password = None
    name, authentication_status, username = authenticator.login('Login', 'main')
    if authentication_status:
        authenticator.logout('Logout', 'main')
        st.write(f'bienvenue *{name}* à votre espace crypto ')
        st.write(password)
        st.title('espace perso')
    elif authentication_status == False:
        st.error('Username/password is incorrect')
    elif authentication_status == None:
        st.warning('Please enter your username and password')
    if authentication_status == True:
        st.write(authenticator.credentials['usernames'][username]['adresse'])
        st.write(authenticator.credentials['usernames'][username]['CP'])

    # creation bot
    if authentication_status == True:
        with st.expander("Creat a new bot", expanded=False):
            name_robot = ["Trix", "Cocotier"]
            selection_bot = st.selectbox("choise your Bot", name_robot)
            if selection_bot == "Trix":
                # front entry
                bot_name = st.text_input("Entrer the bot name ")
                email = st.text_input("Entrer your email ",
                                      value=authenticator.credentials['usernames'][username]['email'])
                api_key = st.text_input("enter your api_key")
                secret_key = st.text_input("enter  secret key")
                sub_account = st.text_input("Subaccount")
                col1, col2, col3 = st.columns(3)
                pair_symbol = col1.text_input("FTX Pair symbol", value="ETH/USDT", placeholder="i.e  BTC/USDT")
                trix_lenght = col2.number_input("Trix Lenght", value=9)
                trix_signal = col3.number_input("Trix Signal", value=21)
                stoch_top = col1.number_input("Stoch Top", value=0.88)
                stoch_bottom = col2.number_input("Stoch Bottom", value=0.15)
                stoch_rsi = col3.number_input("Stoch RSI", value=13)

            if selection_bot == "Cocotier":
                bot_name = st.text_input("Entrer the bot name ")
                email = st.text_input("Entrer your email ")
                api_key = st.text_input("enter your api_key")
                secret_key = st.text_input("enter  secret key")

            user = Users(name, email)
            bot = CreateBot(user, bot_name, selection_bot, con)

            if st.button('Create this bot'):
                #  create  bot with a personal data
                st.write("nom:", user.name)
                st.write("email:", user.email)
                # encode_message(self, password)
                # bot.encrypt_message(frenet_key, message)
                st.write("secret key:", secret_key)
                st.write("secret key:", api_key)

                bot.create__bot(
                    selection_bot, bot_name, user.get_email(),
                    api_key, secret_key, sub_account, pair_symbol, trix_lenght, trix_signal, stoch_top, stoch_bottom,
                    stoch_rsi)

    if authentication_status == True:
        with st.expander("visulation de vos bot   ", expanded=False):
            try:
                myresult2 = con.get_balences()
                column_names2 = ['dates', 'crypto_wallet', 'nom_bot']
                workbook2 = pd.DataFrame(columns=column_names2)
                for i in myresult2:
                    workbook2.loc[len(workbook2.index)] = i
                workbook2["dates"] = pd.to_datetime(workbook2['dates'])
                workbook2["crypto_wallet"] = pd.to_numeric(workbook2['crypto_wallet'])
                list_df2 = {}
                for i in workbook2['nom_bot'].unique():
                    l = ['dates', i]
                    d = pd.DataFrame(columns=l)
                    list_df2[i] = d
                for i in workbook2.values:
                    for j, k in list_df2.items():
                        if (i[2] == j):
                            k.loc[len(k.index)] = [i[0], i[1]]
                dff2 = pd.concat(list(list_df2.values()))
                dff2 = dff2.sort_values('dates', ignore_index=True)
                dff2 = dff2.fillna(method='ffill')
                dff2 = dff2.fillna(0)
                fig2 = px.line(dff2, x="dates", y=dff2.columns, title='bots showed by date and wallet')
                st.plotly_chart(fig2)
            except:
                pass
        with st.expander("Gestion Des Bots   ", expanded=False):
            try:
                bots = con.get_bots()
                bot = [i[1] for i in bots]
                if 'my_list' not in st.session_state:
                    st.session_state.my_list = bot

                for index, item in enumerate(st.session_state.my_list):
                    emp = st.empty()
                    col1, col2 = emp.columns([9, 4])
                    empp = st.empty()
                    col3, col4 = empp.columns([9, 4])

                    if f'{item}' not in st.session_state:
                        st.session_state[f'{item}'] = False

                    if col2.button("Delete this bot", key=f"but{index}") or st.session_state[f'{item}']:
                        st.error(f"Do you really want to delete {item}")
                        st.session_state[f'{item}'] = True
                        if col3.button("Confirm Delete"):
                            del st.session_state.my_list[index]
                            st.write(f"bot {item} deleted!")
                            delBot(bots[index][0])
                            pyautogui.hotkey("ctrl", "F5")

                        if col4.button("Cancel"):
                            pass
                    if len(st.session_state.my_list) > index:
                        col1.markdown(f'Bot : **{item}**.', unsafe_allow_html=True)
                    else:
                        emp.empty()
            except:
                pass


if __name__ == "__main__":
    main()
