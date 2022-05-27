rmdir /s /q dist
pyinstaller -F convert_payments_to_json.py
copy dist\convert_payments_to_json.exe "D:\Program Files\MyPyProjects\convert_payments_to_json\convert_payments_to_json.exe"

pause


rem ѕишем команду pyinstaller -F -w -i( to set up icon on your .exe) main.py, где main.py - ваш python скрипт. ¬от что означает каждый флаг: F Ц этот флаг отвечает за то, чтобы в созданной папке dist, в которой и будет хранитьс€ наш исполн€емый файл не было очень много лишних файлов, модулей и т.п. -w Ц этот флаг вам понадобитс€ в том случае, если приложение использует GUI библиотеки (tkinter, PyQt5, т.п.), оно блокирует создание консольного окна, если же ваше приложение консольное, вам этот флаг использовать не нужно. -i Ц этот флаг отвечает за установку иконки на наш исполн€емый файл, после флага нужно указать полный путь к иконке с указанием еЄ имени. Ќапример: D:\LayOut\icon.ico