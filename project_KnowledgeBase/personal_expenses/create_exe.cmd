rmdir /s /q dist
pyinstaller -F convert_payments_to_json.py
copy dist\convert_payments_to_json.exe "D:\Program Files\MyPyProjects\convert_payments_to_json\convert_payments_to_json.exe"

pause


rem ����� ������� pyinstaller -F -w -i( to set up icon on your .exe) main.py, ��� main.py - ��� python ������. ��� ��� �������� ������ ����: F � ���� ���� �������� �� ��, ����� � ��������� ����� dist, � ������� � ����� ��������� ��� ����������� ���� �� ���� ����� ����� ������ ������, ������� � �.�. -w � ���� ���� ��� ����������� � ��� ������, ���� ���������� ���������� GUI ���������� (tkinter, PyQt5, �.�.), ��� ��������� �������� ����������� ����, ���� �� ���� ���������� ����������, ��� ���� ���� ������������ �� �����. -i � ���� ���� �������� �� ��������� ������ �� ��� ����������� ����, ����� ����� ����� ������� ������ ���� � ������ � ��������� � �����. ��������: D:\LayOut\icon.ico