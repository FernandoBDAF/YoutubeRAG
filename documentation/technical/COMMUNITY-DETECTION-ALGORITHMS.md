Community Detection Algorithms and Their Pros/Cons

Community detection algorithms identify clusters (communities) of nodes in a graph that are more densely connected internally than with the rest of the graph
analyticsvidhya.com
analyticsvidhya.com
. Below is a review of common algorithms, especially those supporting hierarchical community detection (multi-level clustering), along with their advantages and disadvantages.

Girvan–Newman (Edge Betweenness) Algorithm

The Girvan–Newman algorithm is a classic divisive hierarchical method. It repeatedly removes the edge with the highest betweenness centrality, causing the network to split into communities
memgraph.com
memgraph.com
. As critical inter-community edges are removed, tightly-knit groups of nodes become isolated as separate communities. This process naturally produces a dendrogram (hierarchical clustering) ranging from one whole network down to individual nodes.

Pros: Girvan–Newman provides a full hierarchy of communities and often yields meaningful splits for small networks. By focusing on edge betweenness (edges that frequently lie on shortest paths between nodes), it targets the “bridges” between communities, producing intuitive divisions
memgraph.com
. It can detect community structure without prior parameters and is useful for detailed analysis on modest-sized graphs. The hierarchy allows you to choose communities at any level (e.g. cut the dendrogram for a desired number of clusters or highest modularity).

Cons: This algorithm is computationally expensive, scaling poorly to large graphs
hypermode.com
. Recalculating betweenness after each removal leads to rapidly increasing costs as the graph splits (it’s often impractical beyond a few thousand nodes). Thus, Girvan–Newman is generally limited to small networks or demonstration purposes
hypermode.com
. It may also tend to break off many single-node communities in later stages if the graph has loosely connected nodes
atlantis-press.com
. In summary, its exhaustive nature yields a rich hierarchy but at the cost of speed and scalability.

Louvain Algorithm (Modularity Optimization)

The Louvain algorithm is a popular greedy modularity optimization method that works in a hierarchical agglomerative fashion
hypermode.com
. It attempts to maximize modularity, a measure of dense intra-community edges versus inter-community edges
analyticsvidhya.com
. Louvain first assigns each node to its own community and then repeatedly merges communities to increase modularity
hypermode.com
. It has two alternating phases: (1) nodes move between communities to improve modularity locally, and (2) communities are aggregated into super-nodes to create a smaller graph, then the process repeats
en.wikipedia.org
en.wikipedia.org
. This yields a final partition and can implicitly produce multiple levels of communities (from fine to coarse) as it merges nodes into communities and communities into larger communities.

Pros: Louvain is fast and scales well to large networks
hypermode.com
. It was found to be one of the fastest and best-performing algorithms in comparative studies
nature.com
. It automatically determines the number of communities and usually yields high-modularity partitions, which often correspond to meaningful clusters. Its hierarchical merging approach allows analysis at different granularities (you can examine the coarse communities at higher levels or the final fine-grained communities)
hypermode.com
. Louvain’s efficiency and ability to handle big graphs (millions of nodes/edges) make it a go-to choice for many applications
hypermode.com
.

Cons: Louvain can sometimes get stuck in local optima and has a known issue with the resolution limit – it may fail to separate small communities in very large graphs, merging them into larger communities
nature.com
nature.com
. In some cases, it can even produce poorly connected or disconnected communities due to the greedy merges
nature.com
. (Researchers observed that Louvain may output communities that are internally not well-connected, which Leiden algorithm aims to fix.) Additionally, Louvain’s results can be somewhat non-deterministic – the outcome might vary slightly depending on the order of node updates or random seed. Overall, while very robust, it might merge or split communities suboptimally if the graph’s structure or size triggers the resolution limit or if run iteratively without refinement
nature.com
.

Leiden Algorithm (Improved Louvain)

The Leiden algorithm is an improved version of Louvain that addresses some of Louvain’s pitfalls
en.wikipedia.org
nature.com
. Like Louvain, Leiden optimizes modularity (or a similar quality function) via node moves and community aggregation, but it adds an extra refinement phase to ensure communities are well-connected internally
en.wikipedia.org
en.wikipedia.org
. After the initial greedy clustering, Leiden splits any community that is found to be disconnected or internally sparse, then continues the iteration. This guarantees that every final community is connected and improves the quality of the partition. Leiden also randomizes the order of node movements in a smarter way to escape local optima more effectively.

Pros: Leiden produces better-quality communities and fixes the problem of disconnected communities present in Louvain
nature.com
. It has theoretical guarantees that each community is internally contiguous (no arbitrary mergers). In practice, Leiden often achieves higher modularity (or can optimize alternative quality metrics) and finds finer-grained structure that Louvain might miss, mitigating the resolution limit to some extent
en.wikipedia.org
nature.com
. It’s also typically faster than Louvain due to more efficient node update rules and fewer iterations needed to converge
nature.com
. For these reasons, Leiden is increasingly favored for community detection on large networks. It retains the hierarchical nature of Louvain – producing multiple levels that can be examined – with improved outcomes.

Cons: There are relatively few disadvantages; Leiden essentially dominates Louvain in quality and speed on most tests
nature.com
. One consideration is that Leiden is newer (introduced in 2019), so support in some libraries came later – but it’s now available in many graph toolkits (e.g., in NetworkX 3.5+ as leiden_communities). Implementation is a bit more complex due to the refinement step, but as a user you mostly see it as a better “drop-in replacement” for Louvain. In terms of behavior, Leiden (like Louvain) can still be sensitive to a resolution parameter if you use one – higher resolution finds more (smaller) communities, lower finds fewer (larger) communities
nature.com
. Tuning that may be necessary if you want a particular granularity. Overall, Leiden’s only “con” might be that it’s slightly more memory-intensive during refinement, but that’s usually negligible. (In rare cases, if improperly used on an extremely sparse or oddly structured graph, any modularity-based method could give trivial communities – but generally Leiden should outperform Louvain on all graph types.)

Hierarchical use: Leiden (and Louvain) can be applied recursively to build a multi-level community hierarchy. For example, the GraphRAG pipeline uses “Hierarchical Leiden” by repeatedly clustering the graph into communities, then clustering those communities into higher-level groups, until a certain small community size is reached
microsoft.github.io
. This yields a tree of communities (large overarching topics down to fine subtopics). In principle, you can also achieve different levels by adjusting the resolution parameter instead of full recursion. This hierarchical approach is useful for navigating and summarizing the graph at various levels of detail.

Infomap Algorithm (Information-Theoretic & Flow-Based)

Infomap takes a very different approach using information theory and random walks. Instead of modularity, it optimizes the Map Equation, which seeks a coding scheme to compress the description of an agent moving along the graph’s links
hypermode.com
. In simpler terms, imagine a random walker traversing the network: Infomap finds communities by minimizing the description length of the walker’s trajectory – effectively grouping nodes into communities such that the walker stays longer within communities and has infrequent jumps between them
hypermode.com
omicsforum.ca
. This tends to partition the graph into clusters where there are many intra-cluster paths (so the walker’s “map” can refer to clusters rather than individual nodes to compress its path description). Infomap can also detect hierarchical communities by extending the map equation to multiple levels (it can output communities and sub-communities if it yields a shorter description length)
omicsforum.ca
.

Pros: Infomap often finds high-quality communities that correspond to real flow structures in the network. It is praised for its stability and consistency – results tend to be robust and less sensitive to random initial conditions compared to, say, label propagation
hypermode.com
hypermode.com
. It can naturally handle weighted and directed networks well, since the random walk process adapts to edge weights and directions (useful if your graph has asymmetric or weighted relationships). Infomap’s information-theoretic objective sometimes captures community structure that modularity-based methods miss, especially in networks where the notion of information flow is relevant (e.g. citation networks, web graphs, transportation networks). It is also reasonably efficient: the algorithm uses techniques like Huffman coding and flow simulations, and can scale to fairly large graphs (hundreds of thousands of nodes) with optimized implementations. Additionally, Infomap provides a hierarchical clustering if desired – a two-level solution where big communities can be subdivided into smaller ones if that yields better compression
omicsforum.ca
.

Cons: Infomap can be a bit slower than Louvain/Leiden on very large graphs (though still much faster than brute-force or older algorithms). Its performance depends on the graph; for extremely large or dense graphs, it may take more time or memory than the greedy modularity methods. Infomap is also somewhat non-deterministic because it relies on random seed for the simulated walker and uses iterative refinement (though in practice it often gives similar results on repeated runs). In graphs with no clear community structure, Infomap might return a trivial single-community partition – for example, on a random graph, it tends to put all nodes into one community (because any partition doesn’t significantly shorten description length)
analyticsvidhya.com
. This is actually a reasonable outcome (no communities to find), but it contrasts with some modularity methods that might still partition a random graph due to slight fluctuations. Finally, implementing Infomap’s algorithm or understanding the math is more complex (luckily many libraries provide it). In summary, Infomap is powerful for directed/flow networks and often yields insightful clusters, but it may not always align with modularity-based results and can be slower for giant networks.

Label Propagation Algorithm

Label Propagation is a very simple, fast algorithm that propagates labels through the network until communities emerge
hypermode.com
. Initially, every node is assigned a unique label (essentially its own community). Then, in random order, each node updates its label to the most frequent label among its neighbors
omicsforum.ca
. Over iterations, labels diffuse such that densely connected groups of nodes form a consensus on a single label (community). The process stops when no node would change its label (convergence). This algorithm is non-parametric and doesn’t optimize a particular objective like modularity – it relies on the network structure alone to reach an equilibrium partition.

Pros: The major advantage is efficiency – label propagation runs in near linear time, making it feasible for very large graphs (millions of nodes/edges) with minimal computational resources
hypermode.com
. It’s extremely easy to implement and requires no priori information (no need to choose number of communities or initial seeds – it’s completely data-driven). Despite its simplicity, it can often detect reasonable community structures in large networks, especially when the communities are well separated. It’s also an anytime algorithm – it can produce a valid partition even if you stop it early, and often converges in just a few iterations.

Cons: The simplicity comes at a cost of stability and resolution. Label propagation is non-deterministic – the order of node updates and tie-breaking choices can lead to different results on different runs
hypermode.com
. It may require multiple runs and perhaps a voting or consensus on results to get a reliable partition
hypermode.com
hypermode.com
. The algorithm sometimes yields one giant community (or a few large communities) because labels can quickly dominate the network; for example, on a random or nearly homogeneous graph, all nodes might end up with the same label (one community)
analyticsvidhya.com
. Conversely, if there are nodes that act as bridges, random fluctuations might split communities inconsistently. In networks with subtle structure, label propagation can be too greedy and fail to detect small clusters (it lacks a global objective like modularity to refine things). There are improved versions to mitigate randomness (e.g. asynchronous updates or hop attenuation), but generally the variability and tendency to sometimes merge communities too aggressively are pitfalls. It’s great for a quick first pass on huge data, but for final results one often uses it in combination with other checks or more refined algorithms.

Note: Label Propagation as defined here produces a single flat partition and does not provide a hierarchical clustering. It yields one level of communities at convergence. If hierarchical structure is needed, this method on its own isn’t suitable (though one could use it as a coarse clustering and then maybe recursively label-propagate within each cluster, but that’s not standard practice).

Walktrap Algorithm (Random Walks + Hierarchical Clustering)

Walktrap is an agglomerative hierarchical community detection algorithm based on random walks (short random strolls on the graph)
omicsforum.ca
. The intuition is that random walks tend to stay within communities: if two nodes are in the same community, a random walker has many paths to move between them without exiting the community. Walktrap simulates many short random walks of a fixed length (usually 3–5 steps) to compute a distance (or similarity) between nodes. Initially, each node is its own community, then it progressively merges communities in a bottom-up manner, such that communities with similar random-walk visitation patterns are merged
omicsforum.ca
. Typically it uses a criterion similar to Ward’s method in hierarchical clustering, ensuring each merge causes the smallest increase in intra-community distance. This results in a dendrogram of communities from fine to coarse.

Pros: Walktrap provides a full hierarchical clustering of the graph, which is very useful if you want multi-level communities. You can cut the dendrogram at the level that maximizes modularity or any desired number of communities. The random-walk-based distance is a clever way to capture the notion of node proximity in terms of graph structure – it implicitly considers not just direct links but the structure of the neighborhood within a few hops. This often leads to detecting small, tightly-knit communities accurately, since a random walk of length 4 will likely remain inside such a community. It’s especially effective on moderate-size networks where a detailed hierarchy is needed. Unlike purely greedy modularity methods, Walktrap won’t miss a tiny community just because it’s slightly suboptimal to modularity; it clusters stepwise, which can sometimes preserve small clusters until a late stage (you might then select a level of the dendrogram that shows them). It also doesn’t require a preset number of clusters and tends to be more deterministic than label propagation (given the same random walk length and starting seed, results are reproducible).

Cons: Walktrap is more computationally intensive than Louvain or label propagation. Its time complexity is roughly O(n²) or O(n·m) (where n is nodes, m edges) depending on implementation optimizations, which means it can struggle with very large graphs (thousands of nodes are fine; millions would be problematic without heavy optimization). Thus, it’s typically used on smaller networks or where hierarchy is more important than speed. Another consideration is the choice of random walk length: a too-short walk (e.g., 1 step) would consider only immediate neighbors (not very informative), while too long might mix communities. In practice, 4-5 steps is recommended
inarwhal.github.io
, but if your communities are very large, one might adjust this. The algorithm’s results can also sometimes be similar to other hierarchical clustering – if the graph has a clear modular structure, it will find it, but if the structure is fuzzy, the merges might be somewhat arbitrary (however, you can always choose the best level via modularity). Finally, while providing a hierarchy is a strength, it also means you need to interpret or select the right level – the output is not a single community partition unless you decide on a cut (the default cut by maximum modularity is often used). Overall, Walktrap is a solid choice for hierarchical community detection on networks of manageable size, trading off speed for richer structure.

Spectral Algorithms (Leading Eigenvector Method)

Spectral community detection refers to algorithms that use eigenvectors of matrices (like the graph Laplacian or modularity matrix) to find clusters. A notable example is Newman's Leading Eigenvector method for modularity maximization
arxiv.org
igraph.org
. This algorithm computes the leading eigenvector of the modularity matrix (which indicates how each edge’s presence compares to random expectation) and uses its signs to split the network into two communities
igraph.org
. Essentially, it’s a form of recursive bipartitioning: the graph is split into two parts such that modularity gain is maximized, and then each part can be further split recursively until no positive modularity gain is possible
igraph.org
. The result is a hierarchical division of the graph into communities.

Pros: Spectral methods are grounded in linear algebra, providing an analytical approach to community detection. The leading eigenvector method can effectively find an optimal split of a network and then repeat, which usually yields good modularity scores. It’s deterministic for a given graph (no random heuristics involved in the core calculation), so results are stable. These methods can be faster than brute-force or naive methods because eigenvector calculations can leverage optimized routines; for medium-sized graphs they work quite well. Spectral clustering is also flexible – by using different matrices (like the Laplacian for normalized cuts, or modularity matrix for communities), one can target different clustering objectives. The leading eigenvector approach produces a hierarchy of communities (similar to a binary tree of splits) which can be useful if multi-level insight is needed.

Cons: Computing eigenvectors can still be computationally heavy for very large graphs. While faster than something like Girvan–Newman for big networks, it doesn’t scale as efficiently as Louvain or Leiden – computing the top eigenvector of a million-node graph’s modularity matrix is generally not feasible without specialized methods. Typically, spectral methods are used on networks up to maybe tens of thousands of nodes. Another con is that the leading eigenvector method inherently makes binary splits; if the true community structure isn’t well approximated by successive binary divisions, the algorithm might not capture it as naturally (it will split communities even if a more multi-way cut would be better). There’s also the issue of needing to decide when to stop splitting – the standard approach is to stop when no split increases modularity, but this relies on modularity’s resolution and can miss small communities or create slightly imbalanced splits. In practice, spectral algorithms have been somewhat supplanted by Louvain/Leiden in general use because those tend to give higher modularity and are easier to run on large data
nature.com
. Still, spectral clustering (especially using Laplacian eigenvectors for graph partitioning) is widely used in contexts like image segmentation or clustering items, although those often require specifying the number of clusters. In summary, spectral community detection is elegant and multi-level, but for huge graphs one might prefer faster heuristic methods.

Spinglass (Potts Model / Simulated Annealing)

The Spinglass algorithm treats community detection as an optimization of a spin-glass model (an analogy from physics). It’s related to the Potts model approach where each node is like an atom that can be in one of $k$ spin states (communities), and the system’s Hamiltonian (energy) favors nodes being in the same state if they are connected. By simulating this system (often via simulated annealing), the algorithm tries to find a low-energy state that corresponds to a good community division. In essence, it’s another way to optimize modularity or a similar quality function with a resolution parameter (γ) by an annealing process rather than greedy moves.

Pros: Spinglass can be very flexible. You can often specify parameters like the number of communities or resolution desired, or allow it to be determined automatically. Because it explores partitions in a global manner (simulated annealing can escape local optima by accepting worse moves occasionally), it might find a better optimum partition than a greedy algorithm that got stuck. In some cases, spinglass can detect communities where other algorithms struggle, especially if you tune the resolution parameter to the scale of communities you expect. It’s grounded in statistical physics, which provides a nice theoretical framework.

Cons: Unfortunately, spinglass algorithms are typically slow and computationally intense. Simulated annealing may require many iterations and cooling schedules, which is impractical for large networks. The results can also be variable if the annealing is not run for long enough – it might give different partitions on different runs (though one can run it multiple times and take the best result). The Analytics Vidhya comparison found spinglass to be an outlier, giving unreliable results (e.g., detecting 10 communities when most others found 3)
analyticsvidhya.com
analyticsvidhya.com
. This inconsistency and the parameter tuning required (like choosing γ, temperature schedule, etc.) make it less user-friendly. For most purposes, faster algorithms (Louvain/Leiden or Infomap) match or exceed its performance in quality. Thus, spinglass is rarely used unless one has a small network and a reason to believe a global-optimization approach might be needed. Its ability to produce a full hierarchy is also limited; it usually yields one partition (unless you scan across resolution values to simulate a hierarchy). In summary, it’s a powerful idea overshadowed by more practical methods – not recommended as a first choice due to speed and stability issues
analyticsvidhya.com
.

Conclusion and Recommendations

When choosing a community detection algorithm, consider your graph size, whether you need a hierarchical multi-level output, and what kind of structure you expect:

For small graphs (hundreds of nodes) where a full hierarchical dendrogram is valuable, algorithms like Girvan–Newman (divisive) or Walktrap (agglomerative) or spectral splitting can give comprehensive multi-level insights. These provide more interpretability at the cost of speed.

For large graphs (thousands to millions of nodes), Louvain or Leiden are typically the best choices. They are fast, yield reasonable communities, and can be applied hierarchically if needed (or via resolution parameters) to get multiple levels
microsoft.github.io
. Between the two, Leiden is usually superior due to its refinements
nature.com
 – if available, it’s often the recommended default.

Infomap is an excellent alternative, especially if your graph is directed or you care about flow dynamics. It can also produce hierarchical communities and sometimes finds patterns modularity methods miss. It’s a good second option to compare with Louvain/Leiden results for validation.

Label Propagation is a quick and easy tool for a first pass or for very large-scale data where speed is crucial. However, due to its randomness and flat output, it might need post-processing or repeated runs to be reliable
hypermode.com
. It’s useful for seeding or as a baseline, but for final analysis one usually turns to the more stable algorithms.

Others: If you have specific needs (e.g., overlapping communities, you might consider algorithms like Clique Percolation or link clustering – not covered above since GraphRAG’s context seems to use disjoint communities). Overlapping algorithms allow nodes to belong to multiple communities, but they are a different class of methods. Also, if you can formulate your problem as a statistical model, stochastic block models (SBM) or degree-corrected SBMs can infer communities and give probabilities, but those involve heavier computations (and sometimes require specifying number of communities or using Bayesian selection). In practice, the heuristic algorithms discussed above are more commonly used for general community detection tasks.

Given the context (grouping semantically similar knowledge in a GraphRAG pipeline) and no strict constraints, a hierarchical approach using Louvain or Leiden would be ideal. The Leiden algorithm in a hierarchical mode (as in GraphRAG) is designed exactly for this, but as you observed, if a particular implementation “consistently fails” or yields trivial communities, switching to the robust Louvain method is a valid solution
microsoft.github.io
analyticsvidhya.com
. Louvain should produce a reasonable partition (as your tests showed with ~6 communities), and you can always apply it recursively for sub-communities.

In summary, there are many algorithms available, each with pros/cons:

Greedy modularity methods (Louvain/Leiden) – fast, scalable, good default (hierarchical via recursion or multi-level output; be mindful of resolution issues).

Flow-based (Infomap) – captures different structure (possibly hierarchical), stable but slightly slower.

Hierarchical clustering (Girvan–Newman, Walktrap, spectral) – provide full multi-level insight; great for small/medium graphs, but computationally heavier.

Heuristic propagation (Label Propagation) – extremely fast, but result quality can vary; use for quick partitioning or huge graphs with caution.

Others (Spinglass, etc.) – rarely used in practice due to performance or complexity, unless niche requirements.

Each algorithm has nuances in implementation, but the above outlines their typical behavior. For your use case, focusing on a hierarchical Louvain/Leiden solution (with possibly Infomap as a cross-check) seems prudent, balancing quality and performance
analyticsvidhya.com
nature.com
. Always consider experimenting with a couple of algorithms and comparing community outcomes – this can give confidence that the communities detected are robust and meaningful
hypermode.com
hypermode.com
. Good luck with building the community detection stage of your GraphRAG pipeline!

Sources:

Traag et al., “From Louvain to Leiden: guaranteeing well-connected communities,” Scientific Reports 9, 5233 (2019) – Improved Leiden algorithm vs Louvain
nature.com
nature.com
.

Microsoft GraphRAG Documentation – Hierarchical Leiden community detection for multi-level knowledge graph clustering
microsoft.github.io
.

Hypermode Blog – “Top Community Detection Algorithms Compared” (2025) – Overview of Girvan–Newman, Louvain, Label Propagation, Infomap, etc., with use-case guidance
hypermode.com
hypermode.com
.

Analytics Vidhya – “Comparative Analysis of Community Detection Algorithms” (2022) – Empirical comparison on benchmark graphs (Louvain performed best; spinglass inconsistent)
analyticsvidhya.com
analyticsvidhya.com
.

OmicsAnalyst Forum – explanation of Walktrap, Infomap, and Label Propagation algorithms for module detection
omicsforum.ca
omicsforum.ca
.

Memgraph Blog – “Community Detection Algorithms with NetworkX” – Girvan–Newman algorithm concept and other techniques
memgraph.com
memgraph.com
.