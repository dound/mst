/**
 * Implicit set version of Kruskal's algorithm which maintains an implicit set
 * in the chained parent pointers.
 */

#include <kruskal_common.h> /* unionCCs, find */
#include <math.h> /* sqrt */
#include <stdlib.h> /* malloc */
#include <mst.h> /* edge, foi */

// a node in the tree that represents the connected component
typedef struct
{
    int size;
    int parent;
} UFCCNode;

// parents of vertices
UFCCNode *imp_parents;
// list and count of nodes whose parents pointers need to be updated
int *toUpdate;
int numToUpdate;

void set_parent_implicit(int group, int parent);


/*** union find functions ***/
void makeUnionFind(int n)
{
    imp_parents = (UFCCNode *)malloc((n+1)*sizeof(UFCCNode));
    int i;
    for (i = 0; i < n+1; i++)
    {
        imp_parents[i].parent = i;
        imp_parents[i].size = 0;
    }
    toUpdate = (int *)malloc((sqrt(n)+1)*sizeof(int));
}

/***** union-find code *****/
void unionCCs(int a, int b)
{
    if (imp_parents[a].size <= imp_parents[b].size)
        set_parent_implicit(a, b);
    else
        set_parent_implicit(b, a);
}

// union helper func
void set_parent_implicit(int a, int b)
{
    imp_parents[a].parent = b;
    imp_parents[b].size += imp_parents[a].size;
    int i;
    for (i = 0; i < numToUpdate; i++)
        imp_parents[toUpdate[i]].parent = b;
}

int find(int u)
{
    numToUpdate = 0;
    while (imp_parents[u].parent != u)
    {
        toUpdate[numToUpdate] = u;
        numToUpdate++;
        u = imp_parents[u].parent;
    }
    return u;
}
