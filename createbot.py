import os
import base64
from pytz_deprecation_shim import NonExistentTimeError
import streamlit as st
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import shutil




class CreateBot :
    def __init__(self, user, name_bot, cnx):
        self.name_bot = name_bot
        self.cnx = cnx
        self.user = user

    def get_name_bot(self):
        return self.name_bot

    def import_template(self, file_source, file_destination):
        """
        copyt the template trix  robot from the template file to the detination file
        """
        source= bytes(file_source, 'utf-8')
        destination = bytes(file_destination, 'utf-8')
        shutil.copyfile(source, destination)

    def create_trix_bot(self, path, api_key, secret_key, subbot_name=None, pair_symbol=None, 
                        sub_account=None,trix_lenght=None,trix_signal=None,
                        stoch_top=None, stoch_bottom=None ,stoch_rsi=None ):
        # create bot of trix algorith
        if self.name_bot ==  "Trix":
            path_trix = path+ f"/{self.user.get_email()}/ftx/trix/"
            st.write(f"cree un bot trix dans {path_trix} ")
            pair_symbol = pair_symbol[:3].lower()
            if not os.path.exists(f"{path_trix}/{pair_symbol}/{sub_account}/_bot"):
                try :
                    os.makedirs(f"{path_trix}/{pair_symbol}/{sub_account}_bot")
                    st.success("bot creted")
                except FileExistsError :
                    st.warning("this bot exist yet")

        # copy trix algotirh template files into the  production environnement
        self.import_template(file_source = './templates/trix_template/TrixFtxlive.py',
                            file_destination = f'./user_bot/{self.user.get_email()}/ftx/trix/{pair_symbol}/{sub_account}_bot/{pair_symbol}_TrixFtxlive.py')

        self.import_template(file_source = './templates/trix_template/config.py',
                            file_destination = f'./user_bot/{self.user.get_email()}/ftx/trix/{pair_symbol}/{sub_account}_bot/{pair_symbol}_config.py')
        
        # send data to the databse 
        self.cnx.insert_new_trix_bot(self.user.get_name(),self.name_bot,
                                     api_key, secret_key, sub_account, pair_symbol,
                                     trix_lenght, trix_signal, stoch_top, stoch_bottom, stoch_rsi )
        # creat a bot of cocotier alghorithm
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
