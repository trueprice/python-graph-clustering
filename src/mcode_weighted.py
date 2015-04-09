# Author: True Price <jtprice@cs.unc.edu>

import sys
from collections import defaultdict

WEIGHT_THRESHOLD = 0.2

##
WEIGHT_THRESHOLD = 1 - WEIGHT_THRESHOLD

# dictionary type that returns zero for missing values
# used here in 'edges' dictionary
class zerodict(dict):
  def __missing__(self, k):
    return 0

def mcode(filename):
  graph = defaultdict(set) # node id => neighboring node ids
  edges = defaultdict(zerodict)

  # read in graph
  print >> sys.stderr, 'loading graph...'
  with open(filename, 'r') as f:
    for line in f:
      a,b,w = line.split()[:3]
      w = float(w)
      graph[a].add(b)
      graph[b].add(a)
      edges[a][b], edges[b][a] = w, w
  
  # Stage 1: Vertex Weighting
  print >> sys.stderr, 'vertex weighting...'
  weights = dict(
    (v,sum(edges[v].itervalues()) / len(edges[v])**2) for v in graph)
  for i,v in enumerate(graph):
    if i > 0 and i % 1000 == 0:
      print >> sys.stderr, i, '/', len(graph)

    neighborhood = set((v,)) | graph[v]
    # if node has only one neighbor, we know everything we need to know
    if len(neighborhood) <= 2: continue

    # valid k-core with the highest weight
    k = 2 # already covered k = 1
    while True:
      invalid_nodes = True
      while invalid_nodes and neighborhood:
        invalid_nodes = set(
          n for n in neighborhood if len(graph[n] & neighborhood) < k)
        neighborhood -= invalid_nodes
      if not neighborhood: break

      # vertex weight = k-core number * density of k-core
      weights[v] = max(weights[v],
        k * sum(edges[v][n] for n in neighborhood) / len(neighborhood)**2)
      k += 1

  # Stage 2: Molecular Complex Prediction
  print >> sys.stderr, 'molecular complex prediction...'
  unvisited = set(graph)
  num_clusters = 0
  for seed in sorted(weights, key=weights.get, reverse=True):
    if seed not in unvisited: continue

    cluster, frontier = set((seed,)), set((seed,))
    w = weights[seed] * WEIGHT_THRESHOLD
    while frontier:
      cluster.update(frontier)
      unvisited -= frontier
      frontier = set(
        n for n in set.union(*(graph[n] for n in frontier)) & unvisited
        if weights[n] > w)

    # haircut: only keep 2-core complexes
    invalid_nodes = True
    while invalid_nodes and cluster:
      invalid_nodes = set(n for n in cluster if len(graph[n] & cluster) < 2)
      cluster -= invalid_nodes

    if cluster:
      print ' '.join(cluster)
      num_clusters += 1
      print >> sys.stderr, num_clusters, len(cluster), seed
      if not unvisited: break # quit if all nodes visited

if __name__ == '__main__':
  mcode(sys.argv[1])
 
