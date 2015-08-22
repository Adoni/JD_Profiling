from sklearn.externals.joblib import Memory
from sklearn.datasets import load_svmlight_file
from settings import RAW_DATA_DIR
from settings import self_training_file_dir
from settings import base_dir
from sklearn.naive_bayes import MultinomialNB
from sklearn.linear_model import LogisticRegression
import numpy

def get_data(attribute):
    labeled_train = load_svmlight_file(self_training_file_dir+'labeled_train_%s.data'%(attribute),n_features=11000)
    unlabeled_train = load_svmlight_file(self_training_file_dir+'unlabeled_train_%s.data'%(attribute),n_features=11000)
    test = load_svmlight_file(self_training_file_dir+'test_%s.data'%(attribute),n_features=11000)
    return labeled_train,unlabeled_train,test

def learn(train,test):
    train_x,train_y=train
    test_x,test_y=test
    clf = MultinomialNB()
    #clf = LogisticRegression()
    clf.fit(train_x, train_y)
    return clf,clf.score(test_x,test_y)

def extract_new_data(result,count):
    good_x=[]
    good_y=[]
    bad_x=[]
    bad_y=[]
    result0=sorted(filter(lambda r:r[1][0]>r[1][1],result),key=lambda d:sum(d[0]),reverse=True)
    result1=sorted(filter(lambda r:r[1][0]<r[1][1],result),key=lambda d:sum(d[0]),reverse=True)
    count=count/2

    for r in result0[:count]+result1[:count]:
        good_x.append(r[0])
        good_y.append(0 if r[1][0]>r[1][1] else 1)
    for r in result0[count:]+result1[count:]:
        bad_x.append(r[0])
        bad_y.append(0 if r[1][0]>r[1][1] else 1)
    return numpy.array(good_x),numpy.array(good_y),numpy.array(bad_x),numpy.array(bad_y)

def iterate(attribute,iterate_count,new_data_count):
    print ''
    labeled_train,unlabeled_train,test=get_data(attribute)
    labeled_train=[labeled_train[0].toarray(),labeled_train[1]]
    unlabeled_train=[unlabeled_train[0].toarray(), unlabeled_train[1]]
    test=[test[0].toarray(),test[1]]
    scores=[]
    for i in xrange(iterate_count):
        print '----------------'
        print 'Iterate: %d'%i
        print 'Labeled training data size: %d'%(len(labeled_train[0]))
        print 'Unlabeled training data size: %d'%(len(unlabeled_train[0]))
        print 'Testing data size: %d'%(len(test[0]))
        clf,score=learn(labeled_train,test)
        print 'Accurate: %0.4f'%score
        scores.append(score)
        result=clf.predict_proba(unlabeled_train[0])
        good_x,good_y,bad_x,bad_y=extract_new_data(zip(unlabeled_train[0],result),new_data_count)
        if len(good_x)==0:
            print 'No more new train data!'
            break
        print 'New training data size: %d'%(len(good_x))
        labeled_train[0]=numpy.concatenate((labeled_train[0], good_x), axis=0)
        labeled_train[1]=numpy.concatenate((labeled_train[1], good_y), axis=0)
        unlabeled_train=[bad_x,bad_y]
    print '--------'
    for s in scores:
        print s
    print '--------'
