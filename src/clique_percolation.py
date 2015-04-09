# Author: True Price <jtprice@cs.unc.edu>

# NOTE: this script is currently hard-coded to run for k=3 (see line 88); it can
#       be easily modified to accept a specific k (or range of k's) on the
#       command line, though.

import networkx as nx
import sys
from itertools import combinations
from collections import defaultdict, deque
from threading import Thread, Semaphore

NUM_THREADS = 2

class TreeNode:
  static_id = 0

  def __init__(self, data, left=None, right=None):
    self.id = TreeNode.static_id
    TreeNode.static_id += 1
    self.data = data
    self.left = left
    self.right = right
    self.is_leaf = not left and not right
    self.__hash__ = lambda: self.id
    self.__eq__ = lambda self,other: self.id == other.id

def get_percolated_cliques(filename):
  # read in graph
  G = nx.read_edgelist(filename, nodetype=str, data=False)
  clique_sizes = defaultdict(list) # size => cliques of that size
  # find maximal cliques
  for c in nx.find_cliques(G): 
    if len(c) > 2:
      clique_sizes[len(c)].append(TreeNode(frozenset(c)))
  clique_sizes = sorted(clique_sizes.iteritems()) # [(size,cliques)...]

  # build our binary tree
  size_roots = dict()
  for size,cliques in clique_sizes:
    cliques = deque(cliques)
    while len(cliques) > 1:
      for _ in xrange(0, len(cliques), 2):
        a,b = cliques.popleft(), cliques.popleft()
        cliques.append(TreeNode(a.data | b.data, a, b))
    size_roots[size] = cliques.pop()
  
  size_roots = sorted(size_roots.iteritems()) # [(size,root),...]

  # k = k - 1, technically
  def percolation_thread(components, k, sem):
    frontier = set()
    visited = set()

    def get_neighbor_nodes(clique, node, component):
      if node in visited: return True

      if len(clique.data & node.data) >= k:
        if node.is_leaf:
          frontier.add(node)
          component |= node.data
          visited.add(node)
          return True
        elif (get_neighbor_nodes(clique, node.left, component) and
              get_neighbor_nodes(clique, node.right, component)):
          visited.add(node)
          return True

      return False

    for i,(size,cliques) in enumerate(clique_sizes):
      if size <= k: continue
      for clique in cliques:
        if clique not in visited: # clique not already touched for this k?
          component = set(clique.data)
          frontier.add(clique)

          # find neighbor cliques sharing k-1 nodes and add them to the frontier
          while frontier:
            current = frontier.pop()
            for size,root in size_roots[i:]:
              get_neighbor_nodes(current, root, component)

          components.add(frozenset(component))

    sem.release()
  
  # run clique percolation on multiple threads
  krange = xrange(3, 4)#max(clique_sizes.iterkeys()) - 1)
  components = dict((k,set()) for k in krange) # k => components

  sem = Semaphore(NUM_THREADS)
  for k in krange:
    sem.acquire()
    print >> sys.stderr, 'Running K =', k
    Thread(target=percolation_thread, args=(components[k],k-1,sem)).start()
  for i in xrange(NUM_THREADS):
    sem.acquire() # wait until all threads have finished

  # return the components
  return reduce(lambda x,y: x|y, components.itervalues())

if __name__ == '__main__':
  for c in get_percolated_cliques(sys.argv[1]):
    print ' '.join(str(x) for x in c)

