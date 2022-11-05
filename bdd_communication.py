import mysql.connector
import sys
from datetime import datetime


class ConnectBbd:
    def __init__(self, host, port, user, password, database, auth_plugin):
        self.host = host
        self.port = port
        self.user = user
        self.password = password
        self.database = database
        self.auth_plugin = auth_plugin
        self.cnx = mysql.connector.connect(host=self.host,
                                           user=self.user,
                                           password=self.password,
                                           port=self.port,
                                           database=self.database,
                                           auth_plugin=self.auth_plugin)

    def insert_new_user(self, user_name, email, password):
        cursor = self.cnx.cursor()
        query = """INSERT INTO users (username, email, password) VALUES ('%s', '%s', '%s')""" % (
            user_name, email, password)
        cursor.execute(query)
        self.cnx.commit()
        cursor.close()
        #self.cnx.close()

    def delete_user(self, user_name):
        cursor = self.cnx.cursor()
        query = """ DELETE FROM users WHERE username = ('%s')""" % (user_name)
        cursor.execute(query)
        self.cnx.commit()
        cursor.close()
        #self.cnx.close()

    def delete_bot(self, bot_id):
        cursor = self.cnx.cursor()
        query = """ DELETE FROM bots WHERE bot_id = ('%s')""" % (bot_id)
        cursor.execute(query)
        self.cnx.commit()
        cursor.close()
        #self.cnx.close()

    def insert_new_trix_bot(self, selection_bot, bot_name, user_mail,
                            api_key, secret_key, sub_account, pair_symbol,
                            trix_lenght, trix_signal, stoch_top, stoch_bottom, stoch_rsi):
        cursor = self.cnx.cursor()
        query = """Insert into bots (nom_bot) values ('%s')""" % (bot_name)
        cursor.execute(query)
        idd = cursor.lastrowid
        self.cnx.commit()

        query = """ INSERT INTO params_bot_trix (api_key, secret_key, sub_account, 
        pair_symbol, trix_length, trix_signal, stoch_top, stoch_bottom, stoch_RSI ,bot_id)
                           VALUES ('%s', '%s', '%s','%s', '%s', '%s', '%s', '%s', '%s', '%s') """ % (
            api_key, secret_key, sub_account, pair_symbol, trix_lenght, trix_signal, stoch_top, stoch_bottom,
            stoch_rsi, idd)
        cursor.execute(query)
        self.cnx.commit()
        cursor.close()
        #self.cnx.close()

    def update_trix_bot(self, bot_id, api_key, secret_key, sub_account, pair_symbol,
                        trix_lenght, trix_signal, stoch_top, stoch_bottom, stoch_rsi):
        cursor = self.cnx.cursor()
        query = f'''update params_bot_trix set
                           api_key = '{api_key}',
                           secret_key = '{secret_key}',
                           sub_account = '{sub_account}',
                           pair_symbol = '{pair_symbol}',
                           trix_length = '{trix_lenght}',
                           trix_signal = '{trix_signal}',
                           stoch_top = '{stoch_top}',
                           stoch_bottom = '{stoch_bottom}',
                           stoch_RSI = '{stoch_rsi}' where bot_id = {bot_id} ;'''
        cursor.execute(query)
        self.cnx.commit()
        cursor.close()
        self.cnx.close()

    def insert_trix_balence(self, date, crypto_name, crypto_wallet, id_bot):
        cursor = self.cnx.cursor()
        query = """Insert into get_balence (dates, crypto_name,crypto_wallet,id_bot) values ('%s','%s','%s','%s')""" % (
            date, crypto_name, crypto_wallet, id_bot)
        cursor.execute(query)
        self.cnx.commit()
        idd = cursor.lastrowid
        cursor.close()
        self.insert_trix_balence_pourcentage(idd)
        self.insert_trix_balence_crypto_pourcentage(idd)

    def insert_trix_balence_pourcentage(self,idd):
        cursor = self.cnx.cursor()
        #recupére the last get_balence id
        print("idd : ",idd)
        #get the id_bot
        query = f"SELECT id_bot  FROM get_balence where id_get_balence={idd} ;"
        cursor.execute(query)
        bot_id = cursor.fetchall()[0][0]
        print("bot_id : ",bot_id)
        #get the max crypto_wallet
        query = f"SELECT max(crypto_wallet)  FROM get_balence where id_bot={bot_id} ;"
        cursor.execute(query)
        max = cursor.fetchall()[0][0]
        print("max : ",max);
        #add the crypto wallet pourcentage to the get_ballence
        query = f'''update get_balence set crypto_wallet_pourcentage = crypto_wallet/{max}
         where  id_get_balence = {idd};'''
        cursor.execute(query)
        self.cnx.commit()
        cursor.close()
        #self.cnx.close()

    def insert_trix_balence_crypto_pourcentage(self,idd):
        cursor = self.cnx.cursor()
        query = f"SELECT id_bot  FROM get_balence where id_get_balence={idd} ;"
        cursor.execute(query)
        bot_id = cursor.fetchall()[0][0]
        query = f"SELECT crypto_wallet  FROM get_balence where id_bot= {bot_id} order by dates limit 1;"
        cursor.execute(query)
        max = cursor.fetchall()[0][0]
        query = f'''update get_balence set crypto_pourcentage = crypto_wallet/{max}
         where  id_get_balence = {idd};'''
        cursor.execute(query)
        self.cnx.commit()
        cursor.close()
        # self.cnx.close()

    def insert_log_info(self, date, pair_symbol, status_bot, transaction, bot_id):
        cursor = self.cnx.cursor()
        query = """Insert into log_execution (date, pair_symbol, status_bot, transaction, bot_id) values ('%s','%s','%s','%s','%s')""" % ( 
                 date, pair_symbol, status_bot, transaction, bot_id)
        cursor.execute(query)
        self.cnx.commit()
        cursor.close()


    def get_info(self):
        cursor = self.cnx.cursor()
        query = " SELECT password  FROM users ;"
        cursor.execute(query)
        result = cursor.fetchall()
        #self.cnx.close()
        return result

    def get_bots(self):
        cursor = self.cnx.cursor()
        query = " SELECT bot_id, nom_bot  FROM bots ;"
        cursor.execute(query)
        result = cursor.fetchall()
        #self.cnx.close()
        return result

    def get_trix_bot(self, bot_id):
        cursor = self.cnx.cursor()
        query = f"select params_bot_trix.*, bots.nom_bot from params_bot_trix , bots where bots.bot_id = params_bot_trix.bot_id and params_bot_trix.bot_id = {bot_id};"
        cursor.execute(query)
        result = cursor.fetchall()
        # self.cnx.close()
        return result

    def get_type_bot(self, bot_id):
        cursor = self.cnx.cursor()
        query = f"select type_bot from bots where bot_id={bot_id};"
        cursor.execute(query)
        result = cursor.fetchall()
        # self.cnx.close()
        return result

    def get_balences(self):
        cursor = self.cnx.cursor()
        query = "select dates, crypto_wallet,nom_bot from get_balence, bots where (get_balence.id_bot = bots.bot_id);"
        cursor.execute(query)
        myresult = cursor.fetchall()
        return myresult

    def get_balences_Normalization(self):
        cursor = self.cnx.cursor()
        query = "select dates, crypto_wallet_pourcentage,nom_bot from get_balence, bots where (get_balence.id_bot = bots.bot_id);"
        cursor.execute(query)
        myresult = cursor.fetchall()
        return myresult
    def get_crypto_pourcentage(self):
        cursor = self.cnx.cursor()
        query = "select dates, crypto_pourcentage,nom_bot from get_balence, bots where (get_balence.id_bot = bots.bot_id and bots.type_bot = 'trix');"
        cursor.execute(query)
        myresult = cursor.fetchall()
        return myresult


    def get_maintenance_setting(self):
        cursor = self.cnx.cursor()
        query = "select value_setting_boolean from settings where name_setting='maintenance';"
        cursor.execute(query)
        myresult = cursor.fetchall()
        return myresult

    def update_maintenance_setting(self):
        cursor = self.cnx.cursor()
        query = "update settings set value_setting_boolean = not value_setting_boolean where name_setting = 'maintenance';"
        cursor.execute(query)
        self.cnx.commit()
        cursor.close()
        # self.cnx.close()

 
    def bot_status(self, pairSymbol, side, id_bot):
        """ 
           insert status bot data to the database 
        """
        try:
            self.insert_log_info(datetime.now(),pairSymbol,"ONN",side ,id_bot)
        except BaseException as ex:
            ex_type, ex_value, ex_traceback = sys.exc_info()
            self.insert_log_info(datetime.now(),pairSymbol,"ex_value", side,id_bot)

    def get_status(self):
       """
          get bots status information from bdd 
       """
       cursor = self.cnx.cursor()
       #query = "select * from log_execution;"
       query = " select * from log_execution left join bots on log_execution.bot_id = bots.bot_id;"
       cursor.execute(query)
       result = cursor.fetchall()
       #self.cnx.close()
       return result


