from multi_clf.data_constructor import *
from multi_clf.learn import *
import os
def main():
    os.system('cp -r /home/adoni/JD_Profiling/labeled_features/ /home/adoni/JD_Profiling/multi_clf/')
    pass

if __name__=='__main__':
    iterate_learn('gender',20000)
    iterate_learn('age',20000)
    iterate_learn('location',20000)
    iterate_learn('kids',20000)
    print 'Done'
