unset title
unset label
set autoscale
set key bottom right
set size 0.7, 0.7

set xlabel "Number of Vertices"
set grid x
set xr [2:8192]
set logscale x 2
set xtics (2,8,32,128,512,2048,8192)

set ylabel "Average MST Weight"
set grid y
set format y "%G"
set yr [1:605]
set logscale y 2

set terminal postscript eps color enhanced linewidth 3 dashed
set output "part2.eps"

set style line 1 lt 1 lc rgb "#000000" pt 0
set style line 2 lt 1 lc rgb "#CC0000" pt 6
set style line 3 lt 2 lc rgb "#00CC00" pt 0
set style line 4 lt 3 lc rgb "#0000CC" pt 0

plot "../data/weight/edge.dat" using 1:3 title 'Edge'    with linespoints ls 1, \
     "../data/weight/loc2.dat" using 1:3 title 'Dim = 2' with linespoints ls 2, \
     "../data/weight/loc3.dat" using 1:3 title 'Dim = 3' with linespoints ls 3, \
     "../data/weight/loc4.dat" using 1:3 title 'Dim = 4' with linespoints ls 4
