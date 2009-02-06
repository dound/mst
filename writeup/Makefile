# Makefile to build the PDF for the report
# make -- builds the reports including all plots
# make clean -- delete byproducts

TEX = latex
TEX_SRCS = $(wildcard *.tex)

NAME = report
MASTER = $(NAME).pdf
CLEANABLE = $(MASTER)

# determine which gnuplot files to build (using their own makefiles)
GNUPLOT_FIGURE_SRCS = $(shell find figures -name '*.gnuplot')
GNUPLOT_FIGURE_PDFS = $(GNUPLOT_FIGURE_SRCS:.gnuplot=.pdf)
CLEANABLE += $(GNUPLOT_FIGURE_SRCS:.gnuplot=.eps) $(GNUPLOT_FIGURE_PDFS)

# determine which bplot files to build (using their own makefiles)
BPLOT_FIGURE_SRCS = $(shell find figures -name '*.bplot')
BPLOT_FIGURE_PDFS = $(BPLOT_FIGURE_SRCS:.bplot=.pdf)
CLEANABLE += $(BPLOT_FIGURE_SRCS:.bplot=.eps) $(BPLOT_FIGURE_PDFS)

PLOT_PDFS = $(GNUPLOT_FIGURE_PDFS) $(BPLOT_FIGURE_PDFS)
PLOT_DATA = $(shell find data -name '*.dat')


.PHONY: all cleanjunk clean

# build the pdfs and cleanup the byproducts
all : $(MASTER)

# build the pdf (run pdflatex until all references are resolved)
$(MASTER) : $(TEX_SRCS) $(PLOT_PDFS)
	@name=`echo $@ | sed -e "s#.pdf##"`; \
	while (pdflatex $$name.tex ; \
	grep  "Rerun to get cross" $$name.log ) do true ; \
	done; \

# target for building our plot figures (delegated to the figures Makefile)
$(PLOT_PDFS): $(PLOT_DATA)
	make --no-print-directory -C $(dir $@) $(notdir $@)

# remove byproducts of building the pdf
cleanjunk:
	@rm -f $(NAME).aux $(NAME).bbl $(NAME).blg $(NAME).dvi $(NAME).log
	@rm -f $(NAME).*pk $(NAME).tfm $(NAME).lot $(NAME).lof $(NAME).out $(NAME).toc

# remove the pdf and its byproducts
clean: cleanjunk
	@rm -f $(CLEANABLE)
