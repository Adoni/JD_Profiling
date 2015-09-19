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
from label_arbiter import LabelArbiter


feature_file_name=base_dir+'/features/all_features.feature'

def combine_features(a,b):
    c=dict()
    for key in a:
        c[key]=a[key]
    for key in b:
        c[key]=b[key]
    return c

def dict2mallt(data):
    data=' '.join(map(lambda d:'%d %d'%(d[0],d[1]), data.items()))
    return data

def output(file_name,data):
    fout=open(file_name,'w')
    if type(data)==dict:
        data=data.items()
    for d in data:
        fout.write('%s %d %s\n'%(d[0],d[1],dict2mallt(d[2])))

def get_test_uids():
    collection=Connection().jd.test_users
    uids=set()
    for user in collection.find():
        uids.add(user['_id'])
    return uids

def construct_train_data():
    import random
    all_features=get_features(feature_file_name=feature_file_name)
    review_features=get_features(feature_file_name=base_dir+'/features/review.feature',start_index=max(all_features.values())+1)
    collection=Connection().jd.train_users
    bar=progress_bar(collection.count())
    data=[]
    uids=get_test_uids()
    for index,user in enumerate(collection.find()):
        uid=user['_id']
        if uid in uids:
            continue
        features=combine_features(user['mentions'],Counter(user['products']))
        x=dict()
        for f in features:
            if f not in all_features:
                continue
            x[all_features[f]]=features[f]
        for f,v in Counter(user['review']).items():
            if f not in review_features:
                continue
            x[review_features[f]]=v
        y=random.randint(0,1)
        data.append([uid,y,x])
        bar.draw(index+1)
    output(RAW_DATA_DIR+'mallet/mallet_train.data',data)

def construct_test_data(attribute):
    collection=Connection().jd.test_users
    all_features=get_features(feature_file_name=feature_file_name)
    review_features=get_features(feature_file_name=base_dir+'/features/review.feature',start_index=max(all_features.values())+1)
    data=[]
    bar=progress_bar(collection.count())
    for index,user in enumerate(collection.find()):
        uid=user['_id']
        features=combine_features(user['mentions'],Counter(user['products']))
        try:
            y=user['profile'][attribute].index(1)
        except:
            continue
        x=dict()
        for f in features:
            if f not in all_features:
                continue
            x[all_features[f]]=features[f]

        for f,v in Counter(user['review']).items():
            if f not in review_features:
                continue
            x[review_features[f]]=v
        data.append([uid,y,x])
        bar.draw(index+1)
    #data=balance(data,target_index=1)
    output(RAW_DATA_DIR+'mallet/mallet_test_%s.data'%attribute,data)
