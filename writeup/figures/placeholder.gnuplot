# gnuplot script file for a placeholder plot

unset title
unset label
set autoscale
set key top left
set size 0.7, 0.7

set xlabel "# of Nodes"
set grid x
set logscale x
set xr [2:100000]

set ylabel "System CPU Usage Time (sec)"
set grid y
set logscale y

set terminal postscript eps color enhanced linewidth 3 dashed
set output "placeholder.eps"

set style line 1 lt 1 lc rgb "#CC0000" pt 0
set style line 2 lt 2 lc rgb "#00CC00" pt 0
set style line 3 lt 3 lc rgb "#0000CC" pt 0

plot "../data/placeholder.dat" using 1:($2/1000)  title 'Log'        with linespoints ls 1, \
     "../data/placeholder.dat" using 1:($3/1000)  title 'Linear'     with linespoints ls 2, \
     "../data/placeholder.dat" using 1:($4/1000)  title 'Linear Log' with linespoints ls 3
