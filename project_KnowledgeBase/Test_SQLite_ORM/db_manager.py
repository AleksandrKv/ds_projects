import datetime
from models import *

with db:
    
    # Создать таблицы в базе данных
    # db.create_tables([Expense, Payment])

    # Добавить одну запись    
    # rec1 = Expense(name='Бензин').save()
    # rec2 = Expense(name='Продукты').save()
    # rec3 = Expense(name='Проекты').save()

    # Добавить список записей
    expenses = Expense.select()
    payments = [
        {'date': datetime.date(2022, 4, 11), 'amount': 130, 'name': 'pay1', 'expense_id': expenses[0].id},
        {'date': datetime.date(2022, 4, 12), 'amount': 200, 'name': 'pay2', 'expense_id': expenses[0].id},
        {'date': datetime.date(2022, 4, 14), 'amount': 500, 'name': 'pay3', 'expense_id': expenses[1].id},
    ]
    Payment.insert_many(payments).execute()

print('DONE')