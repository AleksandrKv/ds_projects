from modules.models import *

def get_payments():    
    with db:
        res = PamentBankCard.select()
    return res

def create_new_base():
    import sqlite3 

    # Создать базу данных
    connetion = sqlite3.connect(db_name)    
    connetion.close()

    # создать таблицы 
    BankCard.create_table()
    PamentBankCard.create_table()
    FNS_Receipt.create_table()
    FNS_Receipt_Product.create_table()
    PaymentAccount.create_table()
    