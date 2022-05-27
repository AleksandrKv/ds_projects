from tkinter.tix import Tree
import xml.etree.ElementTree as ET
import numpy as np
import pandas as pd
import time
import datetime as dt
import tkinter as tk
import tkinter.filedialog as fd
import tkinter.messagebox as mb
import modules.my_methods as mm
import modules.win_messages as win
from  modules.models import *
import os, datetime, json

def convert_payments_to_json(file_name_input, file_name_output):
    """ Функция сохраняет исходный файл банковских выписок в формат json     
    """
    res = load_сard_payments(file_name_input)
    if res['success']:

        with open(file_name_output, 'w') as write_file:  # encoding='cp1251' 'UTF-8'

            # conveer datetime to sec1970
            res['d1'] = mm.datetime_to_sec1970(res['d1']) 
            res['d2'] = mm.datetime_to_sec1970(res['d2']) 
            # преобразовать DataFrame в списки и массивы
            df = res.pop('df')
            # res['heads'] = df.columns.to_list()
            # res['FNS_Receipt_Product'] = df.to_numpy()

            # Запись параметров (таблицы)
            # json.dump(res, write_file)
            # Запись таблицы DataFrame
            str_json = df.to_json(orient="records") 
            parsed = json.loads(str_json)
            # json.dumps(parsed, write_file)#, indent=4)              
            json.dump([res, parsed], write_file)

            aa=pd.DataFrame().to_json()
            return 'Ok'

    error_text = res.pop('error_text', 'Не классифицированная ошибка')
    return error_text

def load_сard_payments(file_name):
    """ Функция переберает все имеющиеся функции распознавания и возвращает словарь res:
            res['success']: bool
            df = res['df']: DataFrame 
            d1,d2 = res['d1'], res['d2']
            bank_card = get_bank_card(card_mark=res['card_mark']
            res['error_text']
    """
    ext =  os.path.splitext(file_name)[1].lower()
    load_payments_methods = [
        (load_payments_from_XML_sber, '.xml'),
        (load_payments_from_XML_RNKB, '.xml'),
        (load_payments_from_CSV_RNKB, '.csv'),
    ]

    for method, m_ext in load_payments_methods:

        # Проверить соответствие расширения исходного файла расширению метода
        if ext == m_ext:

            # Выполнить метод
            res = method(file_name=file_name)
            if res['success']:
                return res

    res = {}
    res['success'] = False
    return res

def load_сard_payments_to_sqlite():

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

    title="Загрузка банковской выписки по карте"

    res = load_сard_payments(file_name)


    # Обработать успешную загрузку
    if res['success']:
                df,d1,d2 = res['df'], res['d1'], res['d2']
                bank_card = get_bank_card(card_mark=res['card_mark'])

                # Вопрос да/нет пользователю
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
                mb.showinfo(title, 'Загрузка прошла успешно')
                # win.win_message_show(title, 'Загрузка прошла успешно')
                return
    
    error_text = res.pop('error_text', 'Не классифицированная ошибка')
    mb.showinfo(title, f'Не удалось загрузить файл\n\n{file_name}\n\n' + error_text)

def load_payments_from_XML_sber(file_name):
    # возвращает словарь результатов:
    # df: DataFrame
    # Параметры выписки (d1, d2, sum1, sum2, приходы, расходы, метка карты)

    res = {}
    res["error_text"] = "" # значение поумолчанию, т.е. нет ошибок
    res['success'] = False
    res['prop'] = [0,0,0,0]  # res['prop'] [Остаток1, Остаток2, Расходы, Приходы]

    # tag_root
    xlm = ET.parse(file_name)
    tag_root = xlm.getroot()

    level =   '{urn:schemas-microsoft-com:office:spreadsheet}Worksheet'
    level += '/{urn:schemas-microsoft-com:office:spreadsheet}Table'
    level += '/{urn:schemas-microsoft-com:office:spreadsheet}Row'

    ind = 0
    rows = []
    rows1 = []

    # считать данные в список
    for tag_row in tag_root.findall(level):
        row = []
        for i_cel, tag in enumerate(tag_row.findall('{urn:schemas-microsoft-com:office:spreadsheet}Cell')):            
            text = ''
            for t in tag.itertext():
                text += t
            row.append(text)
        rows.append(row)
        ind +=1
    
    ind = 19
    n_rows = len(rows)
    while ind < n_rows: 

        row=rows[ind]

        # все строки, длиной 8 ячеек
        #   Date	    Time  ...   Name	...	         Amount	....	Balance	Amount_num	Balance_num
        # 0	2022.03.31	15:44		Перевод с карты		5 000,00		337.94	5000.00	337.94
        # 1	2022.03.31	202880		SBOL перевод 2202****6497 В. СЕРГЕЙ СЕРГЕЕВИЧ					NaN	NaN
        if len(row)==8:
            rows1.append(row) 
        # т.к. дина ячеек <> 8
        elif len(row) == 1:       
            if rows[ind-1] == ['В валюте счёта']:
                
                spaces = '     '
                while (spaces in rows[ind][0]) and (n_rows-ind > 5):

                        # проверить задовение 2-х строк в одну (если точнее, то 5 строк в 10. цветной пример см. в xlsx февраль 2022, "Maestro •••• 6632")
                        packet=1     # число строк в группе (задовения)
                        if spaces in rows[ind+2*packet][0]: 
                            packet=2
                            if spaces in rows[ind+2*packet][0]: 
                                packet=3
                                if spaces in rows[ind+2*packet][0]: 
                                    # перебор. делаем ошибку. 
                                    res["error_text"] = f'Ошибка формата Сбер_XML. Превышен допустимый размер пакета строк (код 311)'
                                    return res
                        for p_ind in range(0, packet):                                

                            # считываем строки и записываем их в rows1 (длиной 8)
                            r1=8*[""]
                            r2=8*[""]

                            # val = ['21.02.2022         13:54']     
                            row = rows[ind+2*p_ind + 0]
                            val = row[0]  
                            v1 = f'{val[6:10]}-{val[3:5]}-{val[0:2]}' #  '%d.%m.%Y' -> '%Y-%m-%d'
                            v2 = val[-5:]
                            r1[0] = v1
                            r1[1] = v2

                            # val = ['22.02.2022          209281']
                            row = rows[ind+2*p_ind + 1]
                            val = row[0]
                            v1 = f'{val[6:10]}-{val[3:5]}-{val[0:2]}' #  '%d.%m.%Y' -> '%Y-%m-%d'
                            v2 = val[-6:]
                            r2[0] = v1
                            r2[1] = v2

                            # val = ['Перевод с карты']
                            row = rows[ind + 2*packet + 2*p_ind + 0]
                            val = row[0]
                            r1[3] = val

                            # val = ['SBOL перевод 4276****9099 П. ДЕНИС ЮРЬЕВИЧ']
                            row = rows[ind + 2*packet + 2*p_ind + 1]
                            val = row[0]
                            r2[3] = val

                            # val = ['125 000,00                           70 228,77']
                            row = rows[ind + 4*packet + p_ind]
                            val = row[0]
                            lst = val.split('   ')
                            v1 = lst[0]
                            v2 = lst[-1]
                            r1[5] = v1
                            r1[7] = v2
                            rows1.append(r1)
                            rows1.append(r2)
                        ind += 5*packet
        ind +=1

    if len(rows) < 19:
        res['error_text'] = f'При попытке чтения XML файла возникла ошибка формата файла. Недостаточная длина строк (код 201).\n\
            количество строк: {len(rows)}'
        res['success'] = False
        return res

    # Заголовки
    # Найти метку
    mark_text = 'Карта'
    if rows[5][0] != mark_text:
        res['error_text'] = 'Ошибка формата файла. Не найдена метка (код 202)'
        res['success'] = False
        return res
        
    # Найти метку карты (в той же строке)
    res['card_mark'] = rows[6][0]

    # 'd1', 'd2', 'period'
    text = rows[7][0]
    res['period'] = text    # Итого по операциям с 01.03.2022 по 31.03.2022
    i1 = text.find(' с ') + 3
    i2 = text.find(' по ') + 4
    if len(text) == 45: # len(text)=45
        t1 = text[21:31]
        t2 = text[35:45]
        res['d1'] = datetime.datetime.strptime(t1, '%d.%m.%Y')
        res['d2'] = datetime.datetime.strptime(t2, '%d.%m.%Y')
    else:
        error_text = f'При попытке чтения XML \n\
            {file_name} \n не считаны данные о периоде выписки. \n\
            длина строки д.б. равна 45: ltn(text)={len(text)}'
        res["error_text"] = error_text
        res['success'] = False
        return res


    # res['prop'] [Остаток1, Остаток2, Расходы, Приходы]
    res['prop'][0] = mm.text_to_float(rows[9][0])
    res['prop'][1] = mm.text_to_float(rows[9][2])
    res['prop'][2] = mm.text_to_float(rows[9][4])
    res['prop'][3] = mm.text_to_float(rows[9][6])


    # Обрезать строки заголовка
    rows = rows1

    # Обработать rows в массив записей rows_ar
    len1 = len(rows)
    len2 = len1//2
    if len1%2 != 0:
        res["error_text"] = f'При попытке чтения XML файла считано не четное количество строк в таблице: {len1}'
        res['success'] = False
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
        val = dt.datetime.strptime(r1[0][0:10] + ' ' + r1[1], '%Y-%m-%d %H:%M')
        row.append(val)

        # date_account = DateTimeField(null=True)    
        val = dt.datetime.strptime(r2[0][0:10], '%Y-%m-%d')
        row.append(val)

        # category = CharField(null=True) 
        val = r1[3]
        row.append(val)

        # name = CharField(null=True)
        val = r2[3]
        row.append(val)
        name = val

        # amount = FloatField()
        st = r1[5]
        val = mm.text_to_float(st) 
        # sign
        # Поступления на р/с помечаются символом "+", одноко...
        # При конвертации из pdf в xlsx, при суммах до 1000 руб (без пробелов) знак "+" не сохраняется. 
        # Поэтому вылавливаем частные случаи поступлений на р/с
        sign = -1
        if st[0] == '+':
            sign = +1
        else:
            if val < 1000:
                if name[0:12] == 'SBOL перевод': 
                    if len(name) == 25:
                        sign = +1
        row.append(sign*val)

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

def load_payments_from_XML_sber_old(file_name):
    """ Эта функция воде работала, но перестала. Возможно сменился формат выгрузки со сбера.
    Новая функция должна работать с этим же форматом. После тестирования новой функции, эту можно удалить"""
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
                    res['d2'] = datetime.datetime.strptime(t2, '%d.%m.%Y')# + datetime.timedelta(days=1)
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
    d1 = datetime.datetime.strptime(rows[3][1], '%d.%m.%Y')
    d2 = datetime.datetime.strptime(rows[4][1], '%d.%m.%Y')
    res['d1'] = d1
    res['d2'] = d2# + datetime.timedelta(days=1)
    res['period'] = f'за период с {d1.strftime("%d.%m.%Y")} по {d2.strftime("%d.%m.%Y")}'

    n1 = 10

    for ind in range(5,15):
        row = rows[ind]
        # "Поступления"
        if row[0] == "Поступления":
            res['prop'][3] = mm.text_to_float(row[1])
        # "Расходы"
        elif row[0] == "Расходы":
            res['prop'][2] = mm.text_to_float(row[1])
        # "n1"
        elif row[0] == "Дата операции":
            n1 = ind+1 # Первая стока с датой

        # res['prop'] [Остаток1=None, Остаток2=None, Расходы, Приходы]

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
    n2 = len(rows)
    for ind, r1 in enumerate(rows[n1:n2]):
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
        if r1[4]==0:        # Поле "Комиссия в валюте карты"  почти всегда == 0
            st = r1[3]      # Должно корректно работать, кроме комиссий
        else:
            st = r1[5]      # 3-е поле для комисси банка почему-то идет положительное. Берем 5 поле. Оно отрицательное
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
    
def Load_json_files(path_json=None, path_completed=None):
    
    if path_json==None:      
        path_json = 'D:\\IDE_prj\\project_KnowledgeBase\\personal_expenses\\data_input\\my_tickets_json'
    if path_completed==None: 
        path_completed = 'D:\\IDE_prj\\project_KnowledgeBase\\personal_expenses\\data_input\\my_tickets_json\\completed'

    counts = {
        'Ok': 0,
        'duplicate': 0,
        'fail': 0
    }

    lst_files = os.listdir(path_json)
    for fn in lst_files:
        if fn.endswith(".json"):
            file_name = path_json + '\\' + fn
            res = save_json_to_database(file_name)        
            counts[res] += 1
            # print(res + ': ' + fn)

            # Переместить отработанный файл
            if res =='Ok' or res == 'duplicate':
                os.replace(
                        path_json      + '\\' + fn, 
                        path_completed + '\\' + fn)
    
    # Оповещение пользователю                    
    mess = str(counts)[1:-1].replace(', ', '\n')
    mb.showinfo(title='Загрузка чеков ФНС в базу данных', message=mess)

def save_json_to_database(file_name, path_complete=None):

    try:
        with open(file_name, encoding='utf-8') as json_file:
            data = json.load(json_file) #, cls= encoding='cp1251').
            head=data[0]
            items = head.pop('items')
            df=pd.DataFrame(items)

            # Проверить наличие чека в базе данных
            dateTime = dt.datetime.fromtimestamp(head['dateTime'])
            sel = FNS_Receipt.select().where(
                        (FNS_Receipt.dateTime == dateTime)
                      & (FNS_Receipt.fiscalSign >= head['fiscalSign']) 
            )
            if len(sel) > 0:
                return 'duplicate'        

            # Запись в БД. Транзакции удаления/записи    
            with db.atomic() as transaction:  # transaction.rollback()    

                try:
                    # записать чек (заголовок)                    
                    # columns=["date", "date_account", "category", "name", "amount", "balance"]
                    rec = head
                    receipt = FNS_Receipt(
                            dateTime                = dt.datetime.fromtimestamp(rec['dateTime']),
                            localDateTime           = dt.datetime.strptime(rec['localDateTime'], '%Y-%m-%dT%H:%M'),
                            totalSum                = rec['totalSum']/100,
                            user                    = rec['user'],
                            retailPlaceAddress      = rec.pop('retailPlaceAddress', ''),
                            userInn                 = rec['userInn'],
                            requestNumber           = rec['requestNumber'],
                            shiftNumber             = rec['shiftNumber'],
                            operator                = rec.pop('operator', ''),
                            operationType           = rec['operationType'],
                            cashTotalSum            = rec['cashTotalSum'],
                            ecashTotalSum           = rec['ecashTotalSum'],
                            kktRegId                = rec['kktRegId'],
                            fiscalDriveNumber       = rec['fiscalDriveNumber'],
                            fiscalDocumentNumber    = rec['fiscalDocumentNumber'],
                            fiscalSign              = rec['fiscalSign'],
                            nds18                   = rec.pop('nds18', ''),
                            nds10                   = rec.pop('nds10', ''),
                            code                    = rec['code'],
                            fiscalDocumentFormatVer = rec['fiscalDocumentFormatVer'],
                            retailPlace             = rec['retailPlace'],
                            prepaidSum              = rec['prepaidSum'],
                            creditSum               = rec['creditSum'],
                            provisionSum            = rec['provisionSum'],
                            taxationType            = rec['taxationType'],
                    )
                    receipt.save()


                    # Записать номенклатуру покупок
                    lst = []
                    for i,ser in df.iterrows():
                        rec = ser.to_dict()
                        obj = FNS_Receipt_Product(
                            receipt_id   = receipt.id,
                            name         = rec['name'],        # object 
                            price        = rec['price']/100,   # int64  
                            amount       = rec['sum']/100,     # int64  
                            quantity     = rec['quantity'],    # float64
                            paymentType  = rec.pop('paymentType', ''), # int64  
                            productType  = rec.pop('productType', ''), # int64  
                            nds          = '' #rec['nds'],         # int64  
                        )
                        lst.append(obj)
                    FNS_Receipt_Product.bulk_create(lst, batch_size=999)
                    
                except Exception as e:                    
                    print('При попытке сохранить в базу данных загруженные данные возникла ошибка')
                    print(e)
                    transaction.rollback()
                    raise
    except:
        return 'fail'        
    return 'Ok'      


def main():

    res = load_payments_from_XML_sber("D:\\IDE_prj\\project_KnowledgeBase\\personal_expenses\data_input\\tests\\test.xml")
    print(res)
    # print(res.prop)


if __name__ == '__main__':
    main()