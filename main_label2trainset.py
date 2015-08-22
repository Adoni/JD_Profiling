from label2trainset.data_constructor import *
from label2trainset.learn import *
def learn_single(attribute,count):
    print '========%s:%d========'%(attribute,count)
    construct(attribute,training_count=count)
    return learn(attribute)

def test_count_and_learn(attribute):
    accurates=[]
    for count in range(1,20):
        count=count*2000
        a,c=learn_single(attribute,count)
        accurates.append(a)
        print ''
        if c<count:
            print c
            break
    print '-----%s-----'%attribute
    for a in accurates:
        print a
    print '------------'

def main():
    pass

if __name__=='__main__':
    print learn_single('gender',50000)
    print learn_single('age',50000)
    print learn_single('location',50000)
    print learn_single('kids',50000)
    #test_count_and_learn('gender')
    #test_count_and_learn('kids')
    #test_count_and_learn('age')
    #test_count_and_learn('location')
