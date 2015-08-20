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

def construct_knn(neibor_count=100):
    user_products=get_train_user_products()
    collection=Connection().jd.test_users
    bar=progress_bar(collection.count())
    for index,user in enumerate(collection.find()):
        distance=[]
        products=dict(Counter(user['products']))
        #products=user['mentions']
        for uid in user_products:
            if uid==user['_id']:
                continue
            d=get_distance(user_products[uid],products)
            distance.append((uid,d))
        distance=sorted(distance,key=lambda d:d[1],reverse=True)[:neibor_count]
        collection.update({'_id':user['_id']},{'$set':{'knn_by_products':distance}})
        bar.draw(index+1)

if __name__=='__main__':
    #construct_knn()
    init()
