from pkgutil import extend_path
from telnetlib import TTYLOC
import datetime as dt
import tkinter as tk
import tkinter.filedialog as fd
import tkinter.messagebox as mb
from tkinter import ttk
from turtle import color
import pandas as pd
import modules.data_manager as dm
import modules.pe_methods as pe

# import os

# from modules.models import *

def OnClick_Load_сard_payments():
    pe.Load_сard_payments()

    # # Выбрать файл
    # filetypes = (   ("Форматы выписок (*.xml, *.csv)", ["*.xml", "*.csv"] ),
    # # filetypes = (("CSV", "*.csv"),
    #                 ("Сбербанк PDF", "*.pdf"),
    #                 ("Любой", "*"))                
    # filename = fd.askopenfilename(title="Открыть файл", #initialdir=os.getcwd(), #"/",
    #                                 filetypes=filetypes)
    # if filename:
    #     print(filename)    

    # ext =  os.path.splitext(filename)[1].lower()

    # # Загрузить файл в DataFrame
    # if ext == '.csv':
    #     df = pd.read_csv(filename, sep=';', encoding='cp1251')

    # # Создать столбец "date" (перобразовать тип поля текст в дату)
    # df["date"] = pd.to_datetime(df["Дата операции"], dayfirst=True)
    
    # # Расчет приходов и расходов по карте за период
    # mask_receipt = df["Сумма операции в валюте карты"] > 0
    # mask_expense = df["Сумма операции в валюте карты"] < 0
    # df['receipt'] = df[mask_receipt]["Сумма операции в валюте карты"]
    # df['expense'] = -df[mask_expense]["Сумма операции в валюте карты"]
    # # df.receipt.sum(), df.expense.sum()

    # # Получить объект банковской карты
    # sel = BankCard.select().where(BankCard.number == '2200020233972043')
    # if len(sel) != 1:
    #     print("В базе данных не найдена банковская карта с запрашиваемым именем")
    #     return
    # bank_card = sel.get()

    # # Проверить наличие записей по этой карте за период (для удаления)
    # d1 = df.date.min().date()
    # d2 = (df.date.max()+pd.offsets.Day(1)).date()
    # sel = PamentBankCard.select().where(
    #     (PamentBankCard.card_id == bank_card) 
    #     & (PamentBankCard.date >= d1) 
    #     & (PamentBankCard.date < d2)
    #     )
    # delete_count = len(sel)

    # # Начало транзакции удаления/записи
    # with db.atomic() as transaction:  # transaction.rollback()
    
    #     # Удалить записи по загружаемому периоду
    #     if delete_count > 0:
    #         try:
    #             for rec in sel:
    #                 rec.delete_instance()
    #             print(f'Количество удаленных записей: {delete_count}')
    #         except:
    #             print('При попцтке удления возникла ошибка')
    #             transaction.rollback()

    #     # Записать операции по карте в базу данных
    #     try:
    #         bank_card = get_bank_card('2200020233972043')

    #         payments = [PamentBankCard(
    #                 card_id      = bank_card, 
    #                 date         = get_dt_from_pandas(rec.date),
    #                 date_account = dt.datetime.now(), #['Дата обработки'],
    #                 name         = rec['Название операции'],
    #                 amount       = rec['Сумма операции в валюте карты'],
    #                 category     = rec['Категория'],
    #                 place        = rec['Место операции'],
    #             ) for i,rec in df.iterrows()
    #         ]
    #         PamentBankCard.bulk_create(payments, batch_size=999)
    #     except:
    #         print('При попытке сохранить в базу данных загруженные данные возникла ошибка')
    #         transaction.rollback()

    # # print(filename)    
    # # print(df.head())    
    
    


window = tk.Tk()
window.title('Tests tkinter')
# window.size = (400, 350)

# командная панель
frame_top = tk.Frame(window, background='#D9D8D7')
frame_top.pack(side=tk.TOP, fill=tk.X)
bt1 = tk.Button(frame_top, text="Загрузить выписку", command=OnClick_Load_сard_payments)
bt1.grid(row=0, column=0, sticky='w', padx=15, pady=5)

# body
frame_body = tk.Frame(window)
frame_body.pack(side=tk.BOTTOM, fill=tk.Y)

frame1 = tk.Frame(frame_body, bg='blue')
frame2 = tk.Frame(frame_body, bg='red')
frame3 = tk.Frame(frame_body, bg='green')

frame1.grid(row=0, column=0, sticky='ns')
frame2.grid(row=0, column=1)
frame3.grid(row=1, column=0, sticky='we', columnspan=2)

lab1 = tk.Label(frame1, text='lab1')
lab2 = tk.Label(frame2, text='lab2')
lab3 = tk.Label(frame3, text='lab3')

lab1.grid(row=0, column=0, sticky='w', padx=10, pady=10)
lab2.grid(row=0, column=0, sticky='w', padx=20, pady=20)
# lab3.grid(row=0, column=0, sticky='w', padx=10, pady=10)

# Заголовки таблицы
heads = ['id', 'date', 'amount', 'name']
table = ttk.Treeview(frame3, show='headings') 
table['columns'] = heads
# table['displaycolumns'] = ['amount', 'id', 'date', 'name']

for header in heads:
    table.heading(header, text=header, anchor='center')
    table.column(header, anchor='center')

data = dm.get_payments()
for row in data:
    row2=[row.id, row.date, row.amount, row.name]
    table.insert('', tk.END, values=row2)

# scrollbar
scrollbar = ttk.Scrollbar(frame3, command=table.yview)
table.configure(yscrollcommand=scrollbar.set)

# размещение на форме
scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
table.pack(expand=tk.YES, fill=tk.BOTH)

# mess = 'инфо \n' + 'dsasaaa'
# res = mb.askyesno(title="Загрузка банковской выписки по карте", message=mess )
# print(type(res))
# print(res)

window.mainloop()

