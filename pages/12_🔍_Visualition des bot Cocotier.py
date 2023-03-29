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

st.title("Visualization des bots Cocotier")


if authentication_status:
    if not maintenance :
        if con.get_maintenance_setting()[0][0]:
            st.warning('''The page is in maintenance!''')
        try:
            list_balences = con.get_balencesCocotier()
            df_balence = pd.DataFrame(list_balences, columns=['dates', 'crypto_wallet', 'nom_bot'])
            fig =px.line(df_balence, x="dates", y=df_balence.columns ,color=df_balence['nom_bot'],title='bots showed by date and wallet')
            st.plotly_chart(fig)
        except Exception as e:
            st.exception(e)
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
