from settings import RAW_DATA_DIR
from prModel import prModel
from prData import prData

def save_vec(fname,vec):
    f=open(fname,'w')
    for v in vec:
        f.write('%s %s\n'%(v,' '.join(map(lambda d:str(d),vec[v]))))
if __name__=='__main__':
    opts={
            'max_iter':2,
            }
    pr=prModel(opts)
    data=prData(RAW_DATA_DIR+'graph.data',RAW_DATA_DIR+'users_init_vec.data',RAW_DATA_DIR+'users_init_vec.data')
    pr.train(data)
    save_vec(RAW_DATA_DIR+'u_vec.data',pr.f_u)
    save_vec(RAW_DATA_DIR+'v_vec.data',pr.f_v)
