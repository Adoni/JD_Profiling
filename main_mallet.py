from mallet.data_constructor import *
from mallet.statistics import *

def test():
    #construct_test_data('gender')
    #construct_test_data('age')
    #construct_test_data('kids')
    #construct_test_data('location')
    compair('gender')
    compair('age')
    compair('location')
    compair('kids')

if __name__=='__main__':
    test()
