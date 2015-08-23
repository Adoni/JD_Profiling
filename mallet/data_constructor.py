#coding:utf8
from pymongo import Connection
from settings import RAW_DATA_DIR
from tools import balance
from collections import Counter
from small_utils.progress_bar import progress_bar
from tools import get_balance_params
from tools import get_features
from settings import base_dir
from settings import labeled_feature_file_dir


feature_file_name=base_dir+'/features/all_features.feature'

def combine_features(a,b):
    c=dict()
    for key in a:
        c[key]=a[key]
    for key in b:
        c[key]=b[key]
    return c

def construct_label_train_set(attribute,training_count):
    '''
    The format of labeled_feature_file is as the same as mallet
    '''
    all_features=get_features(feature_file_name=feature_file_name)
    labeled_feature_file=open('%s/review_constraint_%s.constraints'%(labeled_feature_file_dir,attribute))
    labeled_features=dict()
    for line in labeled_feature_file:
        line=line[:-1].split(' ')
        labeled_features[line[0].decode('utf8')]=map(lambda d:float(d.split(':')[1]),line[1:])
    collection=Connection().jd.train_users

    bar=progress_bar(collection.count())
    confidence=[]
    for index,user in enumerate(collection.find()):
        label_distributed=[1,1]
        for f,value in user['mentions'].items():
            if f in labeled_features:
                label_distributed[0]*=labeled_features[f][0]*value
                label_distributed[1]*=labeled_features[f][1]*value
        s=1.0*sum(label_distributed)
        label_distributed[0]/=s
        label_distributed[1]/=s
        if label_distributed[0]>label_distributed[1]:
            label=0
        elif label_distributed[0]<label_distributed[1]:
            label=1
        else:
            continue
        #features=user['mentions']
        #features=Counter(user['products'])
        features=combine_features(user['mentions'],Counter(user['products']))
        sorted_feature=[]
        for f in features:
            if f not in all_features:
                continue
            sorted_feature.append((all_features[f],features[f]))
        sorted_feature=sorted(sorted_feature,key=lambda d:d[0])
        str_features=' '.join(map(lambda f:'%s %d'%f,sorted_feature))
        confidence.append(
                (user['_id'],
                    label,
                    abs(label_distributed[0]-label_distributed[1]),
                    str_features))
        bar.draw(index+1)

    confidence0=filter(lambda d:d[1]==0,confidence)
    confidence0=sorted(confidence0,key=lambda d:d[2],reverse=True)
    confidence1=filter(lambda d:d[1]==1,confidence)
    confidence1=sorted(confidence1,key=lambda d:d[2],reverse=True)

    dimention=min(len(confidence0),len(confidence1))
    #confidence0=confidence0[:dimention]
    #confidence1=confidence1[:dimention]
    print len(confidence0),len(confidence1)
    fout=open(RAW_DATA_DIR+'mallet/mallet_train_%s.data'%attribute,'w')
    for d in confidence0+confidence1:
        fout.write('%s %d %s\n'%(d[0],d[1],d[3]))

def construct_train_data():
    import random
    all_features=get_features(feature_file_name=feature_file_name)
    collection=Connection().jd.train_users
    fout=open(RAW_DATA_DIR+'mallet/mallet_train.data','w')
    bar=progress_bar(collection.count())
    for index,user in enumerate(collection.find()):
        uid=user['_id']
        features=dict(user['mentions'])
        products=Counter(user['products'])
        for p in products:
            features[p]=products[p]
        fout.write('%s %d'%(uid,random.randint(0,1)))
        for f in features:
            if f not in all_features:
                continue
            fout.write(' %s %d'%(all_features[f],features[f]))
        fout.write('\n')
        bar.draw(index+1)

def construct_test_data(attribute):
    collection=Connection().jd.test_users
    all_features=get_features(feature_file_name=feature_file_name)
    data=[]
    bar=progress_bar(collection.count())
    for index,user in enumerate(collection.find()):
        uid=user['_id']
        features=dict(user['mentions'])
        products=Counter(user['products'])
        for p in products:
            features[p]=products[p]
        try:
            label=user['profile'][attribute].index(1)
        except Exception as e:
            continue
        x=''
        for f in features:
            if f not in all_features:
                continue
            x+=' %s %d'%(all_features[f],features[f])
        if x=='':
            continue
        data.append((uid,label,x))
        bar.draw(index+1)
    data=balance(data,target_index=1)
    fout=open(RAW_DATA_DIR+'mallet/mallet_test_%s.data'%attribute,'w')
    for d in data:
        fout.write('%s %d %s\n'%d)
