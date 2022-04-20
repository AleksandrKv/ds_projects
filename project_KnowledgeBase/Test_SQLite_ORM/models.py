from peewee import *

db = SqliteDatabase('D:/YandexDisk/it_Projects/py_databases/database.db')

# Базовый класс (общие для всех поля)
class BaseModel(Model):
    id = PrimaryKeyField(unique=True)

    class Meta:
        database = db
        order_by = 'id'

# Расход
class Expense(BaseModel):
    name = CharField()

    class Meta:
        db_table = 'expenses'

# Оплата
class Payment(BaseModel):
    date = DateField()
    amount = FloatField()
    name = CharField()
    expense_id = ForeignKeyField(Expense)

    class Meta:
        db_table = 'payments'

# p = Payment()
# print(type(p))