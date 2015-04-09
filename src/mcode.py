# Author: True Price <jtprice@cs.unc.edu>

import sys
from collections import defaultdict

WEIGHT_THRESHOLD = 0.2

##
WEIGHT_THRESHOLD = 1 - WEIGHT_THRESHOLD

def mcode(filename):
  edges = defaultdict(set) # node id => neighboring node ids

  # read in graph
  with open(filename, 'r') as f:
    for line in f:
      a,b = line.split()[:2]
      edges[a].add(b)
      edges[b].add(a)
  print >> sys.stderr, 'graph loaded; %i nodes' % (len(edges),)
  
  # Stage 1: Vertex Weighting
  print >> sys.stderr, 'vertex weighting...'
  weights = dict((v,1.) for v in edges)
  for i,v in enumerate(edges):
    if i % 1000 == 0: print >> sys.stderr, i
    neighborhood = set((v,)) | edges[v]
    # if node has only one neighbor, we know everything we need to know
    if len(neighborhood) <= 2: continue

    # see if larger k-cores exist
    k = 1 # highest valid k-core
    while neighborhood:
      k_core = neighborhood.copy()
      invalid_nodes = True
      while invalid_nodes and neighborhood:
        invalid_nodes = set(
          n for n in neighborhood if len(edges[n] & neighborhood) <= k)
        neighborhood -= invalid_nodes
      k += 1 # on exit, k will be one greater than we want
    # vertex weight = k-core number * density of k-core
    weights[v] = (k-1) * (sum(len(edges[n] & k_core) for n in k_core) / 
      (2. * len(k_core)**2))

  # Stage 2: Molecular Complex Prediction
  print >> sys.stderr, 'molecular complex prediction'
  unvisited = set(edges)
  num_clusters = 0
  for seed in sorted(weights, key=weights.get, reverse=True):
    if seed not in unvisited: continue

    cluster, frontier = set((seed,)), set((seed,))
    w = weights[seed] * WEIGHT_THRESHOLD
    while frontier:
      cluster.update(frontier)
      unvisited -= frontier
      frontier = set(
        n for n in set.union(*(edges[n] for n in frontier)) & unvisited
        if weights[n] > w)

    # haircut: only keep 2-core complexes
    invalid_nodes = True
    while invalid_nodes and cluster:
      invalid_nodes = set(n for n in cluster if len(edges[n] & cluster) < 2)
      cluster -= invalid_nodes

    if cluster:
      # fluff never really seems to improve anything...
      #cluster.update(
      # n for n in set.union(*(edges[c] for c in cluster)) & unvisited
      # if densities[n] > FLUFF_THRESHOLD)

      print ' '.join(cluster)
      num_clusters += 1
      print >> sys.stderr, num_clusters, len(cluster), seed

if __name__ == '__main__':
  mcode(sys.argv[1])
 
