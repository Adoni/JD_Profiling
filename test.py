#coding:utf8
def count_intersection():
    from pymongo import Connection
    from collections import Counter
    jd_ids=set(map(lambda d:str(d['_id']),Connection().jd.users.find({},{'_id':1})))
    linked_jd_ids=map(lambda d:d,Connection().jd.weibo_users.find({},{'jd_id':1,'profile':1}))
    linked_jd_ids=filter(lambda d:str(d['jd_id']) in jd_ids,linked_jd_ids)
    print len(linked_jd_ids)
    genders=Counter(map(lambda d:str(d['profile']['gender']),linked_jd_ids))
    print 'Gender'
    for key in genders:
        print key,genders[key]
    ages=Counter(map(lambda d:str(d['profile']['age']),linked_jd_ids))
    print 'Age'
    for key in ages:
        print key,ages[key]
    locations=Counter(map(lambda d:str(d['profile']['location']),linked_jd_ids))
    print 'Location'
    for key in locations:
        print key,locations[key]

def analyze_feature_count(attribute):
    from small_utils.progress_bar import progress_bar
    from pymongo import Connection
    from collections import Counter
    collection=Connection().jd.test_users
    bar=progress_bar(collection.count())
    x=[]
    y=[]
    labels=[]
    for index,user in enumerate(collection.find()):
        try:
            label=user['profile'][attribute].index(1)
        except:
            continue
        labels.append(label)
        x.append(len(user['products']))
        y.append(len(user['mentions'].values()))
        bar.draw(index)
    f=open('./tmp.data','w')
    for i in xrange(len(labels)):
        f.write('%d %d %d\n'%(labels[i],x[i],y[i]))
    print Counter(labels)

def age_distribute():
    from small_utils.progress_bar import progress_bar
    from pymongo import Connection
    from collections import Counter
    collection=Connection().jd.test_users
    weibo_collection=Connection().jd.weibo_users
    linked_jd_ids=dict()
    ages=[]
    for line in open('/mnt/data1/adoni/data/linked_uids.data'):
        linked_jd_ids[line[:-1].split(' ')[1]]=line.split(' ')[0]
    bar=progress_bar(collection.count())
    for index,user in enumerate(collection.find()):
        if sum(user['profile']['age'])==0:
            continue
        weibo_id=linked_jd_ids[user['_id']]
        weibo_user=weibo_collection.find_one({'_id':weibo_id})
        if weibo_user==None:
            continue
        age=2015-int(weibo_user['birthday'].split(u'年')[0])
        if age>50 or age<10:
            continue
        ages.append(age)
        if age<28:
            user['profile']['age']=[0,1]
        else:
            user['profile']['age']=[1,0]
        collection.update({'_id':user['_id']},{'$set':{'profile':user['profile']}})
        bar.draw(index)
    s=sum(Counter(ages).values())
    ages=sorted(Counter(ages).items(),key=lambda d:d[0])
    ss=0.
    for age in ages:
        ss+=age[1]
        print age[0],(ss)/s

if __name__=='__main__':
    analyze_feature_count('age')
    #age_distribute()
