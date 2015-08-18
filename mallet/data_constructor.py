#coding:utf8
from pymongo import Connection
from settings import RAW_DATA_DIR
from tools import balance
from collections import Counter
from small_utils.progress_bar import progress_bar
from tools import get_balance_params
from tools import get_features


def construct_train_data():
    import random
    all_features=get_features()
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
    all_features=get_features()
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
            if f in [u'宝宝',u'儿子',u'女儿',u'男朋友',u'女朋友']:
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

def main():
    #construct_train_data()
    #construct_test_data('gender')
    #construct_test_data('age')
    #construct_test_data('kids')
    #construct_test_data('location')
    statistics('location',threshold=100,feature_file_name='./features/all_features.feature')

if __name__=='__main__':
    main()
