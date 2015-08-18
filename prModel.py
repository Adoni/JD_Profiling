from prData import prData
from iterateTrainer import iterateTrainer
from settings import RAW_DATA_DIR
class prModel:
    def __init__(self,opts):
        self.trainer=iterateTrainer(opts['max_iter'])

    def train(self,data):
        self.f_u,self.f_v=self.trainer.train(data)

if __name__=='__main__':
    pr=prModel()
    data=prData(RAW_DATA_DIR+'graph.data',RAW_DATA_DIR+'users_init_vec.data',RAW_DATA_DIR+'users_init_vec.data')
    f_u,f_v=pr.train(data)
