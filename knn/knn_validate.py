#coding:utf8
from pymongo import Connection
from small_utils.progress_bar import progress_bar
import numpy

def get_features_and_labels(attribute):
    from collections import Counter
    import random
    collection=Connection().jd.test_users
    features=dict()
    labels=dict()
    values=[]
    for user in collection.find():
        #if attribute=='kids':
        #    for w in [u'男朋友',u'女朋友',u'孩子',u'宝宝',u'儿子',u'女儿']:
        #        if w in user['mentions']:
        #            user['mentions'].pop(w)
        #if len(user['mentions'])==0:
        #    continue
        if len(user['products'])==0:
            continue
        if sum(user['profile'][attribute])==0:
            continue
        features[user['_id']]=dict(Counter(user['products']))
        labels[user['_id']]=numpy.array(user['profile'][attribute],dtype='float32')
        values.append(str(labels[user['_id']]))
    values=Counter(values)
    min_value=1.0*min(values.values())
    for key in values:
        values[key]=min_value/values[key]
    for uid in features.keys():
        if random.random()>values[str(labels[uid])]:
            features.pop(uid)
            labels.pop(uid)
    return features,labels

def cosine_sim(a,b):
    if type(a)==dict:
        s=0
        for key in a:
            if key in b:
                s+=a[key]*b[key]
        return s**2*1.0/(sum(numpy.array(a.values())**2)*sum(numpy.array(b.values())**2))
    elif type(a)==numpy.array:
        return a.dot(b)**2/(a.dot(a)*b.dot(b))

def get_distance(a,b):
    return cosine_sim(a,b)

def validate_knn(attribute):
    print attribute
    features,labels=get_features_and_labels(attribute)
    neibor_count=100
    f=open('./%s_knn_result.data'%attribute,'w')
    bar=progress_bar(len(features))
    for index,uid1 in enumerate(features):
        distance=[]
        for uid2 in features:
            if uid2==uid1:
                continue
            d=get_distance(features[uid1],features[uid2])
            distance.append((uid2,d))
        distance=sorted(distance,key=lambda d:d[1],reverse=True)[:neibor_count]
        label=labels[uid1]
        plabel=numpy.zeros((len(label)),dtype='float32')
        for d in distance:
            #plabel+=d[1]*labels[d[0]]
            plabel+=labels[d[0]]
        if sum(plabel)==0:
            continue
        plabel/=sum(plabel)
        if label[0]>0:
            f.write('%d %f %f\n'%(0,plabel[0],plabel[1]))
        else:
            f.write('%d %f %f\n'%(1,plabel[0],plabel[1]))
        bar.draw(index+1)

def main():
    validate_knn('gender')
    validate_knn('age')
    validate_knn('location')
    validate_knn('kids')

if __name__=='__main__':
    main()
