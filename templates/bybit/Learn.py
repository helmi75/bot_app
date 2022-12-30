# #pip install Bybit
# #pip install pybit
# #
import bybit
# # import time
# #
# # #il y a 39 usdt check si tu peux te connecter sur wallet apres on va faire achat/vente sur ada / eth / dot / doge / bnb
# # nom_key = "BYBIT_TRIX_ETH"
# api_key = "OLOEOSOVCKYJHWSCAJ"
# secret_key = "UWAFBGTCZPTZVAQPPUJENNCRCRRMMVXIIVBU"
# #
# client = bybit.bybit(test= False ,api_key = api_key, api_secret= secret_key)
# print("Logged in")
#
# info = client.Market.Market_symbolInfo().result()
#
# # print(info)
#
# # keys = info[0]['result']
# #btc = keys[0]['last_price']
# # for i in keys :
# #     print(i)
# #
# balence = client.Wallet.Wallet_getBalance(coin = "USDT").result()
# result = balence[0]['result']['USDT']['available_balance']
# print(result)
#
# # print(client.Order.Order_new(side="Sell",symbol="BTCUSD",order_type="Limit",qty=1,price=btc,time_in_force="GoodTillCancel").result())
# # print(client.Order.Order_new(side="Buy",symbol="BTCUSD",order_type="Limit",qty=1,price=btc,time_in_force="GoodTillCancel").result())
#
# #
# # pos = client.Position.Position_myPosition(symbol = "USDUSD").result()
# # print(pos)
#

#
# from pybit import inverse_perpetual
# session_auth = inverse_perpetual.HTTP(
#     endpoint="https://api-testnet.bybit.com",
#     api_key=api_key,
#     api_secret=secret_key
# )
# print(session_auth.get_wallet_balance(coin="BTC"))
#
# from pybit import inverse_perpetual
# session_unauth = inverse_perpetual.HTTP(
#     endpoint="https://api-testnet.bybit.com"
# )
# print(session_unauth.orderbook(symbol="ETHUSD"))
#
# from pybit import inverse_perpetual
# session_unauth = inverse_perpetual.HTTP(
#     endpoint="https://api-testnet.bybit.com"
# )
# h = session_unauth.query_symbol()['result']
# for i in h :
#     print(i)
# # print(session_unauth.query_symbol()['result'])

# from pybit import inverse_perpetual
# session_auth = inverse_perpetual.HTTP(
#     api_key=api_key,
#     api_secret=secret_key
# )
# # print(session_auth.get_wallet_balance(coin="USDT"))
# print(session_auth.wallet_fund_records())
# print(session_auth.withdraw_records())
# print(session_auth.asset_exchange_records())


import ccxt
import pandas as pd
import time as tm
# api_key = "OLOEOSOVCKYJHWSCAJ"
# secret_key = "UWAFBGTCZPTZVAQPPUJENNCRCRRMMVXIIVBU"
# api_key = "CVSGLIBWKVAHBWVYEP"
# secret_key = "WKSULRIEOXRFPMGGGDWFATRUIDNEXAUCSVMT"
# api_key = "CVSGLIBWKVAHBWVYEP"
# secret_key = "WKSULRIEOXRFPMGGGDWFATRUIDNEXAUCSVMT"
api_key = "OQDVZCKKPLWDWGREDK"
secret_key = "BNYZCPVOTAXGBYHUBMGJRCCJRBQDZCOVUNZB"
# api_key = "SF6FP7mTB7k5CsleoZ"
# secret_key = "5SZq5TCg0XEQxyiG2e02ubSBkl6RRJHHOKoH"
exchange = ccxt.bybit({
            'apiKey': api_key,
            'secret': secret_key,
            'enableRateLimit': True,
        })


balence = exchange.fetch_balance()['total']
print(balence)
# client = bybit.bybit(test= False ,api_key = api_key, api_secret= secret_key)
# print("Logged in")

# balence = client.Wallet.Wallet_getBalance(coin = "BTC").result()
# result = balence[0]['result']['BTC']['available_balance']
# print(result)
# def get_wallet(exchange):
#     balence = exchange.fetch_balance()['total']
#     df_balence = pd.DataFrame([balence]).transpose().rename(columns={0: "balence"})
#     df_balence = df_balence[df_balence['balence'] > 0]
#     crypto_index = [elm + "/USDT" for elm in df_balence['balence'].index]
#     crypto_index.remove('USDT/USDT')
#     # crypto_index.remove('LUNC/USDT')
#     # crypto_index.remove('ETHW/USDT')
#     dict_balence_usdt = {}
#     for elm in crypto_index:
#         try:
#             dict_balence_usdt[elm] = exchange.fetchTickers([elm])[elm]['ask'] * exchange.fetch_balance()['total'][
#                 elm[:-5]]
#             tm.sleep(1)
#         except Exception as e:
#             print(e)
#     return sum(dict_balence_usdt.values())
#
#
# wallet = get_wallet(exchange)
