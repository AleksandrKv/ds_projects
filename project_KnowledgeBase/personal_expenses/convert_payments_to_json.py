from logging import exception
import re
import sys, os, time
import datetime as dt
import modules.pe_methods as pe

def print_log(file_name_input, result):

    file_name_log = os.path.join(os.path.dirname(__file__), 'convert_payments_to_json.log')
    f = open(file_name_log,'a', encoding='UTF-8') #UTF-8  cp1251
    try:
        print(f"{dt.datetime.today().strftime('%Y-%m-%d %H:%M:%S')} {result} {file_name_input}", file=f)
    finally:
        f.close()    

def main_func():

    if len (sys.argv) == 2:
        file_name_input = sys.argv[1]
        file_name_output = os.path.splitext(file_name_input)[0] + '.json'
        stop_on_complete = True
    else:
        # file_name_input = 'D:\\YandexDisk\\Мои ДОКУМЕНТЫ\\ООО Арсенал-строй (уу)\\!!! Управленческй учет\\Закрытие 2022-03 (март)\\Выписка по дебетовой карте (на русском) MIR 6753.xml'
        file_name_input = 'D:\\YandexDisk\\Мои ДОКУМЕНТЫ\\ООО Арсенал-строй (уу)\\!!! Управленческй учет\\Закрытие 2022-02 (февраль)\\Документ-2022-03-05 Maestro 6632.xml'
        file_name_output = os.path.splitext(file_name_input)[0] + '.json'
        stop_on_complete = False
        # print (f"При запуске программы указано не верное число параметров. \n\
        #     Должно быть 1. Передано :{len(sys.argv)}")
        # print(sys.argv)
        # return

    
    # Уведомление пользователя
    print(f"Сборка программы 107:")
    print(f"------------ Начало конвертации файла ---------------")
    print(f"Папка: {     os.path.dirname( file_name_input) }")
    print(f"Имя файла: { os.path.basename(file_name_input) }")

    try:
        res = pe.convert_payments_to_json(file_name_input, file_name_output)
        if res =='Ok':
            log_text = 'Конвертация прошла успешно!'
        else:
            log_text = f'bad format \n {res}\n'
    except Exception as e:
        log_text = e

    print_log(file_name_input, log_text)
    print(log_text)

    if stop_on_complete:
        # Не закрывать окно консоли после завершения 
        print("Для завершения работы нажмите любую кнопку...")
        from msvcrt import getch
        key=getch()
        # if key==b'\r':
        #     sys.exit()    
        

if __name__ == "__main__":

    main_func()

