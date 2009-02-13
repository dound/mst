// interface for calculating mst
#ifndef MST_H
#define MST_H

// representation of edges
typedef struct
{
    int u;
    int v;
    float weight;
} edge;

/** run Kruskal's algorithm */
void kruskal(char* fn);

/** run a version of Prim's algorithm optimized for dense-graphs */
void prim_dense(char* fn);

#endif
