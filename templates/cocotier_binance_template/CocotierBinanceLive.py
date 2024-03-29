import sys
import traceback


sys.path.insert(0,"/home/anisse9/bot_app")
import emailing

from fonctions import *
from utilities.bdd_communication import *
import mysql.connector
from binance.client import Client
# import ta

now = datetime.now()
current_time = now.strftime("%d/%m/%Y %H:%M:%S")
print("")
print("--- Start Execution Time :", current_time, "---")
print("")
pwd = mot_de_passe
cnx = mysql.connector.connect(host='localhost', user='root', password=pwd, port='3306', database='cryptos',
                              auth_plugin='mysql_native_password')
cursor = cnx.cursor()
query = "select p.*, b.nom_bot,b.working from Params_bot_Cocotier as p, bots as b where p.bot_id = b.bot_id and b.type_bot = 'Cocotier Binance';"
cursor.execute(query)
myresult = cursor.fetchall()
df_myresult = pd.DataFrame(myresult, columns =["id_params_bot_cocotier","api_key","secret_key","sub_account",
                                               "pair_symbol","delta_hour","type_computing","bot_id","nom_bot_bot",
                                               "nom_bot_bots"])

for i in myresult:
    if i[9] :
        con = ConnectBbd('localhost', '3306', 'root', pwd, 'cryptos', 'mysql_native_password')
        idd = i[7]
        apiKey = i[1]
        secret = i[2]
        apiKey, secret = degenerateApiSecret(apiKey, secret, idd)
        market = i[4].split(',')
        for j in range(len(market)):
            market[j] = market[j].upper() + "/USDT"
        d_hour = i[5]
        delta_hour = str(i[5])+'h'
        type_computing = i[6]
        name_bot = i[8]

        # verify the time for the crontab
        try :
            query = f"select dates from get_balence where id_bot ={i[7]} order by dates desc limit 1;"
            cursor.execute(query)
            lastDate = datetime.strptime(str(cursor.fetchall()[0][0]),'%Y-%m-%d %H:%M:%S')
        except :
            lastDate = datetime.now() - timedelta(hours=(d_hour-1))
        currentDate = datetime.now()
        show_time = datetime.now()
        if(currentDate >= lastDate and (int(show_time.hour)-1) % d_hour == 0 ):
            start_time = datetime.now() - timedelta(2)
            crypto = {}
            exchange = ccxt.binance({
                'apiKey': apiKey,
                'secret': secret,
                'enableRateLimit': True
            })

            print(" ")
            print("///////////////")
            print(f"Cocotier Bot : {name_bot}")
            print(" ")

            #Get the values
            stt = datetime.strftime(start_time, '%Y-%m-%d %H:%M:%S')
            show_time = datetime.strftime(show_time, '%Y-%m-%d %H:%M:%S')
            for elm in market:
                x = elm[:-5].lower()
                klinesT = Client().get_historical_klines(elm.replace("/", ""), delta_hour, stt)
                df = pd.DataFrame(klinesT,
                                  columns=['timestamp', x + '_open', 'high', 'low', x + '_close', 'volume', 'close_time',
                                           'quote_av', 'trades', 'tb_base_av', 'tb_quote_av', 'ignore'])
                df = df[['timestamp', x + '_open', x + '_close']]
                df[x + '_close'] = pd.to_numeric(df[x + '_close'])
                df[x + '_open'] = pd.to_numeric(df[x + '_open'])
                df = df.set_index('timestamp')
                df.index = pd.to_datetime(df.index, unit='ms')
                crypto[elm.lower()] = df

            # Get the best bot
            print("============= the dataframe=============")
            # print((crypto))
            print(affichageDataFrameLog(crypto).tail(4).head(3).to_string())
            print("============= the dataframe=============")
            crypto = variationN(crypto, type_computing)
            crypto = coeffMulti(crypto)
            crypto = mergeCryptoTogether(crypto)
            del crypto['BOT_MAX']
            nom_crypto_achat = getBotMax(crypto, market, type_computing)
            #Sell Then Buy maybe here we need to do an exception management
            try :
                # nom_crypto_vente = crypto_a_vendre(exchange, market)
                nom_crypto_vente = findCurrentCrypto(exchange)
                algo_achat_vente(exchange, nom_crypto_vente, nom_crypto_achat)

                print(" ")
                print(f"Plage Horraire = {delta_hour}")
                print(" ")
                print(f"computing = {type_computing}")
                print(" ")
                print(f"{show_time} , la meilleur crypto est {nom_crypto_achat}, je vends {nom_crypto_vente} et j'achete {nom_crypto_achat}")

                # Save the wallet value
                wallet = get_wallet(exchange)
                print(f"The new crypto wallet is {wallet}")
                con.insert_balence(datetime.now(),nom_crypto_achat , wallet, i[7],"ONN","none","No Problem")
            except ZeroDivisionError :
                pass
            except Exception as exceptions :
                print("*****Exceptions*****")
                con.insert_balence(datetime.now(),"none" , 0, i[7],"OFF","none",str(exceptions))
                emailing.send_mail("helmichiha@gmail.com",name_bot,"Cocotier Binance",exceptions,traceback.format_exc())
                emailing.send_mail("aitmoummad.anisse@gmail.com",name_bot,"Cocotier Binance",exceptions,traceback.format_exc())
                emailing.send_mail("aitmoummad.yassine@gmail.com",name_bot,"Cocotier Binance",exceptions,traceback.format_exc())
                traceback.print_exc()
                print("********************")



print("")
print("--- End Execution Time ---")
print("")
