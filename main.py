import streamlit as st
from createbot import Users, CreateBot
import os 

def main():
    st.title("Create a bot ")
   
    
    selection_bot = st.selectbox("Bot",  ["Trix","Cocotier"])
    # front entry
    name =st.text_input("Entrer your name")
    email = st.text_input("Entrer your email ")
    api_key = st.text_input("enter your api_key")
    secret_key = st.text_input("enter  secret key")

    user = Users(name, email)
    bot = CreateBot(selection_bot, api_key, secret_key )

       
    if st.button('Create this bot'):     
        #  create  bot with a personal data 
        st.write("nom:", user.name)
        st.write("email:", user.email)
        st.write("secret key:", bot.secret_key)
        st.write("secret key:", bot.api_key)

        

    





if __name__ == "__main__":
    main()
