import os
import base64
from pytz_deprecation_shim import NonExistentTimeError
import streamlit as st 
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

class CreateBot :
    def __init__(self, name_bot, secret_key, api_key, subaccount=None, params=None):
        self.name_bot = name_bot
        self.api_key = api_key
        self.secret_key = secret_key
        self.subaccount = subaccount  
        self.params = params   

    def get_name_bot(self):
        return self.name_bot
    
    def get_api_key(self):
        return self.api_key
    
    def get_secret_key(self):
        return self.secret_key

    def import_template(self, file):
        pass  
    
    def create_bot(self, path, user):
        # create bot of trix algorith
        if self.name_bot ==  "Trix":
            path_trix = path+ "/bots/trix/"
            st.write(f"cree un bot trix dans {path_trix} ")
            if not os.path.exists(f"{path_trix}{user.get_name()}/_bot"):
                try :
                    os.makedirs(path_trix + user.get_name()+'_bot')
                    st.success("bot creted")
                except FileExistsError :
                    st.warning("this bot exist yet")
                
            

        # creat a bot  of cocotier alghorithm 
        if self.name_bot == "Cocotier":
            path_cocotier= path+ "/bots/cocotier/"
            st.write(f"cree un bot Cocotier dans {path_cocotier}")
            print(Users.get_name)
            if not os.path.exists(f"{path_cocotier}{user.get_name()}/_bot"):
                       os.makedirs(path_cocotier + user.get_name()+'_bot')
            else:
                    st.error("ce bot existe déja ")						
        return print("bot created ")

    

    
    
    def encode_message_with_pwd(self, password):
        """ 
        Crypt a message with a custom password 
        arg: str 
        return : cryptography.fernet.Fernet object       
        """
        self.bytpassword =password.encode('utf-8')
        salt = os.urandom(16)
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=390000,
        )
        key = base64.urlsafe_b64encode(kdf.derive(self.bytpassword))
        frenet_key = Fernet(key)
        return frenet_key 
    
    def encrypt_message(frenet_key, message):
        """
        Crypt a meesage with encrypted frenet object and return a byte type token 
        Agr : frenet_key-> frenet object, message :str 
        Return token : <class 'bytes'>
        """
        token = frenet_key.encrypt(message.encode('utf-8'))
        return token

    def decode_message(frenet_key, token):
        """
        Decode a message with frenet object and  a str type token 
        Agr :  frenet_key : frenet object, token : <class 'bytes'>
        Return : str 
         """
        return frenet_key.decrypt(token).decode('utf-8')  
  
    # encode message : str
    def encode_message(self, message, key_to_crypt): 
        self.fernet = Fernet(key_to_crypt)     
        encMessage = self.fernet.encrypt(message.encode())
        return encMessage

    # décode message : str
    def decode_pwd(self, encMessage, key_to_decrypt):
        self.fernet = Fernet(key_to_decrypt) 
        decMessage = self.fernet.decrypt(encMessage).decode() 
        return decMessage        
                
class Users :
    def __init__(self, name, email):
        self.name = name
        self.email = email        

    def get_name(self):
        return self.name
    
    def get_email(self):
        return self.email 