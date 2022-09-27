import streamlit as st
from createbot import Users, CreateBot
import auth
from  bdd_communication import ConnectBbd
import os 


def main():
    st.image("https://upload.wikimedia.org/wikipedia/commons/thumb/c/c2/Gnome-stock_person_bot.svg/1200px-Gnome-stock_person_bot.svg.png",
              width=200,
              use_column_width=False)
    st.title("Cocobots")
    authenticator = auth.auth_data()
    con = ConnectBbd( 'localhost', '3306', 'root', 'Magali_1984','cryptos', 'mysql_native_password')
    name, authentication_status, username, password = authenticator.login('Login', 'main')
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
            name_robot = ["Trix","Cocotier"]
            selection_bot = st.selectbox("choise your Bot", name_robot)
            if selection_bot == "Trix":
            # front entry
                bot_name =st.text_input("Entrer the bot name ")
                email = st.text_input("Entrer your email ", value = authenticator.credentials['usernames'][username]['email'])
                api_key = st.text_input("enter your api_key")
                secret_key = st.text_input("enter  secret key")
                sub_account = st.text_input("Subaccount")
                col1, col2, col3 = st.columns(3)
                pair_symbol = col1.text_input("FTX Pair symbol",value="ETH/USDT", placeholder="i.e  BTC/USDT")
                trix_lenght =  col2.number_input("Trix Lenght", value=9)
                trix_signal =  col3.number_input("Trix Signal", value=21)
                stoch_top =  col1.number_input("Stoch Top", value=0.88)
                stoch_bottom = col2.number_input("Stoch Bottom", value=0.15)
                stoch_rsi =  col3.number_input("Stoch RSI", value=13)


            if selection_bot == "Cocotier":
                subbot_name =st.text_input("Entrer the bot name ")
                email = st.text_input("Entrer your email ")
                api_key = st.text_input("enter your api_key")
                secret_key = st.text_input("enter  secret key")      

            user = Users(name, email)
            bot = CreateBot(user, selection_bot, con)
            
            
            if st.button('Create this bot'):     
                #  create  bot with a personal data              
                st.write("nom:", user.name)
                st.write("email:", user.email)
                #encode_message(self, password)
                #bot.encrypt_message(frenet_key, message)
                st.write("secret key:", secret_key)
                st.write("secret key:", api_key)


                bot.create_trix_bot("/home/anisse9/bot_app/user_bot", user.get_name(), api_key, secret_key, sub_account, pair_symbol,
                                     trix_lenght, trix_signal,stoch_top,  stoch_bottom, stoch_rsi)

                frenet_message = bot.encode_message_with_pwd(password)
                print(bot.api_key)
                #byte_message = bot.encrypt_message(frenet_message, bot.api_key)
                #st.write(byte_message)
                #st.write(bot.encode_message(api_key, ))
                #st.write(bot.decode_pwd(bot.encode_message(bot.api_key, password)))


                #st.write(bot.create_bot("/home/helmi/backend_crypto",user))
    if authentication_status == True:
        with st.expander("visulation de vos bot   ", expanded=False):
            st.write( "partie pour visualsier les bots à faire par  (Mahdi) ")
if __name__ == "__main__":
    
    main()
    


