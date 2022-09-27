
import mysql.connector

class ConnectBbd:
    def __init__(self, host, port, user, password, database, auth_plugin=None):
        self.host = host
        self.port = port
        self.user = user
        self.password = password
        self.database = database
        self.auth_plugin =auth_plugin
        self.cnx = mysql.connector.connect(host=self.host,
                                    user=self.user,
                                    password=self.password,
                                    port=self.port,
                                    database=self.database,
                                    auth_plugin=self.auth_plugin)

    def insert_new_user(self, user_name, email, password):
        cursor = self.cnx.cursor()
        query = """INSERT INTO users (user_name, email, password) VALUES ('%s', '%s', '%s')""" % (user_name, email, password)	
        cursor.execute(query)
        self.cnx.commit()
        cursor.close()
        self.cnx.close()

    def delete_user(self, user_name):
        cursor = self.cnx.cursor()
        query = """ DELETE FROM users WHERE user_name = ('%s')""" % (user_name)
        cursor.execute(query)
        self.cnx.commit()
        cursor.close()
        self.cnx.close()
    
    def insert_new_trix_bot(self, user_name=None, name_bot=None,
                            api_key=None, secret_key=None, sub_account=None, pair_symbol=None,
                            trix_lenght=None,trix_signal=None,stoch_top=None, stoch_bottom=None ,stoch_rsi=None ):

       cursor = self.cnx.cursor()
       query = """ INSERT INTO bots ( nom_bot) VALUES ('%s') """% (name_bot)
       cursor.execute(query)
       self.cnx.commit()
       #cursor.close()
       
       query = """ INSERT INTO params_bot_trix (name_bot, api_key, secret_key, sub_account, pair_symbol, trix_length, trix_signal, stoch_top, stoch_bottom, stoch_RSI )
                   VALUES ('%s', '%s', '%s','%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s') """% (name_bot, api_key, secret_key, sub_account, pair_symbol,trix_lenght, trix_signal,  stoch_top, stoch_bottom, stoch_rsi)
       cursor.execute(query)
       self.cnx.commit()
       cursor.close()

       self.cnx.close()

    def get_info(self):
        cursor = self.cnx.cursor()
        query = " SELECT password  FROM users ;"
        cursor.execute(query)
        result = cursor.fetchall()
        self.cnx.close()
        return result
