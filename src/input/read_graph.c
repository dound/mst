#include <input/read_graph.h>

/* apply INPUT_TYPE */
#if INPUT_TYPE == SCANF
#  define GRAPH_TYPE EDGE_LIST
#  include "read_graph_scanf.h"
#  undef  GRAPH_TYPE
#  define GRAPH_TYPE HEAPIFIED_EDGE_LIST
#  include "read_graph_scanf.h"
#  undef  GRAPH_TYPE
#  define GRAPH_TYPE ADJACENCY_LIST
#  include "read_graph_scanf.h"
#  undef  GRAPH_TYPE
#  define GRAPH_TYPE ADJACENCY_MATRIX
#  include "read_graph_scanf.h"
#elif INPUT_TYPE == MMAP
#  define GRAPH_TYPE EDGE_LIST
#  include "read_graph_mmap.h"
#  undef  GRAPH_TYPE
#  define GRAPH_TYPE HEAPIFIED_EDGE_LIST
#  include "read_graph_mmap.h"
#  undef  GRAPH_TYPE
#  define GRAPH_TYPE ADJACENCY_LIST
#  include "read_graph_mmap.h"
#  undef  GRAPH_TYPE
#  define GRAPH_TYPE ADJACENCY_MATRIX
#  include "read_graph_mmap.h"
#else
#  error bad argument to INPUT_TYPE
#endif

/**
 * custom strchr function
 */
char *strchr2(char *start, char val)
{
    while (*start != val)
        start++;
    return start;
}

// table of values of '0' character added up - helps with parsing
int diffs[] = {0, -48, -528, -5328, -53328, -533328, -5333328, -53333328,
               -533333328};
// table of powers of 10
int pwrs[] = {1, 10, 100, 1000, 10000, 100000, 1000000, 10000000,
              100000000};
