#ifdef EXPLICIT_SET

#   define makeUnionFind make_union_find_explicit_set
#   define unionCCs unionCCs_explicit_set
#   define find find_explicit_set
#   include <kruskal_explicit_set.h>

#   define PARTIAL_SORT
#   define kruskal kruskal_explicit_set_with_ps
#   define runKruskals kruskal_run_explicit_set_with_ps
#   include <kruskal_base.h>
#   undef PARTIAL_SORT
#   undef kruskal
#   undef runKruskals
#   define kruskal kruskal_explicit_set_with_fs
#   define runKruskals kruskal_run_explicit_set_with_fs
#   include <kruskal_base.h>

#else

#   define makeUnionFind make_union_find_implicit_set
#   define unionCCs unionCCs_implicit_set
#   define find find_implicit_set
#   include <kruskal_implicit_set.h>

#   define PARTIAL_SORT
#   define kruskal kruskal_implicit_set_with_ps
#   define runKruskals kruskal_run_implicit_set_with_ps
#   include <kruskal_base.h>
#   undef PARTIAL_SORT
#   undef kruskal
#   undef runKruskals
#   define kruskal kruskal_implicit_set_with_fs
#   define runKruskals kruskal_run_implicit_set_with_fs
#   include <kruskal_base.h>

#endif
