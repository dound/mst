# Makefile for the boost MST weight computer binary
# ------------------------------------------------------------------------------
# make        -- builds
# make debug  -- builds in debug mode
# make release-- builds in release mode
# make clean  -- clean up byproducts

include ../../src/Makefile.defs

# define names of our build targets
BCMW = boost_compute_mst_weight

# compiler and its directives
CC     = g++
INC    = /afs/ir/users/d/g/dgu/lib  # include boost
LIBS   =
CPPFLAGS = -c -Wall $(BUILD_TYPE_FLAGS)

# project sources
SRCS = boost_compute_mst_weight.cpp
OBJS = $(patsubst %.cpp,%.o,$(SRCS))
DEPS = $(patsubst %.cpp,.%.d,$(SRCS))

# include the dependencies once we've built them
ifdef INCLUDE_DEPS
include $(DEPS)
endif

#########################
## PHONY TARGETS
#########################
# note targets which don't produce a file with the target's name
.PHONY: all clean clean-all clean-deps debug release deps $(BCMW).ir

# build our apps
all: $(BCMW)

# clean up all by-products
clean-all: clean clean-deps

# clean up by-products (except dependency files)
clean:
	@rm -f *.o $(BCMW)

# clean up dependency files
clean-deps:
	@rm -f .*.d

# shorthand for building the debug or release build
debug release:
	@$(MAKE) BUILD_TYPE=$@ all

# build the dependency files
deps: $(DEPS)

# includes are ready build commands for client, server, and lib
$(BCMW).ir: $(OBJS)
	$(CC) -o $(BCMW) $(OBJS) $(LIBS)

#########################
## REAL TARGETS
#########################
$(BCMW): deps
	@$(MAKE) BUILD_TYPE=$(BUILD_TYPE) INCLUDE_DEPS=1 $@.ir

$(DEPS): .%.d: %.cpp
	$(CC) -MM $(CPPLAGS) $< > $@
