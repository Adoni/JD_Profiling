from pymongo import Connection
from small_utils.progress_bar import progress_bar

def update_min_max_sum(entity):
    '''
    Used to insert min max and sum
    '''
    collection=Connection().jd['train_%s_mentions'%entity]
    collection_user=Connection().jd['train_%ss'%entity]
    mentions=[line[:-1].decode('utf8') for line in open('../features/mention.feature')]
    min_d=dict()
    max_d=dict()
    sum_d=dict()
    sum_u_d=dict()
    for m in mentions:
        min_d[m]=float('inf')
        max_d[m]=-1
        sum_d[m]=0
        sum_u_d[m]=0
    for user in collection_user.find():
        for m in user['mentions']:
            v=user['mentions'][m]
            if v<min_d[m]:
                min_d[m]=v
            if v>max_d[m]:
                max_d[m]=v
            sum_d[m]+=v
            sum_u_d[m]+=1
    for m in mentions:
        collection.insert({'_id':m,'distribute':[min_d[m],max_d[m],sum_d[m],sum_u_d[m]]})

def update(collection):
    for c in collection.find():
        mentions=c['mentions']
        s=1.0*sum(mentions.values())
        for m in mentions:
            mentions[m]/=s
        #collection.update({'_id':c['_id']},{'$set':{'mentions_0':mentions,'mentions_1':{}}})
        collection.update({'_id':c['_id']},{'$unset':{'mentions_1':""}})

def prp_single_user(ucollection,pcollection,uid,iterate):
    user=ucollection.find_one({'_id':uid})
    if user==None:
        print 'Not found user %s'%uid
        return
    mentions=dict()
    for pid in user['products']:
        product=pcollection.find_one({'_id':pid})
        if product==None:
            #print 'Not found product %s'%pid
            continue
        for m,v in product['mentions_%d'%(iterate-1)].items():
            if m in mentions:
                mentions[m]+=v
            else:
                mentions[m]=v
    s=1.0*sum(mentions.values())
    for m in mentions:
        mentions[m]/=s
    max_v=72
    alpha=1.0*len(user['mentions'])/max_v
    F1=dict()
    for key in set(user['mentions_0'].keys()+mentions.keys()):
        try:
            f0=user['mentions_0'][key]
        except:
            f0=0.
        try:
            f1=mentions[key]
        except:
            f1=0.

        if f0==0 and f1==0:
            continue
        F1[key]=alpha*f0+(1-alpha)*f1
    ucollection.update({'_id':user['_id']},{'$set':{'mentions_%d'%iterate:F1}})

def prp_single_product(ucollection,pcollection,pid,iterate):
    product=pcollection.find_one({'_id':pid})
    if product==None:
        print 'Not found product %s'%pid
        return
    mentions=dict()
    for uid in product['users']:
        user=ucollection.find_one({'_id':uid})
        if user==None:
            #print 'Not found user %s'%uid
            continue
        for m,v in user['mentions_%d'%iterate].items():
            if m in mentions:
                mentions[m]+=v
            else:
                mentions[m]=v
    s=1.0*sum(mentions.values())
    for m in mentions:
        mentions[m]/=s
    max_v=418
    alpha=1.0*len(product['mentions'])/max_v
    F1=dict()
    for key in set(product['mentions_0'].keys()+mentions.keys()):
        try:
            f0=product['mentions_0'][key]
        except:
            f0=0.
        try:
            f1=mentions[key]
        except:
            f1=0.

        if f0==0 and f1==0:
            continue
        F1[key]=alpha*f0+(1-alpha)*f1
    pcollection.update({'_id':product['_id']},{'$set':{'mentions_%d'%iterate:F1}})

def get_id(collection,iterate):
    ids=[]
    for c in collection.find():
        if 'mentions_%d'%iterate in c:
            continue
        ids.append(c['_id'])
    return ids

def prp_user(u_collection,p_collection,iterate):
    print 'prp user'
    uids=get_id(u_collection,iterate)
    print len(uids)
    bar=progress_bar(len(uids))
    for index,uid in enumerate(uids):
        prp_single_user(u_collection,p_collection,uid,iterate)
        bar.draw(index+1)

def prp_product(u_collection,p_collection,iterate):
    print 'prp product'
    pids=get_id(p_collection,iterate)
    print len(pids)
    bar=progress_bar(len(pids))
    for index,pid in enumerate(pids):
        prp_single_product(u_collection,p_collection,pid,iterate)
        bar.draw(index+1)

def prp(iterate):
    print iterate
    u_collection=Connection().jd.train_users
    p_collection=Connection().jd.train_products
    u_t_collection=Connection().jd.test_users

    prp_user(u_collection,p_collection,iterate)
    prp_user(u_t_collection,p_collection,iterate)
    prp_product(u_collection,p_collection,iterate)
    print 'Done'


if __name__=='__main__':
    prp(1)
    prp(2)
    prp(3)
    #prp(4)
    print 'Done'

