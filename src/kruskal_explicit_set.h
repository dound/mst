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
#define INIT_CC_CAP 4

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
        CCs[i].capacity = 1;
        CCs[i].size = 1;
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
        if (CCs[b].capacity == 1)
        {
            CCs[b].capacity = INIT_CC_CAP;
            CCs[b].vertices = (int *)malloc(INIT_CC_CAP * sizeof(int));
            CCs[b].vertices[0] = b;
        }
        else
        {
            CCs[b].capacity *= 2;
            CCs[b].vertices = (int *)realloc(CCs[b].vertices,
                                             CCs[b].capacity * sizeof(int));
        }
    }
    
    if (CCs[a].size == 1)
    {
        exp_parents[a] = b;
        CCs[b].vertices[CCs[b].size] = a;
        CCs[b].size++;
    }
    else
    {
        // set new parent values
        int i;
        for (i = 0; i < CCs[a].size; i++)
            exp_parents[CCs[a].vertices[i]] = b;
        
        // copy over values in set
        memcpy(CCs[b].vertices+CCs[b].size, CCs[a].vertices,
               CCs[a].size*sizeof(int));
        free(CCs[a].vertices);
        CCs[b].size += CCs[a].size;
    }
}

int find(int u)
{
    return exp_parents[u];
}
