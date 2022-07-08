
import os

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
	
	def create_bot (self):
		pass
        		
class Users :
	def __init__(self, name, email ):
		self.name = name
		self.email = email

	def get_name(self):
		return self.name
	
	def get_email(self):
		return self.email 
