#coding:utf8
from tools import balance
from settings import labeled_feature_file_dir
from pymongo import Connection
from small_utils.progress_bar import progress_bar
from collections import Counter
from tools import get_features
from settings import self_training_file_dir
from tools import get_balance_params
import random
from collections import Counter
from settings import base_dir

def construct_train_set(attribute,training_count):
    '''
    The format of labeled_feature_file is as the same as mallet
    '''
    all_features=get_features(feature_file_name=base_dir+'/features/mention.feature')
    labeled_feature_file=open('%s/review_constraint_%s.constraints'%(labeled_feature_file_dir,attribute))
    labeled_features=dict()
    for line in labeled_feature_file:
        line=line[:-1].split(' ')
        labeled_features[line[0].decode('utf8')]=map(lambda d:float(d.split(':')[1]),line[1:])

    collection=Connection().jd.train_users
    bar=progress_bar(collection.count())
    confidence=[]
    for index,user in enumerate(collection.find()):
        features=dict(Counter(user['products']))
        for m in user['mentions']:
            features[m]=user['mentions'][m]
        label_distributed=[1,1]
        for f,value in user['mentions'].items():
            if f in labeled_features:
                label_distributed[0]*=labeled_features[f][0]*value
                label_distributed[1]*=labeled_features[f][1]*value
        s=1.0*sum(label_distributed)
        label_distributed[0]/=s
        label_distributed[1]/=s
        #print label_distributed
        #if abs(label_distributed[0]-label_distributed[1])<0.5:
        #    continue
        if label_distributed[0]>label_distributed[1]:
            label=0
        elif label_distributed[0]<label_distributed[1]:
            label=1
        else:
            label=-1
        sorted_feature=[]
        for f in features:
            if f not in all_features:
                continue
            sorted_feature.append((all_features[f],features[f]))
        sorted_feature=sorted(sorted_feature,key=lambda d:d[0])
        str_features=' '.join(map(lambda f:'%s:%d'%f,sorted_feature))
        confidence.append((
                    user['_id'],
                    label,
                    abs(label_distributed[0]-label_distributed[1]),
                    str_features
                    ))
        bar.draw(index+1)

    confidence=sorted(confidence,key=lambda d:d[2],reverse=True)
    confidence0=filter(lambda d:d[1]==0,confidence)[:training_count/2]
    confidence1=filter(lambda d:d[1]==1,confidence)[:training_count/2]
    confidence_unlabel=[]
    confidence_unlabel+=filter(lambda d:d[1]==-1,confidence)
    #confidence_unlabel+=filter(lambda d:d[1]==0,confidence)[training_count/2:training_count*5]
    #confidence_unlabel+=filter(lambda d:d[1]==1,confidence)[training_count/2:training_count*5]
    confidence_unlabel=confidence_unlabel[:5*training_count]
    print len(confidence0),len(confidence1)
    fout=open(self_training_file_dir+'labeled_train_%s.data'%attribute,'w')
    for d in set(confidence0+confidence1):
        fout.write('%d %s\n'%(d[1],d[3]))
    fout_unlabel=open(self_training_file_dir+'unlabeled_train_%s.data'%attribute,'w')
    for d in confidence_unlabel:
        fout_unlabel.write('%d %s\n'%(d[1],d[3]))

def construct_test_set(attribute):
    all_features=get_features(feature_file_name=base_dir+'/features/mention.feature')
    collection=Connection().jd.test_users
    balance_params=get_balance_params(attribute,collection)
    print balance_params
    bar=progress_bar(collection.count())
    fout=open(self_training_file_dir+'test_%s.data'%attribute,'w')
    for index,user in enumerate(collection.find()):
        features=dict(Counter(user['products']))
        for m in user['mentions']:
            features[m]=user['mentions'][m]
        try:
            label=user['profile'][attribute].index(1)
        except Exception as e:
            continue
        if random.random()>balance_params[label]:
            continue
        sorted_feature=[]
        for f in features:
            if f not in all_features:
                continue
            sorted_feature.append((all_features[f],features[f]))
        if len(sorted_feature)==0:
            continue
        fout.write('%d'%label)
        sorted_feature=sorted(sorted_feature,key=lambda d:d[0])
        for f in sorted_feature:
            fout.write(' %s:%d'%f)
        fout.write('\n')
        bar.draw(index+1)

def construct(attribute,training_count):
    construct_train_set(attribute,training_count)
    construct_test_set(attribute)
