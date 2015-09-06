#coding:utf8
from tools import balance
from pymongo import Connection
from small_utils.progress_bar import progress_bar
from collections import Counter
from tools import get_features
from settings import RAW_DATA_DIR
from tools import get_balance_params
import random
from collections import Counter
from settings import base_dir
import StringIO

feature_file_name=base_dir+'/features/all_features.feature'
labeled_feature_file_dir='/home/adoni/JD_Profiling/mylabel2trainset/labeled_features'

def combine_features(a,b):
    c=dict()
    for key in a:
        c[key]=a[key]
    for key in b:
        c[key]=b[key]
    return c

def construct_train_set(labeled_features,training_count):
    '''
    The format of labeled_feature_file is as the same as mallet
    '''
    all_features=get_features(feature_file_name=feature_file_name)
    all_features_1=get_features(feature_file_name=base_dir+'/features/mention_1.feature',start_index=max(all_features.values())+1)
    collection=Connection().jd.train_users

    bar=progress_bar(collection.count())
    confidence=[]
    for index,user in enumerate(collection.find()):
        label_distributed=[1,1]
        for f,value in combine_features(user['mentions'],Counter(user['products'])).items():
            if f in labeled_features:
                label_distributed[0]*=labeled_features[f][0]*value
                label_distributed[1]*=labeled_features[f][1]*value
        s=1.0*sum(label_distributed)
        if not s==0:
            label_distributed[0]/=s
            label_distributed[1]/=s
        if label_distributed[0]>label_distributed[1]:
            label=0
        elif label_distributed[0]<label_distributed[1]:
            label=1
        else:
            label=-1
        features={}
        #features=user['mentions_0']
        #features=Counter(user['products'])
        features=combine_features(user['mentions_0'],Counter(user['products']))
        sorted_feature=[]
        for f in features:
            if f not in all_features:
                continue
            sorted_feature.append((all_features[f],features[f]))
        user['mentions_1_1']={}
        for f,v in user['mentions_1_1'].items():
            f=f+'_1'
            if f not in all_features_1:
                continue
            sorted_feature.append((all_features_1[f],v))

        if 'user_product_vector_from_deepwalk' in user:
        #if False:
            start_index=max(all_features_1.values())+1
            for i,v in enumerate(user['user_product_vector_from_deepwalk']):
                v=abs(v)
                sorted_feature.append((i+start_index,v))

        keys=map(lambda d:d[0], sorted_feature)
        if not len(keys)==len(set(keys)):
            print Counter(keys).values()
        sorted_feature=sorted(sorted_feature,key=lambda d:d[0])
        str_features=' '.join(map(lambda f:'%s:%f'%f,sorted_feature))
        confidence.append(
                (user['_id'],
                    label,
                    abs(label_distributed[0]-label_distributed[1]),
                    str_features,
                    sum(user['mentions'].values()),
                    ))
        bar.draw(index+1)

    confidence0=filter(lambda d:d[1]==0,confidence)
    confidence0=sorted(confidence0,key=lambda d:d[2],reverse=True)
    confidence1=filter(lambda d:d[1]==1,confidence)
    confidence1=sorted(confidence1,key=lambda d:d[2],reverse=True)
    confidence2=filter(lambda d:d[1]==-1,confidence)
    confidence2=sorted(confidence2,key=lambda d:d[4],reverse=True)

    dimention=min(len(confidence0),len(confidence1),training_count/2)
    confidence0=confidence0[:dimention]
    confidence1=confidence1[:dimention]
    confidence2=confidence2[:dimention]

    print len(confidence0),len(confidence1)

    if len(confidence0)==0 or len(confidence1)==0:
        return False
    labeled_train_data=open(RAW_DATA_DIR+'multi_clf/labeled_train.data','w')
    for d in confidence0+confidence1:
        labeled_train_data.write('%d %s\n'%(d[1],d[3]))

    unlabeled_train_data=StringIO.StringIO()
    labeled_train_data=open(RAW_DATA_DIR+'multi_clf/unlabeled_train.data','w')
    for d in confidence0+confidence1:
        unlabeled_train_data.write('%d %s\n'%(d[1],d[3]))
    return True

def construct_test_set(attribute):
    all_features=get_features(feature_file_name=feature_file_name)
    all_features_1=get_features(feature_file_name=base_dir+'/features/mention_1.feature',start_index=max(all_features.values())+1)
    collection=Connection().jd.test_users
    balance_params=get_balance_params(attribute,collection)
    print balance_params
    bar=progress_bar(collection.count())
    fout=open(RAW_DATA_DIR+'multi_clf/%s_test.data'%attribute,'w')
    for index,user in enumerate(collection.find()):
        try:
            label=user['profile'][attribute].index(1)
        except Exception as e:
            continue
        if random.random()>balance_params[label]:
            continue
        features={}
        #features=user['mentions_0']
        #features=Counter(user['products'])
        features=combine_features(user['mentions_0'],Counter(user['products']))
        sorted_feature=[]
        for f in features:
            if f not in all_features:
                continue
            sorted_feature.append((all_features[f],features[f]))
        user['mentions_1_1']={}
        for f,v in user['mentions_1_1'].items():
            f=f+'_1'
            if f not in all_features_1:
                continue
            sorted_feature.append((all_features_1[f],v))
        if 'user_product_vector_from_deepwalk' in user:
        #if False:
            start_index=max(all_features_1.values())+1
            for i,v in enumerate(user['user_product_vector_from_deepwalk']):
                v=abs(v)
                sorted_feature.append((i+start_index,v))

        if len(sorted_feature)==0:
            continue
        fout.write('%d'%label)
        keys=map(lambda d:d[0], sorted_feature)
        if not len(keys)==len(set(keys)):
            print Counter(keys).values()
        sorted_feature=sorted(sorted_feature,key=lambda d:d[0])
        for f in sorted_feature:
            fout.write(' %s:%f'%f)
        fout.write('\n')
        bar.draw(index+1)

def construct(attribute,training_count):
    construct_train_set(attribute,training_count)
    construct_test_set(attribute)
