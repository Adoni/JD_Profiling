from pymongo import Connection
from settings import RAW_DATA_DIR
from settings import base_dir
from settings import labeled_feature_file_dir
from collections import Counter
from small_utils.progress_bar import progress_bar
from tools import get_balance_params
from tools import get_features

def get_word_count():
    collection=Connection().jd.train_users
    count=dict()
    for user in collection.find():
        for m,v in user['mentions'].items():
            if m in count:
                count[m]+=v
            else:
                count[m]=v
    for m,v in sorted(count.items(),key=lambda d:d[1]):
        print m,v

def statistics(attribute,threshold=-1,feature_file_name=base_dir+'/features/mention.feature',show=False):
    import random
    collection=Connection().jd.test_users
    balance_params=get_balance_params(attribute,collection)
    all_features=get_features(feature_file_name)
    bar=progress_bar(collection.count())
    distribute=dict([f,[0.,0.]] for f in all_features)
    labels_distribute=[0.,0.]
    for index,user in enumerate(collection.find()):
        try:
            label=user['profile'][attribute].index(1)
        except:
            continue
        #if random.random()>balance_params[label]:
        #    continue
        features=dict(user['mentions'])
        products=Counter(user['products'])
        for p in products:
            features[p]=products[p]
        if len(features)<10:
            continue
        for f in features:
            if f in distribute:
                distribute[f][label]+=1#features[f]
        labels_distribute[label]+=1
        bar.draw(index)
    for f in distribute.keys():
        if sum(distribute[f])<threshold:
            distribute.pop(f)
    print labels_distribute
    for f in distribute:
        distribute[f][0]/=labels_distribute[0]
        distribute[f][1]/=labels_distribute[1]
    for f in distribute:
        s=sum(distribute[f])
        distribute[f][0]/=s
        distribute[f][1]/=s
    if not show:
        return distribute
    #distribute=filter(lambda d:d[1][0]<d[1][1], distribute.items())
    distribute=sorted(distribute.items(),key=lambda d:abs(1-2*(d[1][0]+0.1)/(sum(d[1])+0.1)), reverse=True)
    #distribute=sorted(distribute,key=lambda d:sum(d[1]), reverse=True)
    print ''
    for d in distribute[:50]:
        print '%s 0:%0.3f 1:%0.3f'%(d[0].encode('utf8'), (d[1][0]+0.1)/(sum(d[1])+0.1),1-(d[1][0]+0.1)/(sum(d[1])+0.1),)

def get_labels_after_train(attribute,method):
    labels=dict()
    for line in open(RAW_DATA_DIR+'%s/train_classify_result_%s.data'%(method,attribute)):
        line=line[:-1].split('\t')
        if abs(float(line[2])-float(line[4]))<0.0:
            continue
        if float(line[2])>float(line[4]):
            labels[line[0]]=int(line[1])
        else:
            labels[line[0]]=int(line[3])
    return labels

def statistics_after_train(attribute,method,threshold=-1,feature_file_name=base_dir+'/features/mention.feature',show=False):
    import random
    labels=get_labels_after_train(attribute,method)
    print len(labels)
    collection=Connection().jd.train_users
    label_distribute=Counter(labels.values())
    balance_params=dict()
    for label in label_distribute:
        balance_params[label]=1.0*min(label_distribute.values())/label_distribute[label]
    all_features=get_features(feature_file_name)
    bar=progress_bar(collection.count())
    distribute=dict([f,[0.,0.]] for f in all_features)
    for index,user in enumerate(collection.find()):
        try:
            label=labels[user['_id']]
        except:
            continue
        #if random.random()>balance_params[label]:
        #    continue
        features=dict(user['mentions'])
        products=Counter(user['products'])
        for p in products:
            features[p]=products[p]
        for f in features:
            if f in distribute:
                distribute[f][label]+=1
        bar.draw(index)
    for f in distribute.keys():
        if sum(distribute[f])<threshold:
            distribute.pop(f)
    print label_distribute
    for f in distribute:
        distribute[f][0]/=label_distribute[0]
        distribute[f][1]/=label_distribute[1]
    for f in distribute.keys():
        s=sum(distribute[f])
        if s==0:
            distribute.pop(f)
            continue
        distribute[f][0]/=s
        distribute[f][1]/=s
    if not show:
        return distribute
    #distribute=filter(lambda d:d[1][0]<d[1][1], distribute)
    distribute=sorted(distribute.items(),key=lambda d:max(d[1])/sum(d[1]), reverse=True)
    #distribute=sorted(distribute,key=lambda d:sum(d[1]), reverse=True)
    print ''
    for d in distribute[:50]:
        print '%s 0:%0.3f 1:%0.3f'%(d[0].encode('utf8'), (d[1][0]+0.1)/(sum(d[1])+0.1),1-(d[1][0]+0.1)/(sum(d[1])+0.1),)

def compair_single(attribute,method):
    d1=statistics(attribute,threshold=50,feature_file_name=base_dir+'/features/all_features.feature')
    d2=statistics_after_train(attribute,method,feature_file_name=base_dir+'/features/all_features.feature')
    result=[]
    labeled_features=[line.split(' ')[0].decode('utf8') for line in
            open(labeled_feature_file_dir+'review_constraint_%s.constraints'%attribute)]
    all_features=get_features(feature_file_name=base_dir+'/features/all_features.feature')
    print '\n======%s======'%attribute
    for f in labeled_features:
        print f
        if f in d1:
            #print d1[f]
            print '%0.2f , %0.2f'%(1.*d1[f][0]/sum(d1[f]),1.*d1[f][1]/sum(d1[f]))
        if f in d2:
            #print d2[f]
            print '%0.2f , %0.2f'%(1.*d2[f][0]/sum(d2[f]),1.*d2[f][1]/sum(d2[f]))

def compair():
    #method='label2trainset'
    method='mallet'
    compair_single('gender',method)
    compair_single('age',method)
    compair_single('location',method)
    compair_single('kids',method)

if __name__=='__main__':
    #statistics('location',threshold=50,show=True,feature_file_name=base_dir+'/features/mention.feature')
    #statistics('kids',threshold=50,show=True)
    statistics_after_train('gender','mallet',threshold=50,show=True,feature_file_name=base_dir+'/features/mention.feature')
    #get_word_count()
    print 'Done'
