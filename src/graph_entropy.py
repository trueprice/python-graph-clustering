# Author: True Price <jtprice@cs.unc.edu>

import sys
from math import log
from collections import defaultdict

def graph_entropy(filename):
  data = defaultdict(set) # node id => neighboring node ids

  # read in graph
  with open(filename, 'r') as f:
    for line in f:
      a,b = line.split()[:2]
      data[a].add(b)
      data[b].add(a)

  # define entropy of a vertex in terms of an associated cluster
  def entropy(c,v):
    neighbors = data[v]
    inner = len(c & neighbors) / float(len(neighbors))# p(inner links)
    return 0 if inner == 0 or inner == 1 else \
        -inner*log(inner,2) -(1-inner)*log(1-inner,2)

  candidates = set(data)
  clusters = []
  while candidates:
    print >> sys.stderr, len(candidates)
    v = candidates.pop() # select a random vertex
    cluster = data[v].copy() # add neighbors to cluster
    cluster.add(v)
    entropies = dict((x,entropy(cluster, x)) for x in data)

    # step 2: try removing neighbors to minimize entropy
    for n in list(cluster): 
      if n == v: continue # don't remove our seed, obviously
      new_c = cluster.copy()
      new_c.remove(n)
      new_e = dict((x,entropy(new_c,x)) for x in data[n])
      # if removing the neighbor decreases new entropy (for the node and
      # all its neighbors), then do so
      if sum(new_e.itervalues()) < sum(entropies[x] for x in data[n]):
        cluster = new_c
        entropies.update(new_e)

    # boundary candidates
    c = reduce(lambda a,b: a | b, (data[x] for x in cluster)) - cluster
    while c:
      n = c.pop()
      new_c = cluster.copy()
      new_c.add(n)
      new_e = dict((x,entropy(new_c,x)) for x in data[n])
      if sum(new_e.itervalues()) < sum(entropies[x] for x in data[n]):
        cluster = new_c
        entropies.update(new_e)
        c &= data[n] - cluster

    # remove the elements of the cluster from our candidate set; add cluster
    candidates -= cluster
    
    if len(cluster ) > 1:
      print ' '.join(c for c in cluster)

if __name__ == '__main__':
  graph_entropy(sys.argv[1])

