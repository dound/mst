# Makefile to build the plots

SRCS = $(wildcard *.gnuplot)
EPSS = $(SRCS:.gnuplot=.eps)
PDFS = $(SRCS:.gnuplot=.pdf)

BSRCS = $(wildcard *.bplot)
EPSS += $(BSRCS:.bplot=.eps)
PDFS += $(BSRCS:.bplot=.pdf)

.PHONY: default clean
.SUFFIXES: .gnuplot .bplot

default: $(PDFS)

# build the eps file from gnuplot files
%.eps : %.gnuplot
	gnuplot $<

# build the eps file from bplot files
%.eps : %.bplot
	../bargraph.pl -eps $< > $@

# build the pdf file
%.pdf : %.eps
	epstopdf $<

# remove the graph outputs
clean:
	rm -f $(EPSS) $(PDFS)
