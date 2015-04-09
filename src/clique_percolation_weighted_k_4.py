# True Price
import sys
from collections import defaultdict
from itertools import combinations
from math import sqrt
import time

# specialized gmean for six values
gmean = lambda a, b, c, d, e, f: sqrt(sqrt(sqrt(a * b * c * d * e * f)))

def weighted_clique_percolation(filename):
  start = time.time()
  print >> sys.stderr, 'Finding 4-cliques...'
  # read protein-protein pairs
  data = defaultdict(set)
  weights = defaultdict(dict)
  four_cliques = defaultdict(set)
  connected_cliques = defaultdict(set) # pair of nodes => 3-cliques having them
  with open(filename, 'r') as f:
    for line in f:
      a,b,w = line.split()[:3]
      x,y = data[a], data[b]
      w = float(w)
      for c,d in combinations(x & y, 2):
        if d not in data[c]: continue
        clique = frozenset((a,b,c,d))
        connected_cliques[frozenset((a,b,c))].add(clique)
        connected_cliques[frozenset((a,b,d))].add(clique)
        connected_cliques[frozenset((a,c,d))].add(clique)
        connected_cliques[frozenset((b,c,d))].add(clique)
        # group cliques by their intensities
        four_cliques[gmean(weights[a][c], weights[a][d], weights[b][c],
          weights[b][d], weights[c][d], w)].add(clique)
      x.add(b)
      y.add(a)
      weights[a][b] = w
      weights[b][a] = w
  del data
  del weights

  if len(four_cliques) == 0:
    raise Exception('No 4-cliques found. (%f sec)' % (time.time()-start))

  print >> sys.stderr, 'Building clique graph... (%f sec)' % (time.time()-start)

  # sort cliques by intensity (four_cliques is now a list)
  four_cliques = sorted(four_cliques.iteritems())

  clique_graph = defaultdict(set)
  connected_cliques = connected_cliques.values()
  while connected_cliques:
    for a,b in combinations(connected_cliques.pop(), 2):
      clique_graph[a].add(b)
      clique_graph[b].add(a)
  del connected_cliques

  print >> sys.stderr, 'Running algorithm... (%f sec)' % (time.time()-start)

  good_cliques = set() # our subset of cliques to examine
  i = 0
  while four_cliques:
    communities = []
    good_cliques |= four_cliques.pop()[1]
    frontier, unvisited = set(), good_cliques.copy()
    while unvisited:
      component = set()
      frontier.add(unvisited.pop())
      
      while frontier:
        component.update(*frontier)
        unvisited -= frontier
        frontier = unvisited & set.union(*(clique_graph[x] for x in frontier))
      
      communities.append(component)

    if len(communities) > 1:
      communities.sort(key=len, reverse=True)
      if i % 100 == 0:
        print >> sys.stderr, i, float(len(communities[0])) / len(communities[1])
      if len(communities[0]) / len(communities[1]) >= 2:
        print >> sys.stderr, 'Done. (%f sec)' % (time.time()-start)
        return communities

    i += 1

  print >> sys.stderr, 'Done. (%f sec)' % (time.time()-start)
  return communities

if __name__ == '__main__':
  for c in weighted_clique_percolation(sys.argv[1]):
    print ' '.join(c)

