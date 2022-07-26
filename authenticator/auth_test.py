import streamlit as st
import streamlit_authenticator as stauth
from streamlit_authenticator import Authenticate
import yaml

with open('./config.yaml', 'r') as file:
        config = yaml.safe_load(file)
	#config = yaml.load(file, SafeLoader)

authenticator = Authenticate(
    config['credentials'],
    config['cookie']['name'],
    config['cookie']['key'],
    config['cookie']['expiry_days'],
    config['preauthorized']
)

name, authentication_status, username = authenticator.login('Login', 'main')
if authentication_status:
    authenticator.logout('Logout', 'main')
    st.write(f'Welcome *{name}*')
    st.title('Some content')
elif authentication_status == False:
    st.error('Username/password is incorrect')
elif authentication_status == None:
    st.warning('Please enter your username and password')
st.write(name,authentication_status, username )
print (name,authentication_status, username )
st.write(authenticator.credentials['usernames'][username]['adresse'])
