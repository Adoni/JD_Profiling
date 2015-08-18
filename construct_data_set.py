#coding:utf8
from pymongo import Connection
from tools import get_mentions
from settings import RAW_DATA_DIR
from small_utils.progress_bar import progress_bar
from settings import base_dir
import numpy

mention_words=[line[:-1].split(' ')[0] for line in open(RAW_DATA_DIR+'mention.data')]

def get_all_ids_from_db(collection_name):
    collection=Connection().jd[collection_name]
    ids=map(lambda d:d['_id'],collection.find({},{'_id':1}))
    return ids

def get_all_ids_from_file(entity):
    fname=RAW_DATA_DIR+'%s_review.data'%entity
    f=open(fname)
    count=int(f.readline()[:-1])
    ids=[]
    for i in xrange(count):
        ids.append(f.readline()[:-1])
        f.readline()
        f.readline()
    return set(ids)

def attribute_statistics(attribute):
    from collections import Counter
    print attribute
    collection=Connection().jd.test_users
    profiles=[]
    for user in collection.find():
        if sum(user['profile'][attribute])>0:
            profiles.append(str(user['profile'][attribute]))
    print len(profiles)
    print Counter(profiles)

def count_mentions(review):
    counts=dict()
    for m in mention_words:
        c=review.count(m)
        if c>0:
            counts[m]=c
    return counts

def construct_train_user():
    all_products=get_all_ids_from_file('product')
    collection=Connection().jd.train_users
    fname=RAW_DATA_DIR+'user_review.data'
    f=open(fname)
    count=int(f.readline()[:-1])
    bar=progress_bar(count)
    for i in xrange(count):
        uid=f.readline()[:-1]
        products=f.readline()[:-1].split(' ')
        products=list(set(products)&all_products)
        mentions=count_mentions(f.readline())
        collection.insert({'_id':uid,'products':products,'mentions':mentions})
        bar.draw(i+1)

def construct_test_user():
    all_products=get_all_ids_from_file('product')
    collection=Connection().jd.test_users
    collection.drop()
    linked_users=Connection().jd.weibo_users
    fname=RAW_DATA_DIR+'test_user_review.data'
    uids_with_kids=[line[:-1] for line in open(RAW_DATA_DIR+'uids_with_kids.data')]
    uids_without_kids=[line[:-1] for line in open(RAW_DATA_DIR+'uids_without_kids.data')]
    linked_uids=dict([(line[:-1].split(' ')[1],line[:-1].split(' ')[0]) for line in open(RAW_DATA_DIR+'linked_uids.data')])
    prone_words=['宝宝','女儿','儿子','男朋友','女朋友']
    f=open(fname)
    count=int(f.readline()[:-1])
    bar=progress_bar(count)
    for i in xrange(count):
        uid=f.readline()[:-1]
        products=f.readline()[:-1].split(' ')
        products=list(set(products)&all_products)
        mentions=count_mentions(f.readline())
        profile={
                'gender':[0]*2,
                'age':[0]*2,
                'location':[0]*2,
                'kids':[0]*2,
                }
        if uid in linked_uids:
            user=linked_users.find_one({'_id':linked_uids[uid]})
            if user==None:
                pass
            else:
                profile['gender']=user['profile']['gender']
                profile['age']=user['profile']['age']
                profile['location']=user['profile']['location']
        if uid in uids_with_kids:
            profile['kids']=[0,1]
        if uid in uids_without_kids:
            profile['kids']=[1,0]
        if uid in uids_without_kids or uid in uids_with_kids:
            for w in prone_words:
                if w in mentions:
                    mentions.pop(w)
        collection.insert({'_id':uid,'products':products,'mentions':mentions,'profile':profile})
        bar.draw(i+1)

def construct_train_product():
    all_users=get_all_ids_from_file('user') | get_all_ids_from_file('test_user')
    collection=Connection().jd.train_products
    fname=RAW_DATA_DIR+'product_review.data'
    f=open(fname)
    count=int(f.readline()[:-1])
    bar=progress_bar(count)
    for i in xrange(count):
        pid=f.readline()[:-1]
        users=f.readline()[:-1].split(' ')
        users=list(set(users)&all_users)
        mentions=count_mentions(f.readline())
        collection.insert({'_id':pid,'users':users,'mentions':mentions})
        bar.draw(i+1)

def output_graph():
    uids=[line.split(' ')[0] for line in open(RAW_DATA_DIR+'user_id.data')]
    pids=[line.split(' ')[0] for line in open(RAW_DATA_DIR+'product_id.data')]
    pids=set(pids)
    fout=open(RAW_DATA_DIR+'graph.data','w')
    collection=Connection().jd['users']
    bar=progress_bar(collection.count())
    for index,user in enumerate(collection.find()):
        uid=user['_id']
        for r in user['records']:
            if r[0] not in pids:
                continue
            fout.write('%s %s\n'%(uid,r[0]))
        bar.draw(index+1)

def output_vector(entity_name):
    collection=Connection().jd[entity_name]
    bar=progress_bar(collection.count())
    mentions=get_mentions()
    fout=open(RAW_DATA_DIR+'%s_init_vec.data'%entity_name,'w')
    fout.write('%d %d\n'%(collection.count(),len(mentions)))
    for index,entity in enumerate(collection.find()):
        reviews=' '.join(set(map(lambda r:r[1],entity['records'])))
        vector=map(lambda m:reviews.count(m),mentions)
        if numpy.any(vector):
            fout.write('%s %s\n'%(entity['_id'],' '.join(map(lambda d:str(d),vector))))
        bar.draw(index+1)

def output_all_features():
    fout=open(base_dir+'/features/all_features.feature','w')
    for i in get_all_ids_from_db('train_products')[:10000]+mention_words:
        fout.write('%s\n'%i)
if __name__=='__main__':
    #construct_data_set('user')
    #construct_data_set('product')
    #output_graph()
    #construct_train_user()
    #construct_train_product()
    construct_test_user()
    #attribute_statistics('gender')
    #attribute_statistics('age')
    #attribute_statistics('location')
    #attribute_statistics('kids')
    #output_all_features()
    print 'Done'
