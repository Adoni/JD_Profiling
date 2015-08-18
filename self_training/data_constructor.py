from tools import balance
from settings import labeled_feature_file_dir
from pymongo import Connection
from small_utils.progress_bar import progress_bar
from collections import Counter
from tools import get_features
from settings import RAW_DATA_DIR
from tools import get_balance_params
import random

def construct_all_data():
    '''
    The format of labeled_feature_file is as the same as mallet
    '''
    all_features=get_features()
    collection=Connection().jd.train_users
    bar=progress_bar(collection.count())
    fout=open(RAW_DATA_DIR+'label2trainset/all_train.data','w')
    uid_output=open(RAW_DATA_DIR+'label2trainset/all_train_uids.data','w')
    for index,user in enumerate(collection.find()):
        features=dict(Counter(user['products']))
        for m in user['mentions']:
            features[m]=user['mentions'][m]
        label=0
        fout.write('%d'%label)
        uid_output.write('%s\n'%user['_id'])
        sorted_feature=[]
        for f in features:
            if f not in all_features:
                continue
            sorted_feature.append((all_features[f],features[f]))
        sorted_feature=sorted(sorted_feature,key=lambda d:d[0])
        for f in sorted_feature:
            fout.write(' %s:%d'%f)
        fout.write('\n')
        bar.draw(index+1)

def construct_train_set(attribute):
    '''
    The format of labeled_feature_file is as the same as mallet
    '''
    all_features=get_features()
    labeled_feature_file=open('%s/review_constraint_%s.constraints'%(labeled_feature_file_dir,attribute))
    labeled_features=dict()
    for line in labeled_feature_file:
        line=line[:-1].split(' ')
        labeled_features[line[0].decode('utf8')]=map(lambda d:float(d.split(':')[1]),line[1:])
    collection=Connection().jd.train_users
    bar=progress_bar(collection.count())
    fout=open(RAW_DATA_DIR+'label2trainset/%s_train.data'%attribute,'w')
    uid_output=open(RAW_DATA_DIR+'label2trainset/%s_train_uids.data'%attribute,'w')
    for index,user in enumerate(collection.find()):
        features=dict(Counter(user['products']))
        for m in user['mentions']:
            features[m]=user['mentions'][m]
        label_distributed=[1,1]
        for f in features:
            if f in labeled_features:
                label_distributed[0]*=labeled_features[f][0]*features[f]
                label_distributed[1]*=labeled_features[f][1]*features[f]
        if abs(label_distributed[0]-label_distributed[1])<0.7:
            continue
        if label_distributed[0]>label_distributed[1]:
            label=0
        elif label_distributed[0]<label_distributed[1]:
            label=1
        else:
            continue
        fout.write('%d'%label)
        uid_output.write('%s\n'%user['_id'])
        sorted_feature=[]
        for f in features:
            if f not in all_features:
                continue
            sorted_feature.append((all_features[f],features[f]))
        sorted_feature=sorted(sorted_feature,key=lambda d:d[0])
        for f in sorted_feature:
            fout.write(' %s:%d'%f)
        fout.write('\n')
        bar.draw(index+1)

def construct_test_set(attribute):
    all_features=get_features()
    collection=Connection().jd.test_users
    balance_params=get_balance_params(attribute,collection)
    print balance_params
    bar=progress_bar(collection.count())
    fout=open(RAW_DATA_DIR+'label2trainset/%s_test.data'%attribute,'w')
    uid_output=open(RAW_DATA_DIR+'label2trainset/%s_test_uids.data'%attribute,'w')
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
        fout.write('%d'%label)
        uid_output.write('%s\n'%user['_id'])
        sorted_feature=[]
        for f in features:
            if f not in all_features:
                continue
            sorted_feature.append((all_features[f],features[f]))
        sorted_feature=sorted(sorted_feature,key=lambda d:d[0])
        for f in sorted_feature:
            fout.write(' %s:%d'%f)
        fout.write('\n')
        bar.draw(index+1)

def construct(attribute):
    construct_train_set(attribute)
    construct_test_set(attribute)
