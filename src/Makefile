# Makefile for the main project binaries
# ------------------------------------------------------------------------------
# make        -- builds in the default mode specified by $(BUILD_TYPE)
# make debug  -- builds in debug mode
# make release-- builds in release mode
# make clean  -- clean up byproducts

# define names of our build targets
MST = mst

# utility programs used by this Makefile
MAKE = gmake --no-print-directory

# debug and release modes
BUILD_TYPE = debug
ifeq ($(BUILD_TYPE),debug)
BUILD_TYPE_FLAGS = -g -D_DEBUG_
else
MATH_OPTS = -ffast-math -fno-math-errno -ffinite-math-only -fno-trapping-math -fsingle-precision-constant
BUILD_TYPE_FLAGS = -O3 -fwhole-program -mtune=nocana $(MATH_OPTS) -fprefetch-loop-arrays
endif

# compiler choices
GCC_IN_PATH = g++  # 4.1.3 on myth
GCC_4_3_3   = /afs/ir.stanford.edu/users/d/g/dgu/bin/gcc-4.3.3/bin/g++
GCC_4_4     = /afs/ir.stanford.edu/users/d/g/dgu/bin/gcc-4.4/bin/g++
ICC         = /afs/ir.stanford.edu/users/d/g/dgu/bin/intel/Compiler/11.0/074/bin/intel64/icc
DEFAULT_CC  = $(GCC_IN_PATH)

# compiler and its directives
CC     = $(DEFAULT_CC)
LIBS   = 
CFLAGS = -c -Wall $(BUILD_TYPE_FLAGS)

# project sources
SRCS = mst.c
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
.PHONY: all clean clean-all clean-deps debug release deps $(MST).ir

# build our apps
all: $(MST)

# clean up all by-products
clean-all: clean clean-deps

# clean up by-products (except dependency files)
clean:
	@rm -f *.o $(MST)

# clean up dependency files
clean-deps:
	@rm -f .*.d

# shorthand for building the debug or release build
debug release:
	@$(MAKE) BUILD_TYPE=$@ all

# build the dependency files
deps: $(DEPS)

# includes are ready build commands for client, server, and lib
$(MST).ir: $(OBJS)
	$(CC) -o $(MST) $(OBJS) $(LIBS)

#########################
## REAL TARGETS
#########################
$(MST): deps
	@$(MAKE) BUILD_TYPE=$(BUILD_TYPE) INCLUDE_DEPS=1 $@.ir

$(DEPS): .%.d: %.c
	$(CC) -MM $(CFLAGS) $< > $@
