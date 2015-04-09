# Author: True Price <jtprice@cs.unc.edu>

# A core-attachment based method to detect protein complexes in PPI networks
# Wu, Li, Kwoh, Ng (2009)
# http://www.biomedcentral.com/1471-2105/10/169

import sys
from collections import defaultdict
from itertools import combinations

DENSITY_THRESHOLD = 0.7
AFFINITY_THRESHOLD = 0.225
CLOSENESS_THRESHOLD = 0.5

# id: protein with which another protein interacts
# w: the weight f the interaction
class Interaction:
  def __init__(self, id, w):
    self.id = id
    self.w = w
    self.__hash__ = self.id.__hash__
    self.__eq__ = lambda other: self.id == other.id

# float comparison inpython can be icky :(
# fgeq returns whether a is not less than b to some precision
fgeq = lambda a,b: (b - a) <= 1e-12

# return the weighted degree of a node in a graph
deg = lambda n: sum(x.w for x in n)

# return average degree and density for a graph
average_deg = lambda g: sum(deg(n) for n in g.itervalues()) / len(g)

# return core nodes, given a graph and its average degree
get_core_nodes = lambda g,a: set(v for v,n in g.iteritems() if fgeq(deg(n), a))

# return NA score
NA_score = lambda a,b: float(len(a & b)**2) / (len(a) * len(b))

def core_removal(graph):
  if len(graph) == 1: # need at least two nodes in the graph...
    return [graph]

  avg_deg = average_deg(graph)
  d = avg_deg / (len(graph)-1)

  if d >= DENSITY_THRESHOLD:
    return [graph]
  else:
    # find and remove core nodes; create connected subcomponents
    core_nodes = get_core_nodes(graph, avg_deg)
    result = []
    subgraphs = []
    for v,n in graph.iteritems():
      if v in core_nodes: continue
      n = n - core_nodes # note that we're reassigning n
      for s in subgraphs:
        if not n.isdisjoint(s):
          s |= n
          break
      else:
        subgraphs.append(n | set([v]))
    # connected subcomponent joining
    i = 0
    while i < len(subgraphs) - 1:
      j = i + 1
      while j < len(subgraphs):
        if not subgraphs[i].isdisjoint(subgraphs[j]):
          subgraphs[i] |= subgraphs[j]
          subgraphs.pop(j)
        else:
          j += 1
      i += 1
    # recursive core removal
    for s in subgraphs:
      tresults = core_removal(dict((v,graph[v] & s) for v in s))
      for tc in tresults:
        nodes = set()
        for v,n in tc.iteritems():
          nodes.add(v)
          n |= graph[v] & core_nodes
        for c in core_nodes:
          tc[c] = graph[c] & (nodes | core_nodes)
      result += tresults
    return result

def coach(filename):
  print >> sys.stderr, 'loading graph...'
  data = defaultdict(set)
  with open(filename, 'r') as f:
    for line in f:
      a,b,w = line.split() # protein, protein, weight
      w = float(w)
      a,b = Interaction(a,w), Interaction(b,w)
      data[a].add(b)
      data[b].add(a)

  # step 1: find preliminary cores
  SC = [] # currently-detected preliminary cores
  count = 0
  print >> sys.stderr, 'finding preliminary cores...'
  for i,(vertex,neighbors) in enumerate(data.iteritems()):
    if i > 0 and i % 1000 == 0:
      print >> sys.stderr, i, '/', len(data)
    # build neighborhood graph
    vertices = set([vertex]) | neighbors
    size1_neighbors = set()
    graph = { }
    for v in vertices:
      n = data[v] & vertices
      if len(n) > 1: # ignore size-1 vertices
        graph[v] = n
      else:
        size1_neighbors.add(v)
    if len(graph) < 2: # not enough connections in this graph
      continue
    graph[vertex] -= size1_neighbors

    # get core graph
    core_nodes = get_core_nodes(graph, average_deg(graph))
    vertices = set(graph.iterkeys())
    for v in vertices - core_nodes:
      del graph[v]
    for n in graph.itervalues():
      n &= core_nodes
    if len(graph) < 2: # not enough connections in this graph
      continue
    graph_nodes = set(graph)

    # inner loop
    for sg in core_removal(graph):
      sg = sg.copy()
      while len(sg) >= 2:
        weights = [(deg(n),w) for w,n in sg.iteritems()]
        # if density threshold met, stop; else, remove min degree node
        if sum(w[0] for w in weights)/len(sg)/(len(sg)-1) < DENSITY_THRESHOLD:
          break
        w = min(weights)[1]
        del sg[w]
        for n in sg.itervalues():
          n.discard(w)
      if len(sg) < 2: continue # the density of this graph is too weak

      sg_nodes = set(sg)
      while graph_nodes - sg_nodes:
        w = max(graph_nodes - sg_nodes,
            key=lambda v: sum(n.w for n in graph[v] & sg_nodes))
        new_sg = sg.copy()
        for v,n in new_sg.iteritems():
          if w in graph[v]:
            n.add(w)
        new_sg[w] = graph[w] & sg_nodes
        d = average_deg(new_sg) / (len(new_sg)-1)
        if d < DENSITY_THRESHOLD: break
        sg = new_sg
        sg_nodes.add(w)

      # redundancy filtering
      max_sim = -1
      for i in xrange(len(SC)):
        sim = NA_score(set(SC[i]), sg_nodes)
        if sim > max_sim:
          max_sim = sim
          index = i
      if max_sim < AFFINITY_THRESHOLD:
        SC.append(sg)
      elif len(SC[index]) > 1:
        d_i = average_deg(SC[index]) / (len(SC[index])-1)
        if d * len(sg) > d_i * len(SC[index]):
          SC[index] = sg

  # step 2: adding peripheral proteins
  print >> sys.stderr, 'adding peripheral proteins...'
  clusters = set()
  for core in SC:
    nodes = frozenset(core)
    neighbors = reduce(lambda x,y: x|y, (data[v] for v in nodes)) - nodes
    neighbors -= set(v for v in neighbors
      if deg(data[v] & nodes) / len(nodes) <= CLOSENESS_THRESHOLD)
    clusters.add(nodes | neighbors)

  return clusters

if __name__ == '__main__':
  for c in coach(sys.argv[1]):
    print ' '.join(p.id for p in c)

