import mysql.connector
from datetime import  datetime
from pass_secret import mot_de_passe

cnx = mysql.connector.connect(host='localhost', user='root', password=mot_de_passe, port='3306', database='cryptos',
                              auth_plugin='mysql_native_password')
cursor = cnx.cursor()
query = "select bot_id,nom_bot from bots where createdDate IS NULL;"
cursor.execute(query)
myresult = cursor.fetchall()
for i in myresult :
    query = f"select dates from get_balence where id_bot = {i[0]} order by dates limit 1"
    cursor.execute(query)
    lastRow = cursor.fetchone()
    try:
        print(i[0],i[1],lastRow[0])
        query = f"update bots set bots.createdDate = '{lastRow[0]}' where bot_id = {i[0]} ;"
        cursor.execute(query)
    except TypeError:
        print(i[0], i[1], datetime.now())
        query = f"update bots set bots.createdDate = '{datetime.now()}' where bot_id = {i[0]} ;"
        cursor.execute(query)

cnx.commit()
cursor.close()