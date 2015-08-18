from label2trainset.data_constructor import *
from label2trainset.learn import *
def test(attribute):
    print '========%s========'%attribute
    #iterate_learn(attribute,10)
    construct(attribute)
    print ''
    print learn(attribute)

def main():
    pass

if __name__=='__main__':
    test('gender')
    test('age')
    test('location')
    test('kids')
