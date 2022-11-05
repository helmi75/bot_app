import mysql.connector
from pass_secret import mot_de_passe

pwd = mot_de_passe

# alter table get_balence add crypto_wallet_pourcentage double ;
# alter table get_balence modify crypto_wallet double ;

con = mysql.connector.connect(host='localhost', user='root', password=pwd, port='3306',
                              database='cryptos', auth_plugin='mysql_native_password')

cursor = con.cursor()
query = "select  bots.bot_id from bots where bot_id IN (select get_balence.id_bot from get_balence);"
cursor.execute(query)
result = cursor.fetchall()
query2 = "select id_get_balence from get_balence;"
cursor.execute(query2)
result2 = cursor.fetchall()
con.close()
list_bot = [i[0] for i in result]
list_bot2 = [i[0] for i in result2]

for i in list_bot:
    con = mysql.connector.connect(host='localhost', user='root', password=pwd, port='3306',
                                  database='cryptos', auth_plugin='mysql_native_password')
    cursor = con.cursor()
    query = f"SELECT max(crypto_wallet)  FROM get_balence where id_bot={i} ;"
    cursor.execute(query)
    max = cursor.fetchall()[0][0]
    con.close()
    for j in list_bot2:
        con = mysql.connector.connect(host='localhost', user='root', password=pwd, port='3306',
                                      database='cryptos', auth_plugin='mysql_native_password')
        cursor = con.cursor()
        query = f"update get_balence set crypto_wallet_pourcentage = crypto_wallet/{max} where id_bot = {i} and id_get_balence = {j};"
        cursor.execute(query)
        con.commit()
        con.close()
