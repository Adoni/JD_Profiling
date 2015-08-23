from sklearn.externals.joblib import Memory
from sklearn.datasets import load_svmlight_file
from settings import RAW_DATA_DIR
from settings import base_dir
from sklearn.naive_bayes import MultinomialNB
from sklearn.naive_bayes import GaussianNB
from sklearn.linear_model import LogisticRegression
from statistics import *
import numpy

def get_data(attribute,kind):
    data = load_svmlight_file(RAW_DATA_DIR+'mylabel2trainset/%s_%s.data'%(attribute,kind),n_features=12000)
    uids=[line[:-1] for line in open(RAW_DATA_DIR+'mylabel2trainset/%s_%s_uids.data'%(attribute,kind))]
    return data[0].toarray(), data[1], uids

def learn(attribute):
    unlabel_train_x,unlabel_train_y,unlabel_train_uids=get_data(attribute,'train_unlabel')
    train_x,train_y,train_uids=get_data(attribute,'train')
    test_x,test_y,_=get_data(attribute,'test')
    clf = MultinomialNB()
    #clf = GaussianNB()
    #clf = LogisticRegression()
    clf.fit(train_x, train_y)
    fout=open(RAW_DATA_DIR+'mylabel2trainset/train_classify_result_%s.data'%attribute,'w')
    #for uid,y in zip(all_uids[:count],clf.predict_proba(all_x[:count])):
    for uid,y in zip(unlabel_train_uids,clf.predict_proba(unlabel_train_x)):
        fout.write('%s\t0\t%0.4f\t1\t%0.4f\n'%(uid,y[0],y[1]))
    score=clf.score(test_x,test_y)
    print clf.score(train_x,train_y)
    print '------'
    print 'Labeled training data size: %d'%(len(train_x))
    print 'Unlabeled training data size: %d'%(len(unlabel_train_x))
    print 'Testing data size: %d'%(len(test_x))
    print 'Accurate: %0.4f'%(score)
    print '------'
    return score

def update_labeled_feature(attribute,new_labeled_feature, max_count=1):
    fin=open(base_dir+'/mylabel2trainset/labeled_features/review_constraint_%s.constraints'%attribute)
    exist_labes=[line.split(' ')[0].decode('utf8') for line in fin]
    fin.close()
    fout=open(base_dir+'/mylabel2trainset/labeled_features/review_constraint_%s.constraints'%attribute,'a')
    count=0
    for label in new_labeled_feature:
        if label[0] in exist_labes:
            continue
        if sum(label[1])==0:
            break
        d=[1.*label[1][0]/sum(label[1]),1.*label[1][1]/sum(label[1])]
        fout.write('%s 0:%0.3f 1:%0.3f\n'%(label[0].encode('utf8'),d[0],d[1]))
        count+=1
        if count==max_count:
            break

def iterate_learn(attribute,iterate_count,initial_data_count,new_data_count):
    from data_constructor import construct
    print 'Attribute: %s'%attribute
    fout=open(base_dir+'/mylabel2trainset/iterate_result_%s.result'%attribute,'w')
    accurates=[]
    for i in xrange(iterate_count):
        construct(attribute,initial_data_count+i*new_data_count)
        print ''
        print '============'
        print 'Iterate: %d'%i
        print '============'
        accurate=learn(attribute)
        fout.write('%d %0.4f\n'%(i,accurate))
        accurates.append(accurate)
        label_distribute=statistics_after_train(attribute,method='mylabel2trainset',threshold=-1,show=False,feature_file_name=base_dir+'/features/all_features.feature')
        threshold=0.8
        label_distribute=filter(lambda d:1.0*max(d[1])/sum(d[1])>threshold, label_distribute.items())
        label_distribute=sorted(label_distribute,key=lambda d:1.0*max(d[1])/sum(d[1]), reverse=True)
        update_labeled_feature(attribute,label_distribute,max_count=5)
    return accurates

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

def self_training(attribute,iterate_count,initial_data_count,new_data_count):
    from data_constructor import construct
    print ''

    construct(attribute,initial_data_count)
    unlabel_train_x,unlabel_train_y,unlabel_train_uids=get_data(attribute,'train_unlabel')
    train_x,train_y,train_uids=get_data(attribute,'train')
    test_x,test_y,_=get_data(attribute,'test')

    scores=[]
    for i in xrange(iterate_count):
        print '----------------'
        print 'Iterate: %d'%i
        print 'Labeled training data size: %d'%(len(train_x))
        print 'Unlabeled training data size: %d'%(len(unlabel_train_x))
        print 'Testing data size: %d'%(len(test_x))
        clf=MultinomialNB()
        clf.fit(train_x,train_y)
        score=clf.score(test_x,test_y)
        print 'Accurate: %0.4f'%score
        scores.append(score)
        result=clf.predict_proba(unlabel_train_x)
        good_x,good_y,bad_x,bad_y=extract_new_data(zip(unlabel_train_x,result),new_data_count)
        if len(good_x)==0:
            print 'No more new train data!'
            break
        print 'New training data size: %d'%(len(good_x))
        train_x=numpy.concatenate((train_x, good_x), axis=0)
        train_y=numpy.concatenate((train_y, good_y), axis=0)
        unlabel_train_x,unlabel_train_y=bad_x,bad_y
    print '--------'
    for s in scores:
        print s
    print '--------'
