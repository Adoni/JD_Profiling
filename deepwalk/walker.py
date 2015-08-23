import random
import numpy
class Graph:
    def __init__(self, file_name):
        self.graph=dict()
        graph_file=open(file_name)
        for line in graph_file:
            line=line[:-1].split(' ')
            id1=line[0]
            id2=line[1]
            weight=1. if len(line)==2 else float(line[2])
            try:
                self.graph[id1][id2]=weight
            except Exception as e:
                self.graph[id1]={id2:weight}
        self.nodes_weight=dict()
        for id1 in self.graph:
            self.nodes_weight[id1]=len(self.graph[id1])

    def __getitem__(self, nid):
        if nid not in self.graph:
            return None
        return self.graph[nid]

    def index_of(self, node_name):
        return self.indexes[node_name]

def weighted_random_select(nodes):
    if nodes=={}:
        return None
    rnd = random.random()*sum(nodes.values())
    for nid, w in nodes.items():
        rnd -= w
        if rnd <= 0:
            return nid

def get_a_random_path_from_graph(graph,length):
    from small_utils.progress_bar import progress_bar
    path=[]
    nid=weighted_random_select(graph.nodes_weight)
    path.append(nid)
    bar=progress_bar(length-1)

    for i in xrange(length-1):
        node=graph[nid]
        while node is None:
            nid=weighted_random_select(graph.nodes_weight)
            node=graph[nid]
        nid=weighted_random_select(node)
        path.append(nid)
        bar.draw(i)
    return path

