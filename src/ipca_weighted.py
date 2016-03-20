# True Price
import sys
from itertools import combinations
from collections import defaultdict

T_IN = 0.5
# SP = 2 # hard-coded, mostly for efficiency

def ipca(filename):
	data = defaultdict(set) # node id => neighboring node ids
	global_edges, degrees = defaultdict(dict), defaultdict(float)

	# read in graph
	with open(filename, 'r') as f:
		for line in f:
			a,b,w = line.split()[:3]
			w = float(w)
			data[a].add(b)
			data[b].add(a)
			global_edges[a][b], global_edges[b][a] = w, w
			degrees[a] += w
			degrees[b] += w

	weights = defaultdict(int)
	for a,b in combinations(data, 2):
		if b not in data[a]: continue	
		shared = len(data[a] & data[b])
		weights[a] += shared
		weights[b] += shared

	unvisited = set(data)
	num_clusters = 0

	# DIFFERENT: weighted degrees
	seed_nodes = sorted(data,key=lambda k: (weights[k],degrees[k]),reverse=True)

	for seed in seed_nodes: # get highest weight/degree node
		if seed not in unvisited: continue

		cluster = set((seed,))

		while True:
			# DIFFERENT: rank neighbors by the sum of global edge weights
			# between the node and cluster nodes
			frontier = sorted((sum(global_edges[p][c] for c in data[p] & cluster),p)
				for p in set.union(*((data[n] - cluster) for n in cluster)))

			# do this until IN_vK < T_IN, SP <= 2 is met, or no frontier nodes left
			found = False
			while frontier and not found:
				m_vk,p = frontier.pop()
				if m_vk < T_IN * len(cluster): break
				c_2neighbors = data[p] & cluster
				c_2neighbors.update(*(data[c] & cluster for c in c_2neighbors))
				if cluster == c_2neighbors:
				 	found = True
				 	break

			if not found: break
				
			cluster.add(p) # otherwise, add the node to the cluster

		unvisited -= cluster
		if len(cluster) > 1:
			print ' '.join(cluster)

			num_clusters += 1
			print >> sys.stderr, num_clusters, len(cluster), len(unvisited)

		if not unvisited: break

if __name__ == '__main__':
	import sys

	ipca(sys.argv[1])
 
