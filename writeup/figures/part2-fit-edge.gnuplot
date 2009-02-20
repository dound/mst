unset title
unset label
set autoscale
set key bottom right
set size 0.7, 0.7

set xlabel "Number of Vertices"
set grid x
set xr [64:8192]
set logscale x
set xtics (2,8,32,128,512,2048,8192)

set ylabel "Average MST Weight"
set grid y
set format y "%G"
set yr [1:1.3]

set terminal postscript eps color enhanced linewidth 3 dashed
set output "part2-fit-edge.eps"

set style line 1 lt 1 lc rgb "#000000" pt 1
set style line 2 lt 2 lc rgb "#CC0000" pt 2
set style line 3 lt 3 lc rgb "#00CC00" pt 3
set style line 4 lt 1 lc rgb "#0000CC" pt 4
set style line 5 lt 2 lc rgb "#00CC00" pt 5
set style line 6 lt 3 lc rgb "#0000CC" pt 6

# data to fit
fitdata = "../data/weight/edge.dat"

log2(x) = log(x) / log(2)

#functions to fit
# vars:  m=multiplier, c=additive constant, e=exponentiation power, b=exponentiation base
#function        multiplier      growth rate                  additive const
const2fit(x)   = const2fit_c
log2fit(x)     = log2fit_m     * log2(x)                    + log2fit_c
lindlog2fit(x) = lindlog2fit_m * x**lindlog2fit_e / log2(x) + lindlog2fit_c
lin2fit(x)     = lin2fit_m     * x**lin2fit_e               + lin2fit_c
loglin2fit(x)  = loglin2fit_m  * x**loglin2fit_e * log2(x)  + loglin2fit_c
exp2fit(x)     = exp2fit_m     * exp2fit_b**x               + exp2fit_c

# fit them
fit const2fit(x)   fitdata using 1:3:2:4 via const2fit_c
fit log2fit(x)     fitdata using 1:3:2:4 via log2fit_m, log2fit_c
fit lindlog2fit(x) fitdata using 1:3:2:4 via lindlog2fit_m, lindlog2fit_e, lindlog2fit_c
fit lin2fit(x)     fitdata using 1:3:2:4 via lin2fit_m, lin2fit_e, lin2fit_c
fit loglin2fit(x)  fitdata using 1:3:2:4 via loglin2fit_m, loglin2fit_e, loglin2fit_c
fit exp2fit(x)     fitdata using 1:3:2:4 via exp2fit_m, exp2fit_b, exp2fit_c

plot fitdata using 1:3 title 'Data: random edge lengths' with linespoints, \
     fitdata using 1:3:2:4 title 'Edge'    with yerrorbars, \
     const2fit(x)   title sprintf('%1.f: constant', const2fit_c)                                                               ls 1, \
     lindlog2fit(x) title sprintf('%.3f * |V|^{%.2f} / log2(|V|) + %.1f: linear/log', lindlog2fit_m, lindlog2fit_e, lindlog2fit_c) ls 3, \
     lin2fit(x)     title sprintf('%.3f * |V|^{%.2f} + %.1f: linear', lin2fit_m, lin2fit_e, lin2fit_c)                           ls 4, \
     loglin2fit(x)  title sprintf('%.3f * |V|^{%.2f} * log2(|V|) + %.1f: linear*log', loglin2fit_m, loglin2fit_e, loglin2fit_c)    ls 5, \
     exp2fit(x)     title sprintf('%.1f * %.1f^|V| + %.1f: exponential', exp2fit_m, exp2fit_b, exp2fit_c)                        ls 6, \
     log2fit(x)     title sprintf('%.4f * log2(|V|) + %.1f: log', log2fit_m, log2fit_c)                                          ls 2
