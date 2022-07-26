import streamlit as st
import streamlit_authenticator as stauth
import yaml

def  auth_data(): 
    with open('./authenticator/config.yaml','r') as file:
        config = yaml.safe_load(file)
	#config = yaml.load(file, SafeLoader)

    authenticator = stauth.Authenticate(
        config['credentials'],
        config['cookie']['name'],
        config['cookie']['key'],
        config['cookie']['expiry_days'],
        config['preauthorized']
    )
    return authenticator