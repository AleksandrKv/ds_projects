from sre_constants import SUCCESS
from tkinter.tix import Tree
import xml.etree.ElementTree as ET
import numpy as np
import pandas as pd
import datetime as dt
import tkinter as tk
import tkinter.filedialog as fd
import tkinter.messagebox as mb
import modules.my_methods as mm
import modules.win_messages as win
from  modules.models import *
import os, datetime

def Load_сard_payments():

    load_payments_methods = [
        (load_payments_from_XML_sber, '.xml'),
        (load_payments_from_XML_RNKB, '.xml'),
        (load_payments_from_CSV_RNKB, '.csv'),
    ]
    # Выбрать файл
    filetypes = (   ("Форматы выписок (*.xml, *.csv)", ["*.xml", "*.csv"] ),
                    ("XML", "*.xml"),
                    ("CSV", "*.csv"),
                    ("PDF", "*.pdf"),
                    ("Любой", "*"))                
    file_name = fd.askopenfilename(title="Открыть файл", #initialdir=os.getcwd(), #"/",
                                    filetypes=filetypes)
    # if filename:
    #     print(filename)    

    ext =  os.path.splitext(file_name)[1].lower()

    for items in load_payments_methods:

        # Перебрать известные функции чтения
        if ext == items[1]:
            func = items[0]
            res = func(file_name=file_name)

            # # Проверка на наличие ошибок
            # if res['error_text'] != '':
            #     mb.showinfo(title, res['error_text'])
            #     return

            # Обработать успешную загрузку
            if res['success']:
                df,d1,d2 = res['df'], res['d1'], res['d2']
                bank_card = get_bank_card(card_mark=res['card_mark'])

                # Вопрос да/нет пользователю
                title="Загрузка банковской выписки по карте"
                flag_yesno = mb.askyesno(title=title, message=res['mess'])
                if not flag_yesno:
                    return None

                # Проверить наличие записей по этой карте за период (для удаления)
                sel = PamentBankCard.select().where(
                    (PamentBankCard.card_id == bank_card) 
                    & (PamentBankCard.date >= d1) 
                    & (PamentBankCard.date < d2)
                    )
                delete_count = len(sel)

                # Запись в БД. Транзакции удаления/записи    
                with db.atomic() as transaction:  # transaction.rollback()    
                    # Удалить записи по загружаемому периоду
                    if delete_count > 0:
                        try:
                            for rec in sel:
                                rec.delete_instance()
                            print(f'Количество удаленных записей: {delete_count}')
                        except:
                            print('При попытке удления возникла ошибка')
                            transaction.rollback()
                    # Записать операции по карте в базу данных
                    try:
                        # columns=["date", "date_account", "category", "name", "amount", "balance"]
                        payments = []
                        for i,rec in df.iterrows():
                            payments.append(
                                PamentBankCard(
                                    card_id      = bank_card, 
                                    date         = mm.get_dt_from_pandas(rec.date),
                                    date_account = dt.datetime.now(), #['Дата обработки'],
                                    name         = rec['name'],
                                    amount       = rec['amount'],
                                    balance      = rec['balance'],
                                    category     = rec['category'],
                                    place        = None, #rec['place'] if rec. else None,
                                )   
                            )
                        # payments = [PamentBankCard(
                        #         card_id      = bank_card, 
                        #         date         = get_dt_from_pandas(rec.date),
                        #         date_account = dt.datetime.now(), #['Дата обработки'],
                        #         name         = rec['Название операции'],
                        #         amount       = rec['Сумма операции в валюте карты'],
                        #         category     = rec['Категория'],
                        #         place        = rec['Место операции'],
                        #     ) for i,rec in df.iterrows()
                        # ]
                        PamentBankCard.bulk_create(payments, batch_size=999)
                    except:
                        print('При попытке сохранить в базу данных загруженные данные возникла ошибка')
                        transaction.rollback()
                win.win_message_show(title, 'Загрузка прошла успешно')

def load_payments_from_XML_RNKB(file_name):
    # возвращает словарь результатов:
    # df: DataFrame
    # Параметры выписки (d1, d2, sum1, sum2, приходы, расходы, метка карты)
    # res['success'] = True - флаг успешного чтения формата файла

    res = {}
    res["error_text"] = "" # значение поумолчанию, т.е. нет ошибок
    res['success'] = False
    res['prop'] = [None, None,0,0]  # res['prop'] [Остаток1=None, Остаток2=None, Расходы, Приходы]


    # tag_root
    xlm = ET.parse(file_name)
    tag_root = xlm.getroot()

    level =   '{urn:schemas-microsoft-com:office:spreadsheet}Worksheet'
    level += '/{urn:schemas-microsoft-com:office:spreadsheet}Table'
    level += '/{urn:schemas-microsoft-com:office:spreadsheet}Row'

    rows = []#{0:[], 1:[], 2:[], 3:[], 4:[], 5:[], 6:[], 7:[]}

    # считать данные в список
    for tag_row in tag_root.findall(level):        
        row = []
        for i_cel, tag in enumerate(tag_row.findall('{urn:schemas-microsoft-com:office:spreadsheet}Cell')):            
            text = ''
            for t in tag.itertext():
                text = t
            row.append(text)
        rows.append(row)
    
    if len(rows) < 11:
        res['error_text'] = 'При попытке чтения XML файла возникла ошибка формата файла. Недостаточная длина строк (код 101)'
        res['success'] = False
        return res

    # Заголовки
    # Найти метку
    mark_text = 'Карта'
    if rows[1][0] != mark_text:
        res['error_text'] = 'Ошибка формата файла. Не найдена метка (код 102)'
        res['success'] = False
        return res

    # Найти метку карты (в той же строке)
    res['card_mark'] = rows[1][1]

    # 'd1', 'd2', 'period'
    res['d1'] = datetime.datetime.strptime(rows[3][1], '%d.%m.%Y')
    res['d2'] = datetime.datetime.strptime(rows[4][1], '%d.%m.%Y') + datetime.timedelta(days=1)
    res['period'] = f'за период с xx.xx.20xx по xx.xx.20xx'

    # res['prop'] [Остаток1=None, Остаток2=None, Расходы, Приходы]
    # "Поступления"
    res['prop'][3] = mm.text_to_float(rows[5][1])
    # "Расходы"
    res['prop'][2] = mm.text_to_float(rows[6][1])

# row  11 ----------------- <Element '{urn:schemas-microsoft-com:office:spreadsheet}Row' at 0x000001B75BE28C20>
# [0] 01.04.2022 08:39
# [1] 01.04.2022 00:00
# [2] 
# [3] -50 000.00
# [4] 0.00
# [5] -50 000.00
# [6] RUR
# [7] Другое
# [8]
# row  12 ----------------- <Element '{urn:schemas-microsoft-com:office:spreadsheet}Row' at 0x000001B75BE2F270>
# [0] 01.04.2022 14:37
# [1] 01.04.2022 00:00
# [2] Выдача наличных RUS SEVASTOPOL ATM-8316
# [3] -49 000.00
# [4] 0.00
# [5] -49 000.00
# [6] RUR
# [7] Снятие наличных
# [8]

    rows2 = []
    n1 = len(rows)
    for ind, r1 in enumerate(rows[11:n1]):
        row = []
        
        # date = DateTimeField()
        val = dt.datetime.strptime(r1[0], '%d.%m.%Y %H:%M')
        row.append(val)

        # date_account = DateTimeField(null=True)    
        val = dt.datetime.strptime(r1[1], '%d.%m.%Y %H:%M')
        row.append(val)

        # category = CharField(null=True) 
        val = r1[7]
        row.append(val)

        # name = CharField(null=True)
        val = r1[2]
        row.append(val)

        # amount = FloatField()
        st = r1[3]
        val = mm.text_to_float(st)
        row.append(val)

        # balance
        val = None
        row.append(val)

        # Сохранить строку
        rows2.append(row)

    # res['df']
    # Создать DataFrame из списка rows
    columns=["date", "date_account", "category", "name", "amount", "balance"]
    df = pd.DataFrame(columns=columns, data=rows2).sort_values(by='date')
    res['df'] = df
    res['mess'] = f"Записать/обновить банковскую выписку? \n\n\
            Карта: {res['card_mark']}\n\
            {res['period']}\n\
            Приходы: {res['prop'][3]:_.2f}  \n\
            Расходы: {res['prop'][2]:_.2f}".replace('_', ' ')
    res['success'] = True
    # df.to_csv('test_out2.csv', sep=';', decimal=',', encoding='cp1251')

    return res

def load_payments_from_XML_sber(file_name):
    # возвращает словарь результатов:
    # df: DataFrame
    # Параметры выписки (d1, d2, sum1, sum2, приходы, расходы, метка карты)

    res = {}
    res["error_text"] = "" # значение поумолчанию, т.е. нет ошибок
    res['success'] = False

    # tag_root
    xlm = ET.parse(file_name)
    tag_root = xlm.getroot()

    level =   '{urn:schemas-microsoft-com:office:spreadsheet}Worksheet'
    level += '/{urn:schemas-microsoft-com:office:spreadsheet}Table'
    level += '/{urn:schemas-microsoft-com:office:spreadsheet}Row'

    rows = []#{0:[], 1:[], 2:[], 3:[], 4:[], 5:[], 6:[], 7:[]}

    flag_mark = False  # Найти текст 'Карта'
    flag_card = False  # Найти метку карты
    for i_row, tag_row in enumerate(tag_root.findall(level)):
        
        # flag1_mark  Найти текст 'Карта'
        if i_row == 5:
            for text in tag_row.itertext():
                if text == 'Карта':
                    flag_mark = True
                break               # д.б. единственная строка
            if not flag_mark:
                res["error_text"] = 'При попытке чтения XML файла в строке 5 не найдена метка "Карта" (код 001)'
                return res

        # Найти метку карты
        # res['card_mark']
        elif i_row == 6:

            for i, text in  enumerate(tag_row.itertext()):
                res['card_mark'] = text # Maestro •••• 6632
                flag_card = True        # допуск на дальнейший парсинг
                break                   # д.б. единственная строка
            if not flag_card:
                res["error_text"] = 'При попытке чтения XML файла в строке 7 не найден текст с номером карты (код 002)'
                return res

        # res['period']
        elif i_row == 7:
            # д.б. единственная строка в цикле
            for text in tag_row.itertext():
                res['period'] = text    # Итого по операциям с 01.03.2022 по 31.03.2022
                i1 = text.find(' с ') + 3
                i2 = text.find(' по ') + 4
                if len(text) == 45: # len(text)=45
                    t1 = text[21:31]
                    t2 = text[35:45]
                    res['d1'] = datetime.datetime.strptime(t1, '%d.%m.%Y')
                    res['d2'] = datetime.datetime.strptime(t2, '%d.%m.%Y') + datetime.timedelta(days=1)
                else:
                    error_text = f'При попытке чтения XML \n\
                        {file_name} \n не считаны данные о периоде выписки. \n\
                        длина строки д.б. равна 45: ltn(text)={len(text)}'
                    res["error_text"] = error_text
                    print(error_text)
                    res['d1'] = None
                    res['d2'] = None
                break                   
        
        # res['prop'] [Остаток1, Остаток2, Расходы, Приходы]
        elif i_row == 9:
            amounts = []
            for i, text in enumerate(tag_row.itertext()):
                if i >= 4: break            
                val = mm.text_to_float(text)
                amounts.append(val)
            res['prop'] = amounts

        elif i_row >= 19:        
            # print('row ', i_row, '-----------------', tag_row)

            row = []
            for i_cel, tag in enumerate(tag_row.findall('{urn:schemas-microsoft-com:office:spreadsheet}Cell')):            
                if i_cel > 7: break
                text = ''
                for t in tag.itertext():
                    text = t
                row.append(text)
            # row.insert(0, len(row))
            if len(row) == 8:
                rows.append(row)


    # Обработать rows в массив записей rows_ar
    len1 = len(rows)
    len2 = len1//2
    if len1%2 != 0:
        res["error_text"] = f'При попытке чтения XML файла считано не четное количество строк в таблице: {len1}'
        return res
    rows2 = []

    #   Date	    Time  ...   Name	...	         Amount	....	Balance	Amount_num	Balance_num
    # 0	2022-03-31	15:44		Перевод с карты		5 000,00		337.94	5000.00	337.94
    # 1	2022-03-31	202880		SBOL перевод 2202****6497 В. СЕРГЕЙ СЕРГЕЕВИЧ					NaN	NaN
    for i2 in range(0, len2):
        i1 = 2*i2
        r1 = rows[i1]
        r2 = rows[i1+1]    
        row = []
        
        # date = DateTimeField()
        val = dt.datetime.strptime(r1[0] + ' ' + r1[1], '%Y-%m-%d %H:%M')
        row.append(val)

        # date_account = DateTimeField(null=True)    
        val = dt.datetime.strptime(r2[0], '%Y-%m-%d')
        row.append(val)

        # category = CharField(null=True) 
        val = r1[3]
        row.append(val)

        # name = CharField(null=True)
        val = r2[3]
        row.append(val)

        # amount = FloatField()
        st = r1[5]
        val = mm.text_to_float(st) if st[0] == '+' else -mm.text_to_float(st)
        row.append(val)

        # balance
        val = mm.text_to_float(r1[7])
        row.append(val)

        # Сохранить в массив 
        rows2.append(row)

    # res['df']
    # Создать DataFrame из списка rows
    columns=["date", "date_account", "category", "name", "amount", "balance"]
    df = pd.DataFrame(columns=columns, data=rows2).sort_values(by='date')
    res['df'] = df
    res['mess'] = f"Записать/обновить банковскую выписку? \n\n\
            Карта: {res['card_mark']}\n\
            {res['period']}\n\
            Приходы: {res['prop'][3]:_.2f}  \n\
            Расходы: {res['prop'][2]:_.2f}  \n\
            Остаток на начло периода: { res['prop'][0]:_.2f}\n\
            Остаток на конец периода: { res['prop'][1]:_.2f}".replace('_', ' ')
    res['success'] = True
    # df.to_csv('test_out2.csv', sep=';', decimal=',', encoding='cp1251')

    return res

def load_payments_from_CSV_RNKB(file_name):
    # Загрузить файл в DataFrame
        
    df = pd.read_csv(file_name, sep=';', encoding='cp1251')

    # Создать столбец "date" (перобразовать тип поля текст в дату)
    df["date"] = pd.to_datetime(df["Дата операции"], dayfirst=True)
    
    # Расчет приходов и расходов по карте за период
    mask_receipt = df["Сумма операции в валюте карты"] > 0
    mask_expense = df["Сумма операции в валюте карты"] < 0
    df['receipt'] = df[mask_receipt]["Сумма операции в валюте карты"]
    df['expense'] = -df[mask_expense]["Сумма операции в валюте карты"]
    # df.receipt.sum(), df.expense.sum()

    # Получить объект банковской карты
    sel = BankCard.select().where(BankCard.number == '2200020233972043')
    if len(sel) != 1:
        print("В базе данных не найдена банковская карта с запрашиваемым именем")
        return
    bank_card = sel.get()

def get_bank_card(card_number=None, card_mark=None):

    if card_number != None:
        sel = BankCard.select().where(BankCard.number == card_number)
        if len(sel) != 1:
            win.win_message_show('Загрузка банковской выписки', 'В базе данных не найдена банковская карта с запрашиваемым номером')
            print("В базе данных не найдена банковская карта с запрашиваемым номером")
            return
        bank_card = sel.get()
        # print(f'{bank_card.name}: {bank_card.number}')
        return bank_card

    if card_mark != None:
        sel = BankCard.select().where(BankCard.mark == card_mark)
        if len(sel) != 1:
            win.win_message_show('Загрузка банковской выписки', 'В базе данных не найдена банковская карта с запрашиваемым именем')
            print("В базе данных не найдена банковская карта с запрашиваемым именем")
            return
        bank_card = sel.get()
        # print(f'{bank_card.name}: {bank_card.number}')
        return bank_card
    

def main():

    res = load_payments_from_XML_sber("D:\\IDE_prj\\project_KnowledgeBase\\personal_expenses\data_input\\tests\\test.xml")
    print(res)
    # print(res.prop)


if __name__ == '__main__':
    main()