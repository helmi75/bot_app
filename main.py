import streamlit as st
import auth
from bdd_communication import ConnectBbd
from pass_secret import mot_de_passe
import pyautogui

pwd = mot_de_passe

st.set_page_config(
    page_title="Cocobots",
    page_icon="code.png",
)

st.title("Cocobots")





def main():
    authenticator = auth.auth_data()
    name, authentication_status, username = authenticator.login('Login', 'main')
    con = ConnectBbd('localhost', '3306', 'root', pwd, 'cryptos', 'mysql_native_password')

    if authentication_status:
        authenticator.logout('Logout', 'main')
    if username == "helmichiha":
        agreed = st.checkbox('Maintenance !')
        if agreed:
            con = ConnectBbd('localhost', '3306', 'root', pwd, 'cryptos', 'mysql_native_password')
            con.update_maintenance_setting()
            pyautogui.hotkey("ctrl", "F5")
    maintenance = con.get_maintenance_setting()[0][0] and username != "helmichiha"
    maintenance=0
    if maintenance:
        st.title('''Please Hold on and visit us next time!''')
        st.warning('''The page is in maintenance!''')
        st.image(
            "https://img.freepik.com/premium-vector/robot-android-with-claw-hands-interface-isolated-cartoon-icon-vector-digital-character-kids-toy-white-robotic-friendly-bot-repair-machine-artificial-intelligence-electronic-space-automaton_53500-1001.jpg",
            use_column_width=False)
    else:
        if con.get_maintenance_setting()[0][0]:
            st.warning('''The page is in maintenance!''')
        st.image(
            "https://upload.wikimedia.org/wikipedia/commons/thumb/c/c2/Gnome-stock_person_bot.svg/1200px-Gnome-stock_person_bot.svg.png",
            width=200,
            use_column_width=False)
        if authentication_status:
            # authenticator.logout('Logout', 'main')
            st.write(f'bienvenue *{name}* à votre espace crypto ')
            st.title('espace perso')
        elif authentication_status == False:
            st.error('Username/password is incorrect')
        elif authentication_status == None:
            st.warning('Please enter your username and password')
        if authentication_status:
            st.write(authenticator.credentials['usernames'][username]['adresse'] + " / Code Postal : " + authenticator.credentials['usernames'][username]['CP'] )



if __name__ == "__main__":
    main()

