from bdd_communication import *
from pass_secret import mot_de_passe

con = ConnectBbd('localhost', '3306', 'root', mot_de_passe, 'cryptos', 'mysql_native_password')

trixs = con.get_trix_details_bot()
cocotier = con.get_cocotier_details_bot()

for i in trixs:
    id = i[10]
    api = i[1]
    secret = i[2]
    api, secret = generateApiSecret(api, secret, id)
    print(id,api,secret)
    # api, secret = degenerateApiSecret(api, secret, id)
    con.update_trix_details_bot(id,api,secret)


for i in cocotier:
    id = i[7]
    api = i[1]
    secret = i[2]
    # api, secret = generateApiSecret(api, secret, id)
    api, secret = degenerateApiSecret(api, secret, id)
    print(id,api,secret)
    # con.update_cocotier_details_bot(id,api,secret)