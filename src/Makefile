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
