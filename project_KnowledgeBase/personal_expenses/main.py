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

# def OnClick_Load_сard_payments():
#     pe.Load_сard_payments()

window = tk.Tk()
window.title('Tests tkinter')
# window.size = (400, 350)

# командная панель
frame_top = tk.Frame(window, background='#D9D8D7')
frame_top.pack(side=tk.TOP, fill=tk.X)
# Кнопки
bt1 = tk.Button(frame_top, text="Загрузить выписку", command=pe.load_сard_payments_to_sqlite)
bt1.grid(row=0, column=0, sticky='w', padx=15, pady=5)
bt2 = tk.Button(frame_top, text="Загрузить файлы json", command=pe.Load_json_files)
bt2.grid(row=0, column=1, sticky='w', padx=15, pady=5)

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

