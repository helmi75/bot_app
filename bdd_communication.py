
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
"""
    def insert(self, data):
      cursor =self.cnx.cursor()
      #query = "INSERT INTO  get_balence (dates, time, user_name, bot_name, actual_crypto_balence, crypto_name, crypto_wallet) VALUES  (%s, %s , %s, %s, %s, >
      cursor.execute(query, data)
      self.cnx.commit()
      cursor.close()
      self.cnx.close()
      return print("value added to database ",data)"""

#con = ConnectBbd( '91.167.181.110', '3306', 'anisse9', 'Magali_1984', 'mysql_native_password')
mysql.connector.connect(host='91.167.181.110', user="root", password='Magali_1984', port="3306", database="cryptos", auth_plugin="mysql_native_password")
#con.insert((datetime.now(), datetime.now(), user_name, bot_name, ticker_ask*balence_total, name_max_var_computing, get_wallet(exchange)))