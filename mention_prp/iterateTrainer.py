from pymongo import Connection
from small_utils.progress_bar import progress_bar

def update(collection):
    for c in collection.find():
        collection.update({'_id':c['_id']},{'$set':{'mentions_0':c['mentions']}})

def prp_user(ucollection,pcollection,uid,iterate):
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
    ucollection.update({'_id':user['_id']},{'$set':{'mentions_%d'%iterate:mentions}})

def prp_product(ucollection,pcollection,pid,iterate):
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
    pcollection.update({'_id':product['_id']},{'$set':{'mentions_%d'%iterate:mentions}})

def prp(iterate):
    u_collection=Connection().jd.train_users
    p_collection=Connection().jd.train_products
    bar=progress_bar(u_collection.count())
    for index,user in enumerate(u_collection.find()):
        if 'mention_%d'%iterate in user:
            continue
        prp_user(u_collection,p_collection,user['_id'],iterate)
        bar.draw(index+1)
    bar=progress_bar(p_collection.count())
    for index,product in enumerate(p_collection.find()):
        if 'mention_%d'%iterate in product:
            continue
        prp_product(u_collection,p_collection,user['_id'],iterate)
        bar.draw(index+1)

if __name__=='__main__':
    prp(1)
    print 'Done'
