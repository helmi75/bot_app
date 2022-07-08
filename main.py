import streamlit as st
import os 


selection_bot = st.selectbox("Bot",  ["Trix","Bigwill","cocotier"])

if selection_bot == "Trix":
    
    
    if st.button('create bot'):
        st.write("creationde bot ")
