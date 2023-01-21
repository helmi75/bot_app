import shutil


class CreateBot:
    def __init__(self, user, name_bot, type_bot, cnx):
        self.name_bot = name_bot
        self.cnx = cnx
        self.type_bot = type_bot
        self.user = user

    def get_name_bot(self):
        return self.name_bot

    def import_template(self, file_source, file_destination):
        """
        copyt the template trix  robot from the template file to the detination file
        """
        source = bytes(file_source, 'utf-8')
        destination = bytes(file_destination, 'utf-8')
        shutil.copyfile(source, destination)

    def create__bot(self, selection_bot, bot_name, user_mail,
                    api_key, secret_key, sub_account, pair_symbol, trix_lenght, trix_signal, stoch_top, stoch_bottom,
                    stoch_rsi, delta_hour, n_i):
        # create trix bot
        if selection_bot == "Trix FTX" or selection_bot == "Trix Binance" or selection_bot == "Trix Bybit":
            pair_symbol = pair_symbol[:-5].lower()

            self.cnx.insert_new_trix_bot(selection_bot, bot_name, user_mail,
                                         api_key, secret_key, sub_account, pair_symbol,
                                         trix_lenght, trix_signal, stoch_top, stoch_bottom, stoch_rsi)

        # create cocotier trix
        elif selection_bot == "Cocotier Binance"or selection_bot == "Cocotier ByBit" :
            pair_symbol = pair_symbol.lower()
            n_i = n_i.lower()
            delta_hour = (int)(delta_hour[:-1])
            self.cnx.insert_new_cocotier_bot(selection_bot,bot_name, api_key, secret_key, sub_account,
                                             pair_symbol, delta_hour, n_i)

        return True


class Users:
    def __init__(self, name, email):
        self.name = name
        self.email = email

    def get_name(self):
        return self.name

    def get_email(self):
        return self.email
