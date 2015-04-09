# True Price
import sys
from collections import defaultdict
from itertools import combinations
from scipy.special import cbrt

# specialized gmean for three values
gmean = lambda a, b, c: cbrt(a * b * c)

def weighted_clique_percolation(filename):
  # read protein-protein pairs
  data = defaultdict(set)
  weights = defaultdict(dict)
  three_cliques = defaultdict(set)
  connected_cliques = defaultdict(set) # pair of nodes => 3-cliques having them
  with open(filename, 'r') as f:
    for line in f:
      a,b,w = line.split()[:3]
      x,y = data[a], data[b]
      w = float(w)
      ab = frozenset((a,b))
      for c in x & y:
        clique = frozenset((a,b,c))
        connected_cliques[ab].add(clique)
        connected_cliques[frozenset((a,c))].add(clique)
        connected_cliques[frozenset((b,c))].add(clique)
        # group cliques by their intensities
        three_cliques[gmean(weights[a][c], weights[b][c], w)].add(clique)
      x.add(b)
      y.add(a)
      weights[a][b] = w
      weights[b][a] = w
  # sort cliques by intensity (three_cliques is now a list)
  three_cliques = sorted(three_cliques.iteritems(), reverse=True)

  if len(three_cliques) == 0:
    raise Exception('No 3-cliques found.')

  clique_graph = defaultdict(set)
  for cliques in connected_cliques.itervalues():
    for a,b in combinations(cliques, 2):
      clique_graph[a].add(b)
      clique_graph[b].add(a)
  del connected_cliques

  good_cliques = set() # our subset of cliques to examine
  i = 0
  while i < len(three_cliques):
    communities = []
    good_cliques |= three_cliques[i][1]
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
        print >> sys.stderr, i, three_cliques[i][0],
        print >> sys.stderr, float(len(communities[0])) / len(communities[1])
      if len(communities[0]) / len(communities[1]) >= 2:
        return communities

    i += 1

  return communities

if __name__ == '__main__':
  for c in weighted_clique_percolation(sys.argv[1]):
    print ' '.join(c)

