from models import *

def get_payments():    
    with db:
        res = Payment.select()
    return res


