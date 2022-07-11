
import os
import streamlit as st 

class CreateBot :
	def __init__(self, name_bot, secret_key, api_key):
		self.name_bot = name_bot
		self.api_key =api_key
		self.secret_key	= secret_key
			

	def get_name_bot(self):
		return self.name_bot
	
	def get_api_key(self):
		return self.api_key
	
	def get_secret_key(self):
		return self.secret_key


	
	def create_bot (self, path):

		if self.name_bot ==  "Trix":
			path_trix = path+ "/trix/"
			st.write(f"cree un bot trix dans {path_trix} ")

			if not os.path.exists("/home/helmi/backend_crypto/trix/"):
    	   			os.makedirs(f'{path_trix}')
			else:
					st.error("ce bot existe déja ")

		if self.name_bot == "Cocotier":
				path_cocotier= path+ "/cocotier/"
				st.write(f"cree un bot Cocotier dans {path_cocotier}")
				st.write("nous comme dans le cocotier ")
				if not os.path.exists(f"/home/helmi/backend_crypto/cocotier/{user.get_name}"):
    	   				os.makedirs(f'{path_cocotier}')
				else:
						st.error("ce bot existe déja ")

		return print("bot created ")
		
        		
class Users :
	def __init__(self, name, email):
		self.name = name
		self.email = email

	def get_name(self):
		return self.name
	
	def get_email(self):
		return self.email 
