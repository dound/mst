// interface for calculating mst
#ifndef MST_H
#define MST_H

// representation of edges in G or T
typedef struct
{
    int u;
    int v;
    float weight;
} edge;


/********** output data **********/
// total weight of mst
extern float mstWeight;
// array of edges in mst, T
extern edge *T;

// reads input file, calculates minimum spanning tree, stores result in
// output data structure
void calculateMst(int n, int m, edge *G);

// outputs the graph G
void printGraph(edge *G, int size, float weight);

#endif
