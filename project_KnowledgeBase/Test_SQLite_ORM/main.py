from telnetlib import TTYLOC
import tkinter as tk
from tkinter import ttk
import data_manager as dm

window = tk.Tk()
window.title('Tests tkinter')
# window.size = (400, 350)

frame1 = tk.Frame(window, bg='blue')
frame2 = tk.Frame(window, bg='red')
frame3 = tk.Frame(window, bg='green')

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

window.mainloop()
