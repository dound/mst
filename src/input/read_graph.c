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
