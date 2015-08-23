from mallet.data_constructor import *
from statistics import *

def test(attribute):
    construct_label_train_set(attribute,50000)
    construct_test_data(attribute)

if __name__=='__main__':
    test('gender')
    test('age')
    test('location')
    test('kids')
