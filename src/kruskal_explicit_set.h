/**
 * Explicit set version of Kruskal's algorithm which maintains the explicit set
 * of elements in the connected component.
 */

#include <assert.h> /* assert */
#include <kruskal_common.h> /* unionCCs, find */
#include <mst.h> /* edge, foi */
#include <stdlib.h> /* free, malloc */
#include <string.h> /* memcpy */

// in EXPLICIT_SET version, initial size of each set to malloc
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


// sets of connected components
UFSet *CCs;
// parents of vertices
int *exp_parents;


void set_parent_explicit(int group, int parent);


/*** union find functions ***/
void makeUnionFind(int n)
{
    int i;
    exp_parents = (int *)malloc((n+1)*sizeof(int));
    for (i = 0; i < n+1; i++)
        exp_parents[i] = i;

    CCs = (UFSet *)malloc((n+1)*sizeof(UFSet));
    for (i = 0; i < n+1; i++)
    {
        CCs[i].vertices = (int *)malloc(INIT_CC_CAP*sizeof(int));
        assert(CCs[i].vertices);
        CCs[i].capacity = INIT_CC_CAP;
        CCs[i].size = 1;
        CCs[i].vertices[0] = i;
    }
}

/***** union-find code *****/
void unionCCs(int a, int b)
{
    if (CCs[a].size <= CCs[b].size)
        set_parent_explicit(a, b);
    else
        set_parent_explicit(b, a);
}

// union helper func
void set_parent_explicit(int a, int b)
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
    int i;
    for (i = 0; i < CCs[a].size; i++)
        exp_parents[CCs[a].vertices[i]] = b;

    // copy over values in set
    memcpy(CCs[b].vertices+CCs[b].size, CCs[a].vertices, CCs[a].size*sizeof(int));
    free(CCs[a].vertices);
    CCs[b].size += CCs[a].size;
}

int find(int u)
{
    return exp_parents[u];
}
