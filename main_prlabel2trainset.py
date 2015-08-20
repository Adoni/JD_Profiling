from prlabel2trainset.data_constructor import *
from prlabel2trainset.learn import *
def test(attribute,count):
    print '========%s:%d========'%(attribute,count)
    #iterate_learn(attribute,10)
    construct(attribute,training_count=count)
    print ''
    print learn(attribute)

def main():
    pass

if __name__=='__main__':
    for count in [8000]:
        test('gender',count)
        test('age',count)
        test('location',count)
        test('kids',count)
