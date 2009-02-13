// interface for calculating mst
#ifndef MST_H
#define MST_H

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
