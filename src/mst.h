// interface for calculating mst
#ifndef MST_H
#define MST_H

/** MST algorithms */
#define BEST_ALG            1
#define KRUSKAL_EXPLICIT_FS 2
#define KRUSKAL_EXPLICIT_PS 3
#define KRUSKAL_IMPLICIT_FS 4
#define KRUSKAL_IMPLICIT_PS 5
#define PRIM_DENSE          6
#define PRIM_HEAP           7

/* use the default value for ALG if one is not specified */
#ifndef ALG
#  define ALG BEST_ALG
#endif

/** whether to use ints instead of floats wherever possible */
#ifdef _NO_FLOATS_
    typedef int foi;
    typedef unsigned long long foi_big;
#   define FOI_TO_OUTPUT_WEIGHT(w) ((w) / 10.0)
#else
    typedef float foi;
    typedef double foi_big;
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
void kruskal_explicit_set_with_fs(char* fn);
void kruskal_explicit_set_with_ps(char* fn);
void kruskal_implicit_set_with_fs(char* fn);
void kruskal_implicit_set_with_ps(char* fn);

/** run a version of Prim's algorithm optimized for dense-graphs */
void prim_dense(char* fn);

#endif
