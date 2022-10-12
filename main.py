import streamlit as st
from createbot import Users, CreateBot
import auth
from bdd_communication import ConnectBbd
import pandas as pd
import plotly.express as px
#import pyautogui


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
    name, authentication_status, username, password  = authenticator.login('Login', 'main')
    if authentication_status:
        authenticator.logout('Logout', 'main')
        st.write(f'bienvenue *{name}* à votre espace crypto ')
        st.title('espace perso')
    elif authentication_status == False:
        st.error('Username/password is incorrect')
    elif authentication_status == None:
        st.warning('Please enter your username and password')
    if authentication_status:
        st.write(authenticator.credentials['usernames'][username]['adresse'])
        st.write(authenticator.credentials['usernames'][username]['CP'])

    # creation bot
    if authentication_status:
        with st.expander("Creat a new bot", expanded=False):
            try:
                name_robot = ["Trix", "Cocotier"]
                selection_bot = st.selectbox("choise your Bot", name_robot, key="selection_bot")

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
                    #pyautogui.hotkey('ctrl', 'F5')
            except Exception as e:
                st.write(e)

    if authentication_status:
        with st.expander("visulation de vos bot   ", expanded=False):
            try:
                list_balences = con.get_balences()
                balences_data_frame_columns = ['dates', 'crypto_wallet', 'nom_bot']
                balences_data_frame = pd.DataFrame(columns=balences_data_frame_columns)
                for balence in list_balences:
                    balences_data_frame.loc[len(balences_data_frame.index)] = balence
                balences_data_frame["dates"] = pd.to_datetime(balences_data_frame['dates'])
                balences_data_frame["crypto_wallet"] = pd.to_numeric(balences_data_frame['crypto_wallet'])
                balence_bot_name_dictionnaire = {}
                for bot_name in balences_data_frame['nom_bot'].unique():
                    balence_bot_name_dictionnaire_dataframe_columns = ['dates', bot_name]
                    balence_bot_name_dictionnaire_dataframe_values = pd.DataFrame(
                        columns=balence_bot_name_dictionnaire_dataframe_columns)
                    balence_bot_name_dictionnaire[bot_name] = balence_bot_name_dictionnaire_dataframe_values
                for bot in balences_data_frame.values:
                    for balence_bot_name_dictionnaire_keys, balence_bot_name_dictionnaire_values in balence_bot_name_dictionnaire.items():
                        if (bot[2] == balence_bot_name_dictionnaire_keys):
                            balence_bot_name_dictionnaire_values.loc[
                                len(balence_bot_name_dictionnaire_values.index)] = [bot[0], bot[1]]
                balence_bots_clean_dataframe = pd.concat(list(balence_bot_name_dictionnaire.values()))
                balence_bots_clean_dataframe = balence_bots_clean_dataframe.sort_values('dates', ignore_index=True)
                balence_bots_clean_dataframe = balence_bots_clean_dataframe.fillna(method='ffill')
                balence_bots_clean_dataframe = balence_bots_clean_dataframe.fillna(0)
                fig2 = px.line(balence_bots_clean_dataframe, x="dates", y=balence_bots_clean_dataframe.columns,
                               title='bots showed by date and wallet')
                st.plotly_chart(fig2)
            except Exception as e:
                st.write(e)

    if authentication_status:
        with st.expander("Gestion Des Bots", expanded=False):
            try:
                bots = con.get_bots()
                bot = [bot_item[1] for bot_item in bots]
                if 'my_list' not in st.session_state:
                    st.session_state.my_list = bot

                for index, item in enumerate(st.session_state.my_list):
                    emplacement = st.empty()
                    col1, col2 = emplacement.columns([9, 4])
                    emplacement2 = st.empty()
                    col3, col4 = emplacement2.columns([9, 4])

                    if f'{item}' not in st.session_state:
                        st.session_state[f'{item}'] = False

                    if col2.button("Delete this bot", key=f"but{index}") or st.session_state[f'{item}']:
                        st.error(f"Do you really want to delete {item}")
                        st.session_state[f'{item}'] = True
                        if col3.button("Confirm Delete"):
                            del st.session_state.my_list[index]
                            st.write(f"bot {item} deleted!")
                            delBot(bots[index][0])
                            #pyautogui.hotkey("ctrl", "F5")
                        if col4.button("Cancel"):
                            pass
                    if len(st.session_state.my_list) > index:
                        col1.markdown(f'Bot : **{item}**.', unsafe_allow_html=True)
                    else:
                        emplacement.empty()
            except Exception as e:
                st.write(e)

    if authentication_status:
        with st.expander("Etat des Bots", expanded=False):
            try:
                result = con.get_status()
                df_result = pd.DataFrame(result, columns =['id_execution','date','pair_symbol','status_bot',
                                                           'transaction','log_execution.id_bot','bot.id_bot',
                                                           'nom_bot','user_id','type_bot'])
                list_satus_bot = [ df_result[df_result['nom_bot']==bot].iloc[-1:] for bot in df_result['nom_bot'].unique()]
                #for bot in df_result['nom_bot'].unique() :
                #    st.write(df_result[df_result['nom_bot']==bot].iloc[-1:])
                df_status_bot = pd.concat(list_satus_bot)[['date','nom_bot','status_bot','transaction','user_id','type_bot']]
                st.dataframe(df_status_bot)
                select_bot = st.selectbox("info bot 10 dernière heures", df_result['nom_bot'].unique())
                df_selected_bot = df_result[df_result['nom_bot']==select_bot]
                #st.dataframe(df_selected_bot)
                st.write(df_selected_bot[['date','nom_bot','status_bot','transaction','user_id','type_bot']].iloc[-5:])
            except Exception as e :
                st.write(e)




if __name__ == "__main__":
    main()
