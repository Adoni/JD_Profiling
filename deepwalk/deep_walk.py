from walker import *

RAW_DATA_DIR='/mnt/data1/adoni/data/'

def deep_walk(total_nodes_count):
    import os
    graph=Graph(RAW_DATA_DIR+'graph.data')
    path=get_a_random_path_from_graph(graph, total_nodes_count)
    path_file_name=RAW_DATA_DIR+'deep_walk_path.data'
    fout=open(path_file_name+'.data','w')
    fout.write(' '.join(path))
    fout.write('\n')
    fout.close()

    print '\nEmbedding...'
    embedding_file_name=RAW_DATA_DIR+'embedding_with_deepwalk.data'
    command='/home/adoni/word2vec/word2vec -train %s.data -output %s.data -cbow 0 -size 100 -window 5 -negative 0 -hs 1 -sample 1e-3 \
    -threads 20 -binary 0'%(path_file_name, embedding_file_name)
    print command
    os.system(command)
    print '\nEmbedding Done'

if __name__=='__main__':
    #for ratio in numpy.arange(start=0.00,stop=0.85,step=0.10):
    #    deep_walk(10000000,ratio,'gender','old')
    deep_walk(1000000)
    #output_matrix('user_embedding_with_LINE_from_record_knn','user_embedding_with_LINE_from_record_knn')
