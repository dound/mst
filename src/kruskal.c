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

// a node in the tree that represents the connected component
typedef struct
{
    int size;
    int parent;
} UFCCNode;


// parent of each vertex
int *parents;
//UFCCNode *parents;
// sets of connected components
UFSet *CCs;


void makeUnionFind(int n);
void unionCCs(int a, int b);
void setParent(int group, int parent);
int find(int u);
int compareEdges(const void *a, const void*b);
void runKruskals(int n, int m, edge *G);
void quickSort(edge *edges, int left, int right);


// main function that algorithm must implement from mst.h
void calculateMst(int n, int m, edge *G)
{
    T = (edge *)malloc((n-1)*sizeof(edge));

    makeUnionFind(n);
    //qsort(G, m, sizeof(edge), compareEdges);
    quickSort(G, 0, m-1);
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
        unionCCs(groupA, groupB);
        // TODO: make T pointers to elements of G? - dpi
        T[nextEdge].u = G[i].u;
        T[nextEdge].v = G[i].v;
        mstWeight += G[i].weight;
        nextEdge++;
    }
}

/*** union find functions ***/
inline void makeUnionFind(int n)
{
    // init parents
    /*parents = (UFCCNode *)malloc((n+1)*sizeof(UFCCNode));
    for (int i = 0; i < n+1; i++)
    {
        parents[i].parent = i;
        parents[i].size = 0;
        }*/
    parents = (int *)malloc((n+1)*sizeof(int));
    for (int i = 0; i < n+1; i++)
    parents[i] = i;
    
    /* todo dpi remove */
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
/*
void unionCCs(int a, int b)
{
    if (parents[a].size <= parents[b].size)
        setParent(a, b);
    else
        setParent(b, a);
}
// union helper func
inline void setParent(int a, int b)
{
    parents[a].parent = b;
    parents[b].size += parents[a].size;
}
inline int find(int u)
{
    while (parents[u].parent != u)
        u = parents[u].parent;
    return u;

}*/

inline void unionCCs(int a, int b)
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
}

inline int find(int u)
{
    return parents[u];
    }


void quickSort(edge *edges, int left, int right)
{
    int i, j;
    edge x, y;

    i = left;
    j = right;
    x = edges[(left+right)/2];

    do {
        while((edges[i].weight < x.weight) && (i < right))
            i++;
        while((x.weight < edges[j].weight) && (j > left))
            j--;

        if(i <= j) {
            y = edges[i];
            edges[i] = edges[j];
            edges[j] = y;
            i++; j--;
        }
    } while(i <= j);

    if(i < right)
        quickSort(edges, i, right);
    if(left < j)
        quickSort(edges, left, j);

}
