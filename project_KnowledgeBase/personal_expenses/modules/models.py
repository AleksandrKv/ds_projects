from enum import unique
from numpy import place
from peewee import *

db_name = 'D:/YandexDisk/it_Projects/py_databases/paymens.db'
db = SqliteDatabase(db_name)

# Базовый класс (общие для всех поля)
class BaseModel(Model):
    id = PrimaryKeyField(unique=True)

    class Meta:
        database = db
        order_by = 'id'

# Расчетный счет
class PaymentAccount(BaseModel):
    name = CharField()

    class Meta:
        db_table = 'payment_accounts'

# Банковская карта
class BankCard(BaseModel):
    number = CharField(unique=True)        # номер карты
    name = CharField()                     # (удобное) пользовательское название карты 
    identification = CharField(null=True)   # идентификационные признаки в текстовом формате
    # bank = CharField()                   # название банка
    # babk_account = CharField()           # номер банковского счета

    class Meta:
        db_table = 'bank_cards'

# Оплата банковской картой
class PamentBankCard(BaseModel):
    card_id = ForeignKeyField(BankCard, backref='payments')
    date = DateTimeField()
    date_account = DateTimeField(null=True)    
    name = CharField(null=True)
    amount = FloatField()
    category = CharField(null=True) 
    place = CharField(null=True)

    class Meta:
        db_table = 'paments_bank_cards'

# # Оплата 
# class Payment(BaseModel):
#     date = DateField()
#     amount = FloatField()
#     name = CharField()
#     # expense_id = ForeignKeyField(Expense)

#     class Meta:
#         db_table = 'payments'

# p = Payment()
# print(type(p))