from mylabel2trainset.data_constructor import *
from mylabel2trainset.learn import *
import os
def learn_single(attribute,count):
    print '========%s:%d========'%(attribute,count)
    construct(attribute,training_count=count)
    return learn(attribute)

def test_count_and_learn(attribute):
    accurates=[]
    for count in range(1,10):
        a=learn_single(attribute,count*1000)
        accurates.append(a)
    print ''
    print '-----%s-----'%attribute
    for a in accurates:
        print a
    print '------------'

def main():
    pass

if __name__=='__main__':
    os.system('cp -r /home/adoni/JD_Profiling/labeled_features/ /home/adoni/JD_Profiling/mylabel2trainset/')
    print learn_single('age',50000)
    print learn_single('gender',50000)
    print learn_single('kids',50000)
    print learn_single('location',50000)
    #construct_all_data()
    #test_count_and_learn('gender')
    #test_count_and_learn('age')
    #test_count_and_learn('location')
    #test_count_and_learn('kids')
    print 'Done'
