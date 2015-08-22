from sklearn.externals.joblib import Memory
from sklearn.datasets import load_svmlight_file
from settings import RAW_DATA_DIR
from settings import labeled_feature_file_dir
from settings import base_dir
from sklearn.naive_bayes import MultinomialNB
from sklearn.naive_bayes import GaussianNB
from sklearn.linear_model import LogisticRegression
from statistics import *

def get_data(attribute,kind):
    data = load_svmlight_file(RAW_DATA_DIR+'mylabel2trainset/%s_%s.data'%(attribute,kind),n_features=12000)
    uids=[line[:-1] for line in open(RAW_DATA_DIR+'mylabel2trainset/%s_%s_uids.data'%(attribute,kind))]
    return data[0].toarray(), data[1], uids

def learn(attribute):
    #all_x,all_y,all_uids=get_data('all','train')
    train_x,train_y,uids=get_data(attribute,'train')
    test_x,test_y,_=get_data(attribute,'test')
    clf = MultinomialNB()
    #clf = GaussianNB()
    #clf = LogisticRegression()
    clf.fit(train_x, train_y)
    #count=30000
    #count=min(count,all_x.shape[0])
    #fout=open(RAW_DATA_DIR+'mylabel2trainset/train_classify_result_%s.data'%attribute,'w')
    #for uid,y in zip(all_uids[:count],clf.predict_proba(all_x[:count])):
    #    fout.write('%s\t0\t%0.4f\t1\t%0.4f\n'%(uid,y[0],y[1]))
    #print clf.score(train_x,train_y)
    return clf.score(test_x,test_y)

def update_labeled_feature(attribute,new_labeled_feature, max_count=1):
    fin=open(base_dir+'/labeled_features/review_constraint_%s.constraints'%attribute)
    exist_labes=[line.split(' ')[0].decode('utf8') for line in fin]
    fin.close()
    fout=open(base_dir+'/labeled_features/review_constraint_%s.constraints'%attribute,'a')
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

def iterate_learn(attribute,iterate_count,training_count):
    from data_constructor import construct
    fout=open(base_dir+'/mylabel2trainset/iterate_result_%s.result'%attribute,'w')
    accurates=[]
    for i in xrange(iterate_count):
        print i
        construct(attribute,training_count)
        print ''
        accurate=learn(attribute)
        fout.write('%d %0.4f\n'%(i,accurate))
        print accurate
        accurates.append(accurate)
        label_distribute=statistics_after_train(attribute,method='mylabel2trainset',threshold=400,show=False,feature_file_name=base_dir+'/features/mention.feature')
        label_distribute=sorted(label_distribute.items(),key=lambda d:1.0*abs(d[1][0]-d[1][1])/sum(d[1]), reverse=True)
        update_labeled_feature(attribute,label_distribute)
    return accurates
