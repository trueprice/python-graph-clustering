Graph Clustering in Python
==========================

This is a collection of Python scripts that implement various weighted and
unweighted graph clustering algorithms. The project is specifically geared
towards discovering protein complexes in protein-protein interaction networks,
although the code can really be applied to any graph. The methods implemented
here include weighted and unweighted versions of the following graph clustering
algorithms:

* Clique Percolation (k=3 and k=4)
* MCODE
* DPClus
* IPCA
* CoAch
* Graph Entropy Clustering

The code is free for academic use. If you find this project useful, please
consider citing
  
True Price, Francisco I Peña III, Young-Rae Cho. "Survey: Enhancing
protein complex prediction in PPI networks with GO similarity weighting."
Interdisciplinary Sciences: Computational Life Sciences, 2013.
[[pdf]](http://cs.unc.edu/~jtprice/papers/price_pena_cho_2013.pdf)


Requirements
============

[NumPy](http://www.numpy.org) and [SciPy](http://www.scipy.org).
[networkx](https://networkx.github.io/) is also required for the clique
percolation methods.


Usage
=====

All files have been tested to run in Python 2.7. Simply run

	python <script.py> <graph file>

where `<graph file>` contains a separate entry on each line defining an edge 
between two nodes in the graph, i.e.:

	<node 1> <node 2> [edge weight]

The edge weight entry is optional for the unweighted methods. Example datasets
for PPI networks (weighted with similarity metrics on Gene Ontology entries) are
provided in the "data" folder.

The output of the scripts is a collection of discovered graph clusters, one per
line. Some methods also print progress to stderr.

Finally, it should be stated that these algorithms run with no warranty, and not
all implementations are guaranteed to scale well for very large datasets (case
in point, the clique percolation implementations might take a bit of time to
run).

