# Makefile for the main project binaries
# ------------------------------------------------------------------------------
# make        -- builds in the default mode specified by $(BUILD_TYPE)
# make debug  -- builds in debug mode
# make release-- builds in release mode
# make clean  -- clean up byproducts

include Makefile.defs
VPATH = input

# define names of our build targets
MST = mst
IC = input_checker
APPS = $(MST) $(IC)

# handle custom defines
ifneq ($(DEF), )
CUSTOM_DEFS = $(shell echo -D$(DEF) | sed -e 's/,/ -D/g')
endif

# compiler and its directives
CC     = $(DEFAULT_CC)
INCS   = -I.
LIBS   =
CFLAGS = -c -Wall $(INCS) $(BUILD_TYPE_FLAGS) $(CUSTOM_DEFS)

# project sources
SRCS_MST = mst.c kruskal.c
OBJS_MST = $(patsubst %.c,%.o,$(SRCS_MST))
DEPS_MST = $(patsubst %.c,.%.d,$(SRCS_MST))

# other helper sub-projects
SRCS_IC = input_checker.c
OBJS_IC = $(patsubst %.c,%.o,$(SRCS_IC))
DEPS_IC = $(patsubst %.c,.%.d,$(SRCS_IC))

# include the dependencies once we've built them
DEPS_ALL = $(shell echo $(DEPS_MST) $(DEPS_IC) | sed -e 's/ /\n/g' | sort -u)
ifdef INCLUDE_DEPS
include $(DEPS_ALL)
endif

#########################
## PHONY TARGETS
#########################
# note targets which don't produce a file with the target's name
.PHONY: all check-cflags clean clean-all clean-deps debug release deps $(MST).ir

# build our apps
all: $(APPS)

# cleans out built objects if the compiler or flags have changed since the last build
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
deps: $(DEPS_ALL)

# includes are ready build commands for the apps
$(MST).ir: check-cflags $(OBJS_MST)
	$(CC) -o $(MST) $(OBJS_MST) $(LIBS)

$(IC).ir: check-cflags $(OBJS_IC)
	$(CC) -o $(IC) $(OBJS_IC) $(LIBS)

#########################
## REAL TARGETS
#########################
$(APPS): deps
	@$(MAKE) BUILD_TYPE=$(BUILD_TYPE) INCLUDE_DEPS=1 $@.ir

$(DEPS_ALL): .%.d: %.c
	$(CC) -MM $(CFLAGS) $< > $@
