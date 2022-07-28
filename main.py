import streamlit as st
from createbot import Users, CreateBot
import auth
import os 


def main():
    st.image("https://upload.wikimedia.org/wikipedia/commons/thumb/c/c2/Gnome-stock_person_bot.svg/1200px-Gnome-stock_person_bot.svg.png", width=200, use_column_width=False)
    st.title("Cocobots")
    authenticator = auth.auth_data()
    
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
                name =st.text_input("Entrer your username", value = username)
                email = st.text_input("Entrer your email ")
                api_key = st.text_input("enter your api_key")
                secret_key = st.text_input("enter  secret key")
                subaccount = st.text_input("Subaccount")
                params  =(9, 21, 0.88, 0.15,13)

            if selection_bot == "Cocotier":
                name =st.text_input("Entrer your name", value = username)
                email = st.text_input("Entrer your email ")
                api_key = st.text_input("enter your api_key")
                secret_key = st.text_input("enter  secret key")      

            user = Users(name, email)
            bot = CreateBot(selection_bot, api_key, secret_key)
            
            
            if st.button('Create this bot'):     
                #  create  bot with a personal data             
                
                st.write("nom:", user.name)
                st.write("email:", user.email)

                #encode_message(self, password)
                #bot.encrypt_message(frenet_key, message)

                st.write("secret key:", bot.secret_key)
                st.write("secret key:", bot.api_key)

                bot.create_bot("/home/helmi/backend_crypto", user)
                frenet_message = bot.encode_message_with_pwd(password)
                print(bot.api_key)
                #byte_message = bot.encrypt_message(frenet_message, bot.api_key)
                #st.write(byte_message)
                #st.write(bot.encode_message(api_key, ))
                #st.write(bot.decode_pwd(bot.encode_message(bot.api_key, password)))


                #st.write(bot.create_bot("/home/helmi/backend_crypto",user))
    if authentication_status == True:
        with st.expander("visulation de vos bot   ", expanded=False):
            st.write( "partie pour visualsier les bots ")
if __name__ == "__main__":
    
    main()
    


