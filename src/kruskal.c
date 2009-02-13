// Implement's Kruskal's algorithm

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <assert.h>
#include <math.h>
#include <input/read_graph.h> /* read_graph */
#include <mst.h> /* edge, foi */

// the EXPLICIT_SET version maintains the set of elements in the connected
// component while the other version maintains an implicit set in
// the chained parent pointers
#define EXPLICIT_SET

// in EXPLICIT_SET version, initial size of each set to malloc
#define INIT_CC_CAP 2


#ifdef EXPLICIT_SET
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

#else
// a node in the tree that represents the connected component
typedef struct
{
    int size;
    int parent;
} UFCCNode;
#endif


#ifdef EXPLICIT_SET
// sets of connected components
UFSet *CCs;
// parents of vertices
int *parents;

#else
// parents of vertices
UFCCNode *parents;
// list and count of nodes whose parents pointers need to be updated
int *toUpdate;
int numToUpdate;
#endif


void makeUnionFind(int n);
void unionCCs(int a, int b);
void setParent(int group, int parent);
int find(int u);
int compareEdges(const void *a, const void*b);
void runKruskals(int n, int m, edge *G);
void quickSort(edge *edges, int left, int right);


// main function that algorithm must implement from mst.h
void kruskal(char* fn)
{
    int n, m;
    edge *G;
    read_graph_to_edge_list(fn, &n, &m, &G);

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
    // total weight of mst
    foi mstWeight;
    // array of edges in mst, T
    edge *T;
    T = (edge *)malloc((n-1)*sizeof(edge));

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

    printf("%f\n", FOI_TO_OUTPUT_WEIGHT(mstWeight));
    for (int i = 0; i < n-1; i++)
        printf("%d %d\n", T[i].u, T[i].v);
}

/*** union find functions ***/
void makeUnionFind(int n)
{
#ifdef EXPLICIT_SET
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

#else
    parents = (UFCCNode *)malloc((n+1)*sizeof(UFCCNode));
    for (int i = 0; i < n+1; i++)
    {
        parents[i].parent = i;
        parents[i].size = 0;
    }
    toUpdate = (int *)malloc((sqrt(n)+1)*sizeof(int));
#endif
}

/***** union-find code *****/
#ifdef EXPLICIT_SET
void unionCCs(int a, int b)
{
    if (CCs[a].size <= CCs[b].size)
        setParent(a, b);
    else
        setParent(b, a);
}

// union helper func
void setParent(int a, int b)
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

int find(int u)
{
    return parents[u];
}

#else
void unionCCs(int a, int b)
{
    if (parents[a].size <= parents[b].size)
        setParent(a, b);
    else
        setParent(b, a);
}

// union helper func
void setParent(int a, int b)
{
    parents[a].parent = b;
    parents[b].size += parents[a].size;
    for (int i = 0; i < numToUpdate; i++)
        parents[toUpdate[i]].parent = b;
}

int find(int u)
{
    numToUpdate = 0;
    while (parents[u].parent != u)
    {
        toUpdate[numToUpdate] = u;
        numToUpdate++;
        u = parents[u].parent;
    }
    return u;
}
#endif

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
