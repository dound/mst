// interface for calculating mst
#ifndef MST_H
#define MST_H

/** MST algorithms */
#define BEST_ALG   1
#define KRUSKAL    2
#define PRIM_DENSE 3
#define PRIM_BHEAP 4
#define KKT        5

/* use the default value for ALG if one is not specified */
#ifndef ALG
#  define ALG BEST_ALG
#endif

/** whether to use ints instead of floats wherever possible */
#ifdef _NO_FLOATS_
    typedef int foi;
#   define FOI_TO_OUTPUT_WEIGHT(w) ((w) / 10.0f)
#else
    typedef float foi;
#   define FOI_TO_OUTPUT_WEIGHT(w) (w)
#endif

// representation of edges
typedef struct
{
    int u;
    int v;
    foi weight;
} edge;

/** run Kruskal's algorithm */
void kruskal(char* fn);

/** run a version of Prim's algorithm optimized for dense-graphs */
void prim_dense(char* fn);

#endif
