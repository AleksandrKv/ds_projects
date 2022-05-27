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
    mark = CharField(null=True)            # идентификационные признаки в текстовом формате
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
    balance = FloatField(null=True)
    category = CharField(null=True) 
    place = CharField(null=True)

    class Meta:
        db_table = 'paments_bank_cards'

# Чек в формате ФНС
class FNS_Receipt(BaseModel):
    """"
    # {'user': 'ОБЩЕСТВО С ОГРАНИЧЕННОЙ ОТВЕТСТВЕННОСТЬЮ "ПЛАНЕТА "СПОРТ"',
    #  'retailPlaceAddress': '299053, Г.Севастополь, Вакуленчука ул, 20 д.',
    #  'userInn': '9204017560  ',
    #  'requestNumber': 449,
    #  'shiftNumber': 164,
    #  'operator': 'М42_Масленникова Галина Николаевна',
    #  'operationType': 1,
    #  'totalSum': 444564,
    #  'cashTotalSum': 0,
    #  'ecashTotalSum': 444564,
    #  'kktRegId': '0004643249002589    ',
    #  'fiscalDriveNumber': '9960440301353190',
    #  'fiscalDocumentNumber': 50854,
    #  'fiscalSign': 2902151782,
    #  'nds18': 22426,
    #  'nds10': 28185,
    #  'code': 3,
    #  'fiscalDocumentFormatVer': 4,
    #  'retailPlace': 'Магазин',
    #  'prepaidSum': 0,
    #  'creditSum': 0,
    #  'provisionSum': 0,
    #  'dateTime': 1649958720,
    #  'taxationType': 1,
    #  'localDateTime': '2022-04-14T20:52'}
    # """
    dateTime        = DateTimeField()
    localDateTime   = DateTimeField()
    totalSum        = FloatField()
    user            = CharField()
    retailPlaceAddress = CharField()
    userInn         = CharField()
    requestNumber   = CharField(null=True)
    shiftNumber     = CharField(null=True)
    operator        = CharField(null=True)
    operationType   = CharField(null=True)
    cashTotalSum    = CharField(null=True)
    ecashTotalSum   = CharField(null=True)
    kktRegId        = CharField(null=True)
    fiscalDriveNumber    = CharField(null=True)
    fiscalDocumentNumber = CharField(null=True)
    fiscalSign      = CharField(null=True)
    nds18           = CharField(null=True)
    nds10           = CharField(null=True)
    code            = CharField(null=True)
    fiscalDocumentFormatVer = CharField(null=True)
    retailPlace     = CharField(null=True)
    prepaidSum      = CharField(null=True)
    creditSum       = CharField(null=True)
    provisionSum    = CharField(null=True)
    taxationType    = CharField(null=True)

    class Meta:
        db_table = 'fns_receipts'

#  Номенклатура покупок из чеков от ФНС
class FNS_Receipt_Product(BaseModel):
    """
    #  0   name         35 non-null     object 
    #  1   price        35 non-null     int64  
    #  2   sum          35 non-null     int64  
    #  3   quantity     35 non-null     float64
    #  4   paymentType  35 non-null     int64  
    #  5   productType  35 non-null     int64  
    #  6   nds          35 non-null     int64  
    #   name	                                           price	sum	  quantity	paymentType	productType	nds
    # 0	Вино Игристое Севастопольский Бриз бел п/сух З...	33900	33900	1.000	4	        2	         1
    # 1	Пиво Жатецкий Гусь ПЭТ 1,35 л 4,6%	                16500	16500	1.000	4	        2	         1
    # ...
    """
    receipt_id = ForeignKeyField(FNS_Receipt, backref='products')
    name = CharField()
    price = FloatField()
    amount = FloatField()
    quantity = FloatField()
    paymentType = CharField()
    productType = CharField()
    nds = CharField()

    class Meta:
        db_table = 'fns_receipt_products'

# p = Payment()
# print(type(p))