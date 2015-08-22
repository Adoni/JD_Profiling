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
        collection.update({'_id':c['_id']},{'$set':{'mentions_0':mentions}})

def prp_single_user(ucollection,pcollection,uid,iterate):
    user=ucollection.find_one({'_id':uid})
    if user==None:
        print 'Not found user %s'%uid
        return
    mentions=dict()
    for pid in user['products']:
        product=pcollection.find_one({'_id':pid})
        if product==None:
            print 'Not found product %s'%pid
            continue
        for m,v in product['mentions_%d'%(iterate-1)].items():
            if m in mentions:
                mentions[m]+=v
            else:
                mentions[m]=v
    s=1.0*sum(mentions.values())
    for m in mentions:
        mentions[m]/=s
    ucollection.update({'_id':user['_id']},{'$set':{'mentions_%d'%iterate:mentions}})

def prp_single_product(ucollection,pcollection,pid,iterate):
    product=pcollection.find_one({'_id':pid})
    if product==None:
        print 'Not found product %s'%pid
        return
    mentions=dict()
    for uid in product['users']:
        user=ucollection.find_one({'_id':uid})
        if user==None:
            print 'Not found product %s'%uid
            continue
        for m,v in user['mentions_%d'%iterate].items():
            if m in mentions:
                mentions[m]+=v
            else:
                mentions[m]=v
    s=1.0*sum(mentions.values())
    for m in mentions:
        mentions[m]/=s
    pcollection.update({'_id':product['_id']},{'$set':{'mentions_%d'%iterate:mentions}})

def prp_user(ucollection,pcollection,iterate):
    bar=progress_bar(u_collection.count())
    for index,user in enumerate(u_collection.find()):
        prp_single_user(u_collection,p_collection,user['_id'],iterate)
        bar.draw(index+1)

def prp_product(ucollection,pcollection,iterate):
    bar=progress_bar(u_collection.count())
    for index,user in enumerate(u_collection.find()):
        prp_single_user(u_collection,p_collection,user['_id'],iterate)

def prp(iterate):
    u_collection=Connection().jd.train_users
    p_collection=Connection().jd.train_products
    u_t_collection=Connection().jd.train_users

    prp_user(u_collection,p_collection,iterate)
    prp_user(u_t_collection,p_collection,iterate)
    prp_product(u_collection,p_collection,iterate)


if __name__=='__main__':
    #prp(1)
    print 'Done'

