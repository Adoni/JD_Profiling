import numpy
from small_utils.progress_bar import progress_bar
import datetime

class iterateTrainer:
    def __init__(self,_max_iter):
        self.max_iter=_max_iter

    def train(self,data):
        f_u=dict()
        f_v=dict()
        C_u=numpy.max(numpy.sum(data.f_u_init.values(),axis=1))
        C_v=numpy.max(numpy.sum(data.f_v_init.values(),axis=1))
        for u in data.U:
            f_u[u]=data.f_u_init[u]
        for v in data.V:
            f_v[v]=data.f_v_init[v]
        bar=progress_bar(self.max_iter)
        t1=datetime.datetime.now()
        for index in xrange(self.max_iter):
            for u in data.U:
                n_u=numpy.zeros((data.vector_size))
                for v in data.U[u]:
                    n_u+=f_v[v]
                alpha=numpy.sum(data.f_u_init[u])/C_u
                f_u[u]=alpha*data.f_u_init[u]+(1.-alpha)*n_u
            for v in data.V:
                n_v=numpy.zeros((data.vector_size))
                for u in data.V[v]:
                    n_v+=f_u[u]
                alpha=numpy.sum(data.f_v_init[v])/C_v
                f_v[v]=alpha*data.f_v_init[v]+(1.-alpha)*n_v
            t2=datetime.datetime.now()
            print 'Iter: %d, minutes: %d'%(index,(t2-t1).seconds/60)
            t1=t2
            #bar.draw(index+1)
        return f_u,f_v
