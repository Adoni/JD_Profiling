from pymongo import Connection
from collections import Counter
from small_utils.progress_bar import progress_bar
from multiprocessing import Pool
import numpy
import time


def cosine_sim(a,b):
    if type(a)==dict:
        s=0
        for key in a:
            if key in b:
                s+=a[key]*b[key]
        t=sum(numpy.array(a.values())**2)*sum(numpy.array(b.values())**2)
        if t==0:
            return 0
        return s**2*1.0/t
    elif type(a)==numpy.array:
        return a.dot(b)**2/(a.dot(a)*b.dot(b))

def get_distance(a,b):
    return cosine_sim(a,b)

def init():
    collection=Connection().jd.test_users
    for user in collection.find():
        collection.update({'_id':user['_id']},{'$unset':{'knn_by_mentions':""}})
        collection.update({'_id':user['_id']},{'$unset':{'knn_by_products':""}})

def get_train_user_products():
    collection=Connection().jd.train_users
    bar=progress_bar(collection.count())
    user_products=dict()
    for index,user in enumerate(collection.find()):
        user_products[user['_id']]=dict(Counter(user['products']))
        #user_products[user['_id']]=user['mentions']
        bar.draw(index)
    return user_products

user_products=get_train_user_products()
record1=user_products
record2=user_products
neibor_count=100

def get_knn(uid1):
    if uid1 not in record1:
        return None
    v1=record1[uid1]
    distance=[]
    for uid2,v2 in record2.items():
        if uid1==uid2:
            continue
        d=get_distance(v1,v2)
        distance.append((uid2,d))
    distance=sorted(distance,key=lambda d:d[1],reverse=True)[:neibor_count]
    return distance

def get_exist_uids():
    uids=[]
    fout=open('/mnt/data1/adoni/data/knn_result/knn.data')
    for line in fout:
        uids.append(line.split(' ')[0])
    return set(uids)

def construct_knn():
    uids=user_products.keys()
    uids=list(set(uids)-get_exist_uids())[:1000]
    print 'Start'
    start = time.time()
    pool = Pool()
    r=pool.map(get_knn, uids)
    pool.close()
    pool.join()
    end = time.time()
    fout=open('/mnt/data1/adoni/data/knn_result/knn.data','a')
    for r in zip(uids,r):
        fout.write(r[0])
        for d in r[1]:
            fout.write(' %s:%f'%d)
        fout.write('\n')
    print "read: %f s" % (end - start)

if __name__=='__main__':
    while 1:
        construct_knn()
    print 'Done'
