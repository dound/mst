unset title
unset label
set autoscale
set key bottom right
set size 0.7, 0.7

set xlabel "Edge Density"
set grid x

set ylabel "Relative Big-Oh Runtime (for arbitrary vertex count)"
set grid y
set logscale y
set format y "%.0E"

set label "Crossover Density = .985" at graph .45, graph .9
set arrow from graph .85, graph .9 to graph .97, graph .955

set terminal postscript eps color enhanced linewidth 3 dashed
set output "work_for_sparse_vs_dense_graph_generation_algs.eps"

set style line 1 lt 1 lc rgb "#CC0000" pt 0
set style line 2 lt 2 lc rgb "#00CC00" pt 6
set style line 3 lt 1 lc rgb "#0000CC" pt 0

plot "../data/work_for_sparse_vs_dense_graph_generation_algs-131072.dat" using 1:2  title 'Sparse Alg Loose' with linespoints ls 1, \
     "../data/work_for_sparse_vs_dense_graph_generation_algs-131072.dat" using 1:3  title 'Sparse Alg Tight' with linespoints ls 2, \
     "../data/work_for_sparse_vs_dense_graph_generation_algs-131072.dat" using 1:4  title 'Dense Alg'  with linespoints ls 3
