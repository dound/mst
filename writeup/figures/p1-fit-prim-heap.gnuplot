unset title
unset label
set autoscale
set key bottom right
set size 0.7, 0.7

set xlabel "Number of Edges"
set grid x
set xr [100000:12000000]
#set logscale x 2
set xtics (100000,1000000,10000000)
set logscale x 2
set format x "%.0f"

set ylabel "Average Runtime (millisec)"
set grid y
set format y "%.0e"
#set yr [1:60]
set logscale y 2

set terminal postscript eps color enhanced linewidth 3 dashed
set output "p1-fit-prim-heap.eps"

set style line 1 lt 1 lc rgb "#000000" pt 1
set style line 2 lt 2 lc rgb "#CC0000" pt 2
set style line 3 lt 3 lc rgb "#00CC00" pt 3
set style line 4 lt 1 lc rgb "#0000CC" pt 4
set style line 5 lt 2 lc rgb "#00CC00" pt 5
set style line 6 lt 3 lc rgb "#0000CC" pt 6

# data to fit
fitdata = "../data/perf/e-all-pom-ph-None-1-97175a2fd4"

log2(x) = log(x) / log(2)

const2fit(x)   = const2fit_c
log2fit(x)     = log2fit_m     * log2(x)                    + log2fit_c
lindlog2fit(x) = lindlog2fit_m * x**lindlog2fit_e / log2(x) + lindlog2fit_c
lin2fit(x)     = lin2fit_m     * x**lin2fit_e               + lin2fit_c
loglin2fit(x)  = loglin2fit_m  * x**loglin2fit_e * log2(x)  + loglin2fit_c
exp2fit(x)     = exp2fit_m     * exp2fit_b**x               + exp2fit_c

# fit them
#fit const2fit(x)   fitdata using 2:($5*1000):($4*1000):($6*1000) via const2fit_c
#fit log2fit(x)     fitdata using 2:($5*1000):($4*1000):($6*1000) via log2fit_m, log2fit_c
#fit lindlog2fit(x) fitdata using 2:($5*1000):($4*1000):($6*1000) via lindlog2fit_m, lindlog2fit_e, lindlog2fit_c
#fit lin2fit(x)     fitdata using 2:($5*1000):($4*1000):($6*1000) via lin2fit_m, lin2fit_e, lin2fit_c
fit loglin2fit(x)  fitdata using 2:($5*1000):($4*1000):($6*1000) via loglin2fit_m, loglin2fit_e, loglin2fit_c
#fit exp2fit(x)     fitdata using 2:($5*1000):($4*1000):($6*1000) via exp2fit_m, exp2fit_b, exp2fit_c

plot fitdata using 2:($5*1000) title 'Prim with Pairing Heap' with linespoints, \
      loglin2fit(x)  title '1.0 * |V|^{0.9} * log2(|V|) + -0.01: linear*log'

#     log2fit(x)     title sprintf('%.1f * log2(x) + %.1f: log', log2fit_m, log2fit_c)                                          ls 2, \
#     lindlog2fit(x) title sprintf('%.1f * x^{%.1f} / log2(x) + %.1f: linear/log', lindlog2fit_m, lindlog2fit_e, lindlog2fit_c) ls 3, \
#     lin2fit(x)     title sprintf('%.1f * x^{%.1f} + %.1f: linear', lin2fit_m, lin2fit_e, lin2fit_c)                           ls 4, \
#     exp2fit(x)     title sprintf('%.1f * %.1f^x + %.1f: exponential', exp2fit_m, exp2fit_b, exp2fit_c)                        ls 6
