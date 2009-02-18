unset title
unset label
set autoscale
set key top left
set size 0.7, 0.7

set xlabel "Number of Vertices"
set grid x
set xr [2:8192]
set logscale x 2
set xtics (2,8,32,128,512,2048,8192)

set ylabel "Average MST Weight"
set grid y
set format y "%G"
set yr [0.25:1024]
set logscale y 2
set ytics (0.25,1,4,16,64,256,1024)

set terminal postscript eps color enhanced linewidth 3 dashed
set output "part2-with-theoretical.eps"

set style line 1 lt 1 lc rgb "#000000" pt 6
set style line 2 lt 1 lc rgb "#CC0000" pt 6
set style line 3 lt 2 lc rgb "#00CC00" pt 6
set style line 4 lt 3 lc rgb "#0000CC" pt 6

set style line 11 lt 1 lw 3 lc rgb "#000000" pt 0
set style line 22 lt 1 lc rgb "#CC0000" pt 0
set style line 33 lt 2 lc rgb "#00CC00" pt 0
set style line 44 lt 3 lc rgb "#0000CC" pt 0

# theoretical upper bounds
loc1(x) = 1
loc2(x) = x**(0.5) + 1
loc3(x) = x**(2/3.0) + x**(1/3.00) + 1
loc4(x) = x**(0.75) + x**(0.5) + x**(0.25) + 1

plot "../data/weight/loc1.dat" using 1:3 title 'Empircal d=1'    with linespoints ls 1,  \
     loc1(x)                             title 'Theoretical d=1' with linespoints ls 11, \
     "../data/weight/loc2.dat" using 1:3 title 'Empirical d=2'   with linespoints ls 2,  \
     loc2(x)                             title 'Theoretical d=2' with linespoints ls 22, \
     "../data/weight/loc3.dat" using 1:3 title 'Empirical d=3'   with linespoints ls 3,  \
     loc3(x)                             title 'Theoretical d=3' with linespoints ls 33, \
     "../data/weight/loc4.dat" using 1:3 title 'Empirical d=4'   with linespoints ls 4,  \
     loc4(x)                             title 'Theoretical d=4' with linespoints ls 44
