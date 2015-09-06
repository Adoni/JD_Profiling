from mallet.data_constructor import *
from statistics import *

def test(attribute):
    construct_test_data(attribute)

if __name__=='__main__':
    construct_train_data()
    test('gender')
    test('age')
    test('location')
    test('kids')
