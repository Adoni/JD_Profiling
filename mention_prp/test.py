from pymongo import Connection
from collections import Counter
import numpy

def update(collection,max_v):
    length=[]
    for user in collection.find():
        length.append(len(user['mentions'].values()))
        #alpha=1.0*sum(user['mentions'].values())/max_v
        alpha=1.0*len(user['mentions'])/max_v
        F1=dict()
        for key in set(user['mentions_0'].keys()+user['mentions_1'].keys()):
            try:
                f0=user['mentions_0'][key]
            except:
                f0=0.
            try:
                f1=user['mentions_1'][key]
            except:
                f1=0.

            if f0==0 and f1==0:
                continue
            F1[key]=alpha*f0+(1-alpha)*f1
        collection.update({'_id':user['_id']},{'$set':{'mentions_1_1':F1}})

    print max(length)
    print min(length)
    print numpy.mean(length)
    print numpy.var(length)
    print Counter(length)

def main():
    collection=Connection().jd.test_users
    update(collection,81)
    collection=Connection().jd.train_users
    update(collection,81)

if __name__=='__main__':
    main()
