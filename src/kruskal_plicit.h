#ifdef EXPLICIT_SET
#   define kruskal kruskal_explicit_set
#   define runKruskals kruskal_run_explicit_set
#   define makeUnionFind make_union_find_explicit_set
#   define unionCCs unionCCs_explicit_set
#   define find find_explicit_set
#   include <kruskal_explicit_set.h>
#else
#   define kruskal kruskal_implicit_set
#   define runKruskals kruskal_run_implicit_set
#   define makeUnionFind make_union_find_implicit_set
#   define unionCCs unionCCs_implicit_set
#   define find find_implicit_set
#   include <kruskal_implicit_set.h>
#endif

#include <kruskal_base.h>
