
# Преобразоватение текста в число (Float)
# избавляемся от всех пробелов, заменяем "," на точки
def text_to_float(text):
    try: 
        text = str.replace(text, ' ', '')
        text = str.replace(text, ',', '.')
        return float(text)
    except: 
        return None
