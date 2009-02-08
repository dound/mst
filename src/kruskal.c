// Implement's Kruskal's algorithm

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <assert.h>
#include "mst.h"


#define INIT_CC_CAP 2


// set of vertices
typedef struct
{
    // array of vertices
    int *vertices;
    // capacity of array
    int capacity;
    // num elements in CC
    int size;
} UFSet;


// parent of each vertex
int *parents;
// sets of connected components
UFSet *CCs;


void makeUnionFind(int n);
void unionCCs(int a, int b);
void setParent(int group, int parent);
int find(int u);
int compareEdges(const void *a, const void*b);
void runKruskals(int n, int m, edge *G);


// main function that algorithm must implement from mst.h
void calculateMst(int n, int m, edge *G)
{
    T = (edge *)malloc((n-1)*sizeof(edge));

    makeUnionFind(n);
    qsort(G, m, sizeof(edge), compareEdges);
    runKruskals(n, m, G);
}

// used for qsort
int compareEdges(const void *a, const void*b)
{
    edge *arg1 = (edge *)a;
    edge *arg2 = (edge *)b;
    if (arg1->weight < arg2->weight)
        return -1;
    else if (arg1->weight == arg2->weight)
        return 0;
    else
        return 1;
}

// runs kruskal's algorithm
void runKruskals(int n, int m, edge *G)
{
    int nextEdge = 0;
    mstWeight = 0;
    for (int i = 0; i < m && nextEdge < n-1; i++)
    {
        int groupA = find(G[i].u);
        int groupB = find(G[i].v);
        // check if same CC
        if (groupA == groupB)
            continue;
        // TODO remove - dpi
        assert(CCs[groupA].size);
        assert(CCs[groupA].capacity);
        assert(CCs[groupB].size);
        assert(CCs[groupB].capacity);
        unionCCs(groupA, groupB);
        // TODO: make T pointers to elements of G? - dpi
        T[nextEdge].u = G[i].u;
        T[nextEdge].v = G[i].v;
        mstWeight += G[i].weight;
        nextEdge++;
    }
}

/*** union find functions ***/
void makeUnionFind(int n)
{
    // init parents
    parents = (int *)malloc((n+1)*sizeof(int));
    for (int i = 0; i < n+1; i++)
        parents[i] = i;
    
    CCs = (UFSet *)malloc((n+1)*sizeof(UFSet));
    for (int i = 0; i < n+1; i++)
    {
        CCs[i].vertices = (int *)malloc(INIT_CC_CAP*sizeof(int));
        assert(CCs[i].vertices);
        CCs[i].capacity = INIT_CC_CAP;
        CCs[i].size = 1;
        CCs[i].vertices[0] = i;
    }
}

void unionCCs(int a, int b)
{
    if (CCs[a].size <= CCs[b].size)
        setParent(a, b);
    else
        setParent(b, a);
}
// union helper func
inline void setParent(int a, int b)
{
    // grow array if necessary
    if (CCs[b].capacity < CCs[a].size + CCs[b].size)
    {
        int *oldParent = CCs[b].vertices;
        CCs[b].capacity *= 2;
        CCs[b].vertices = (int *)malloc(CCs[b].capacity * sizeof(int));
        assert(CCs[b].vertices);
        memcpy(CCs[b].vertices, oldParent, CCs[b].size*sizeof(int));
        free(oldParent);
    }

    // set new parent values
    for (int i = 0; i < CCs[a].size; i++)
        parents[CCs[a].vertices[i]] = b;

    // copy over values in set
    memcpy(CCs[b].vertices+CCs[b].size, CCs[a].vertices, CCs[a].size*sizeof(int));
    free(CCs[a].vertices);
    CCs[b].size += CCs[a].size;
    // TODO: remove this which is just for debugging - dpi
    CCs[a].size = 0;
    CCs[a].capacity = 0;
}

inline int find(int u)
{
    return parents[u];
}
