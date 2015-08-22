from pymongo import Connection
from collections import Counter
from small_utils.progress_bar import progress_bar
import numpy

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

def get_uids():
    collection=Connection().jd.test_users
    uids=[]
    for user in collection.find():
        uids.append(user['_id'])
    return uids

def construct_knn(neibor_count=100):
    user_products=get_train_user_products()
    uids=get_uids()
    collection=Connection().jd.test_users
    bar=progress_bar(collection.count())
    for index,uid1 in enumerate(uids):
        user=collection.find_one({'_id':uid1})
        if user==None:
            continue
        if 'knn_by_products' in user:
            continue
        distance=[]
        products=dict(Counter(user['products']))
        #products=user['mentions']
        for uid2 in user_products:
            if uid1==uid2:
                continue
            d=get_distance(user_products[uid2],products)
            distance.append((uid2,d))
        distance=sorted(distance,key=lambda d:d[1],reverse=True)[:neibor_count]
        collection.update({'_id':uid1},{'$set':{'knn_by_products':distance}})
        bar.draw(index+1)

if __name__=='__main__':
    construct_knn()
    #init()
    print 'Done'
