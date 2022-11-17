import mysql.connector

con = mysql.connector.connect(host='localhost',user='root',password='Magali_1984',port='3306',
                                           database='cryptos',  auth_plugin='mysql_native_password')
cursor = con.cursor()
query = "select bot_id from bots where type_bot = 'cocotier' and bot_id not in (select bot_id from Params_bot_Cocotier);"
cursor.execute(query)
result = cursor.fetchall()

for i in result :
    query = f"insert into Params_bot_Cocotier (api_key,secret_key,sub_account,pair_symbol,delta_hour,type_computing,bot_id) values ('','','','','2','n','{i[0]}');"
    cursor.execute(query)
    con.commit()
con.close()