# Makefile for the main project binaries
# ------------------------------------------------------------------------------
# make        -- builds in the default mode specified by $(BUILD_TYPE)
# make debug  -- builds in debug mode
# make release-- builds in release mode
# make clean  -- clean up byproducts

include Makefile.defs

# define names of our build targets
MST = mst

# compiler and its directives
CC     = $(DEFAULT_CC)
LIBS   =
CFLAGS = -c -Wall $(BUILD_TYPE_FLAGS)

# project sources
SRCS = mst.c kruskal.c
OBJS = $(patsubst %.c,%.o,$(SRCS))
DEPS = $(patsubst %.c,.%.d,$(SRCS))

# include the dependencies once we've built them
ifdef INCLUDE_DEPS
include $(DEPS)
endif

#########################
## PHONY TARGETS
#########################
# note targets which don't produce a file with the target's name
.PHONY: all check-cflags clean clean-all clean-deps debug release deps $(MST).ir

# build our apps
all: $(MST)

check-cflags:
	@echo $(CC) $(CFLAGS) > .cflags_tmp; \
	diff -q .cflags_prev .cflags_tmp > /dev/null && ok=1 || ok=0; \
	if [ $$ok -eq 1 ]; then \
	    rm .cflags_tmp; \
	else \
	    echo "CFLAGS changed: will do a clean build"; \
	    mv .cflags_tmp .cflags_prev; \
	    make clean; \
	fi

# clean up all by-products
clean-all: clean clean-deps

# clean up by-products (except dependency files)
clean:
	@echo -n "object and binary cleanup: "
	rm -f *.o $(MST)

# clean up dependency files
clean-deps:
	@echo -n "dependency cleanup: "
	rm -f .*.d .cflags_prev

# shorthand for building the debug or release build
debug release:
	@$(MAKE) BUILD_TYPE=$@ all

# build the dependency files
deps: $(DEPS)

# includes are ready build commands for client, server, and lib
$(MST).ir: check-cflags $(OBJS)
	$(CC) -o $(MST) $(OBJS) $(LIBS)

#########################
## REAL TARGETS
#########################
$(MST): deps
	@$(MAKE) BUILD_TYPE=$(BUILD_TYPE) INCLUDE_DEPS=1 $@.ir

$(DEPS): .%.d: %.c
	$(CC) -MM $(CFLAGS) $< > $@
