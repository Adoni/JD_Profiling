import numpy
class prData:
    def __init__(self,graph_file_name,init_u_file,init_v_file):
        self.U,self.V=self._load_graph(graph_file_name)
        self.f_u_init=self._load_init_vector(init_u_file)
        self.f_v_init=self._load_init_vector(init_v_file)
        for u in self.U:
            if u not in self.f_u_init:
                self.f_u_init[u]=numpy.zeros((self.vector_size))
        for v in self.V:
            if v not in self.f_v_init:
                self.f_v_init[v]=numpy.zeros((self.vector_size))

    def _load_graph(self,graph_file_name):
        print 'Loading graph ...'
        try:
            fp=open(graph_file_name)
        except:
            raise Exception('Fail to open file')
        U=dict()
        V=dict()
        for line in fp:
            line=line[:-1].split(' ')
            u,v=line[0],line[1]
            if u not in U:
                U[u]=[]
            if v not in V:
                V[v]=[]
            U[u].append(v)
            V[v].append(u)
        print 'Load graph Done'
        return U,V

    def _load_init_vector(self,init_file):
        print 'Loading vector from %s ...'%init_file
        try:
            fp=open(init_file)
        except:
            raise Exception('Fail to open file')
        vectors=dict()
        line=fp.readline()[:-1].split(' ')
        count,vector_size=int(line[0]),int(line[1])
        self.vector_size=vector_size
        for line in fp:
            line=line[:-1].split(' ')
            id=line[0]
            vector=numpy.array(map(lambda d:float(d),line[1:]))
            vectors[id]=vector
        print 'Load vector Done'
        return vectors

if __name__=='__main__':
    from settings import RAW_DATA_DIR
    data=prData(RAW_DATA_DIR+'graph.data',RAW_DATA_DIR+'users_init_vec.data',RAW_DATA_DIR+'users_init_vec.data')
