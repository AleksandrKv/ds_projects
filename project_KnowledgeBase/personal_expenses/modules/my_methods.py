"""     my_methods (ver 01)
Модуль содежит функции общего назначения, 
не привязанные к конкретному проекту
"""

import sys, os
import time
import datetime as dt

## Функция добавляет папки проекта в sys.path
# path = load_my_modules()
# print(path)
def load_my_modules(prj_name=None, lst=None):

    import sys, os

    if prj_name==None:  prj_name = 'project_KnowledgeBase'       
    if lst==None:       lst = [
            '\\my_methods',
            '\\personal_expenses\\modules'
            # '\\qqq,',        
    ]

    # Получить текущую папку
    cwd = os.getcwd()
    prj_len = len(prj_name)
    i1 = cwd.find(prj_name)
    prj_dir = cwd[0:i1+prj_len]
    # d:\IDE_prj\project_KnowledgeBase

    # '\' -> '\\'
    if not prj_dir.find('\\\\'):
        prj_dir = prj_dir.replace('\\', '\\\\')
    
    # Проверить наличие модулей в sys.path_hook
    # Если отсутствют - добавить
    for module_dir in lst:
        module_dir = prj_dir + module_dir
        if not module_dir in sys.path:
            sys.path.insert(0, module_dir)
    return sys.path

# Преобразоватение текста в число (Float)
# избавляемся от всех пробелов, заменяем "," на точки
def text_to_float(text):
    try: 
        text = str.replace(text, ' ', '')
        text = str.replace(text, ',', '.')
        return float(text)
    except: 
        return None

def get_dt_from_pandas(value):
    return dt.datetime(
        value.year,
        value.month,
        value.day,
        value.hour,
        value.minute,
        value.second
    )

def datetime_to_sec1970(value):
    # Проверка наличия часового пояса в переменной
    if value.tzinfo == None: 
        # Установка смещения времени в +00
        sec1970=value.replace(tzinfo= dt.timezone.utc).timestamp()
    else:
        # Расчет секунд с учетом смещения часового пояса
        sec1970=value.timestamp()
    return sec1970

def sec1970_to_datetime(sec1970, timezone=None):
    dt_time = dt.datetime.fromtimestamp(sec1970, tz=timezone)
    return dt_time