# version 1.0 28/07/2022
# version 1.1 29/09/2022
# version 1.2 03/09/2022

import traceback
import mysql.connector
import pandas as pd
import ftx
import sys
sys.path.insert(0,"/home/anisse9/bot_app")
from bdd_communication import ConnectBbd
from pass_secret import mot_de_passe
from datetime import datetime
import time
from math import *
import ta

def truncate(n, decimals=0):
    r = floor(float(n)*10**decimals)/10**decimals
    return str(r)

def getBalance(myclient, coin):
    jsonBalance = myclient.get_balances()
    if jsonBalance == []:
        return 0
    pandaBalance = pd.DataFrame(jsonBalance)
    if pandaBalance.loc[pandaBalance['coin'] == coin].empty:
        return 0
    else:
        return float(pandaBalance.loc[pandaBalance['coin'] == coin]['free'])

def buyCondition(row, stochTop_conf):
    if row['TRIX_HISTO'] > 0 and row['STOCH_RSI'] <=  stochTop_conf:
        return True
    else:
        return False
def sellCondition(row, stochBottom_conf):
    if row['TRIX_HISTO'] < 0 and row['STOCH_RSI'] >= stochBottom_conf:
        return True
    else:
        return False

# First Task
# Get All the necessary columns from the database
pwd = mot_de_passe
cnx = mysql.connector.connect(host='localhost', user='root', password=pwd, port='3306', database='cryptos',
                              auth_plugin='mysql_native_password')
cursor = cnx.cursor()
query = "select * from params_bot_trix;"
cursor.execute(query)
myresult = cursor.fetchall()

# Trix Set : id, api_key, secret_key, sub_account, pair_symbol, trix_length, trix_signal, stoch_top, stoch_bottom,
# stoch_RSI, bot_id

# Second Task
# For each line launch the api and get the crypto_wallet value

print("# ", datetime.now().strftime("%d/%m/%Y %H:%M:%S"))

for i in myresult:
    con = ConnectBbd('localhost', '3306', 'root', pwd, 'cryptos', 'mysql_native_password')
    try :
      fiatSymbol = 'USD'
      cryptoSymbol = (i[4]+"").upper()
      pairSymbol = cryptoSymbol+'/USD'
      myTruncate = 3

      client = ftx.FtxClient(
          api_key=i[1],
          api_secret=i[2],
          subaccount_name=i[3]
      )

      data = client.get_historical_data(
          market_name=pairSymbol,
          resolution=3600,
          limit=1000,
          start_time=float(round(time.time())) - 150 * 3600,
          end_time=float(round(time.time())))
      df = pd.DataFrame(data)

      trixLength = i[5]
      trixSignal = i[6]
      df['TRIX'] = ta.trend.ema_indicator(
          ta.trend.ema_indicator(ta.trend.ema_indicator(close=df['close'], window=trixLength), window=trixLength),
          window=trixLength)
      df['TRIX_PCT'] = df["TRIX"].pct_change() * 100
      df['TRIX_SIGNAL'] = ta.trend.sma_indicator(df['TRIX_PCT'], trixSignal)
      df['TRIX_HISTO'] = df['TRIX_PCT'] - df['TRIX_SIGNAL']
      df['STOCH_RSI'] = ta.momentum.stochrsi(close=df['close'], window=i[9], smooth1=3, smooth2=3)


      actualPrice = df['close'].iloc[-1]
      fiatAmount = getBalance(client, fiatSymbol)
      cryptoAmount = getBalance(client, cryptoSymbol)
      minToken = 5 / actualPrice
      side="none"
      if buyCondition(df.iloc[-2], i[7]):
          if float(fiatAmount) > 5:
              print(f"on achete : subacount_name {i[3]}")
              quantityBuy = truncate(float(fiatAmount) / actualPrice, myTruncate)
              buyOrder = client.place_order(
                  market=pairSymbol,
                  side="buy",
                  price=None,
                  size=quantityBuy,
                  type='market')
              print(side)
              con.bot_status(pairSymbol, side , i[10])

          else:
              con.bot_status(pairSymbol, side , i[10])
              goOn = True

      elif sellCondition(df.iloc[-2], i[8]):
          if float(cryptoAmount) > minToken:
              print(f"on vent :subaccount_name {i[3]}")
              sellOrder = client.place_order(
                  market=pairSymbol,
                  side="sell",
                  price=None,
                  size=truncate(cryptoAmount, myTruncate),
                  type='market')
              print(side)
              con.bot_status(pairSymbol, side, i[10])

          else:
              con.bot_status(pairSymbol, side , i[10])
              goOn = True
      else:
          goOn = True
          con.bot_status(pairSymbol, side , i[10])

      #listBalances = sorted(client.get_balances(),key= lambda d : d['total'], reverse= True)
      df_balences = pd.DataFrame(client.get_balances())
      crypto_symbol_value_balence = df_balences[df_balences['coin']==cryptoSymbol]["usdValue"].values[0] + df_balences[df_balences['coin']=="USD"]["usdValue"].values[0]
      con.insert_trix_balence(datetime.now(), f"Trix : {i[4]}_len{i[5]}_sign{i[6]}_top{i[7]}_bottom{i[8]}_RSI{i[9]}", crypto_symbol_value_balence, i[10])
      #con.insert_log_info(datetime.now(),pairSymbol, "ON", side,i[10])
      print(f"# bot {i[3]} executed")

    except BaseException as ex:
      # Get current system exception
      ex_type, ex_value, ex_traceback = sys.exc_info()

      # Extract unformatter stack traces as tuples
      trace_back = traceback.extract_tb(ex_traceback)

      # Format stacktrace
      stack_trace = list()

      for trace in trace_back:
          stack_trace.append("File : %s , Line : %d, Func.Name : %s, Message : %s" % (trace[0], trace[1], trace[2], trace[3]))
      print("\nsubaccout problem :",i[3])
      print("pair_symbol problem :", pairSymbol)
      print("Exception type : %s " % ex_type.__name__)
      print("Exception message : %s" %ex_value)
      print("Stack trace : %s \n" %stack_trace)
      con.insert_log_info(datetime.now(), pairSymbol, ex_value, "none", i[10])
print("We're done\n\n")