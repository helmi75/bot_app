import streamlit as st
import auth
from bdd_communication import ConnectBbd
import pandas as pd
import plotly.express as px
from pass_secret import mot_de_passe

pwd = mot_de_passe
authenticator = auth.auth_data()
name, authentication_status, username = authenticator.login('Login', 'main')
con = ConnectBbd('localhost', '3306', 'root', pwd, 'cryptos', 'mysql_native_password')
maintenance = con.get_maintenance_setting()[0][0] and username != "helmichiha"

st.title("Visualization de vos bot trix normalisé")


if authentication_status:
    if not maintenance :
        if con.get_maintenance_setting()[0][0]:
            st.warning('''The page is in maintenance!''')
        try:
            list_balences = con.get_crypto_pourcentage()
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
            fig2 = px.line(balence_bots_clean_dataframe, x="dates", y=balence_bots_clean_dataframe.columns,
                           title='bots showed by date and wallet')
            st.plotly_chart(fig2)
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