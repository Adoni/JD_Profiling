from sklearn.externals.joblib import Memory
from sklearn.datasets import load_svmlight_file
from settings import RAW_DATA_DIR
from settings import base_dir
from sklearn.naive_bayes import MultinomialNB
from sklearn.naive_bayes import GaussianNB
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from statistics import *
from data_constructor import *
import numpy

def get_labeled_features(fname):
    features=dict()
    for line in open(fname):
        line=line[:-1].split(' ')
        f=line[0].decode('utf8')
        p0=float(line[1].split(':')[1])
        p1=float(line[2].split(':')[1])
        features[f]=[p0,p1]
    return features

def get_data(fname):
    data = load_svmlight_file(fname,n_features=13000)
    return data[0].toarray(), data[1]

def predict_prob(clfs,accurates,test_dataset):
    test_x,test_y=test_dataset
    results=numpy.zeros((len(test_y),2))
    for i in xrange(len(clfs)):
        results+=accurates[i]*numpy.log(clfs[i].predict_proba(test_x))
    return results

def score(clfs,accurates,test_dataset):
    results=predict_prob(clfs,accurates,test_dataset)
    test_y=test_dataset[1]
    true=0
    false=0
    for i in xrange(len(test_y)):
        r=results[i]
        l=0 if r[0]>r[1] else 1
        if int(l)==test_y[i]:
            true+=1
        else:
            false+=1
    print true,false
    return 1.0*true/(true+false)

def learn(train_datasets,test_dataset):
    test_x,test_y=test_dataset
    clfs=[]
    accurates=[]
    for train_data in train_datasets:
        clf = MultinomialNB()
        #clf = RandomForestClassifier()
        #clf = GaussianNB()
        #clf = LogisticRegression()
        clf.fit(train_data[0],train_data[1])
        accurate=clf.score(test_x,test_y)
        clfs.append(clf)
        accurates.append(accurate)
        print clf.score(train_data[0],train_data[1])
        print accurate
    return clfs,accurates

def iterate_learn(attribute,train_data_count):
    print 'Attribute: %s'%attribute
    train_datasets=[]
    construct_test_set(attribute)
    fname=RAW_DATA_DIR+'multi_clf/%s_test.data'%attribute
    test_dataset=get_data(fname)
    for i in [0]:
        fname=base_dir+'/multi_clf/labeled_features/review_constraint_%s%d.constraints'%(attribute,i)
        labeled_features=get_labeled_features(fname)
        if not construct_train_set(labeled_features,train_data_count):
            continue
        fname=RAW_DATA_DIR+'multi_clf/labeled_train.data'
        train_data=get_data(fname)
        if len(train_data[1])==0:
            continue
        train_datasets.append(train_data)
    clfs,accurates=learn(train_datasets,test_dataset)
    print score(clfs,accurates,test_dataset)
