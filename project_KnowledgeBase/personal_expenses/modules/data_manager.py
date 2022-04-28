from models import *

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
    PaymentAccount.create_table()
    BankCard.create_table()
    PamentBankCard.create_table()

    



