from self_training.data_constructor import *
from self_training.learn import *

def test(attribute):
    print '======%s======'%attribute
    construct(attribute,500)
    iterate(attribute,20,40)

if __name__=='__main__':
    test('gender')
    test('age')
    test('location')
    test('kids')
