#coding:utf8
from pymongo import Connection
from tools import get_mentions
from settings import RAW_DATA_DIR
from small_utils.progress_bar import progress_bar
from settings import base_dir
from collections import Counter
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
    from pyltp import Segmentor
    all_products=get_all_ids_from_file('product')
    collection=Connection().jd.train_users
    fname=RAW_DATA_DIR+'user_review.data'
    f=open(fname)
    count=int(f.readline()[:-1])
    print count
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

def output_user_product_graph():
    fout=open(RAW_DATA_DIR+'graph.data','w')
    collection=Connection().jd.train_users
    bar=progress_bar(collection.count())
    for index,user in enumerate(collection.find()):
        uid=user['_id']
        for pid in user['products']:
            fout.write('%s %s\n'%(uid,pid))
        bar.draw(index+1)

    collection=Connection().jd.test_users
    bar=progress_bar(collection.count())
    for index,user in enumerate(collection.find()):
        uid=user['_id']
        for pid in user['products']:
            fout.write('%s %s\n'%(uid,pid))
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

def insert_LINE_vector(file_name=RAW_DATA_DIR+'normalize2.data'):
    vectors=dict()
    fin=open(file_name)
    line=fin.readline().strip().split(' ')
    count,dimention=int(line[0]),int(line[1])
    bar=progress_bar(count)
    for index in xrange(count):
        line=fin.readline()
        line=line.strip().split(' ')
        vector=map(lambda d:float(d),line[1:])
        vectors[line[0]]=vector
        bar.draw(index+1)
    collection=Connection().jd.train_users
    bar=progress_bar(collection.count())
    for index,user in enumerate(collection.find()):
        if user['_id'] not in vectors:
            vectors[user['_id']]=[0.]*dimention
            continue
        collection.update({'_id':user['_id']},{'$set':{'user_product_vector_from_line':vectors[user['_id']]}})
        bar.draw(index+1)
    collection=Connection().jd.test_users
    bar=progress_bar(collection.count())
    for index,user in enumerate(collection.find()):
        if user['_id'] not in vectors:
            continue
        collection.update({'_id':user['_id']},{'$set':{'user_product_vector_from_line':vectors[user['_id']]}})
        bar.draw(index+1)

def insert_review(collection,fname):
    from collections import Counter
    from pyltp import Segmentor
    f=open(fname)
    count=int(f.readline()[:-1])
    print count
    segmentor=Segmentor()
    segmentor.load('/home/adoni/cws.model')
    bar=progress_bar(count)
    review_count=0
    for i in xrange(count):
        uid=f.readline()[:-1]
        products=f.readline()
        review=f.readline()[:-1].replace('|&|',' ')
        review_count+=len(review)
        continue
        review=[w for w in segmentor.segment(review)]
        collection.update({'_id':uid},{'$set':{'review':review}},safe=True)
        bar.draw(i+1)
    print review_count

def output_features(fname,key):
    fout=open(fname,'w')
    collection=Connection().jd.train_users
    bar=progress_bar(collection.count())
    features=[]
    for index,user in enumerate(collection.find()):
        features+=user[key]
        bar.draw(index+1)
    features=sorted(Counter(features).items(), key=lambda d:d[1],reverse=True)
    fout=open('./features/review.feature','w')
    for f in features:
        fout.write('%s %d\n'%(f[0].encode('utf8'),f[1]))

if __name__=='__main__':
    #construct_data_set('user')
    #construct_data_set('product')
    #output_graph()
    #construct_train_user()
    #construct_train_product()
    #construct_test_user()
    #attribute_statistics('gender')
    #attribute_statistics('age')
    #attribute_statistics('location')
    #attribute_statistics('kids')
    #output_all_features()
    #output_user_product_graph()
    #insert_LINE_vector()
    insert_review(Connection().jd.train_users,RAW_DATA_DIR+'user_review.data')
    #insert_review(Connection().jd.test_users,RAW_DATA_DIR+'test_user_review.data')
    #output_features(base_dir+'/features/review.feature','review')
    print 'Done'
