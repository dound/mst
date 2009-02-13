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

#endif
