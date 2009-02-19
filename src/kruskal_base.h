#include <input/read_graph.h> /* read_graph */
#include <mst.h> /* edge, foi */
#include <input/pq_edge.h> /* pq_pop_min */
#include <sort.h> /* quicksort */
#include <stdio.h> /* printf */
#include <stdlib.h> /* malloc */

#define _PARTIAL_QUICK_
#ifdef _PARTIAL_QUICK_
int sortAmt;
int sortedThrough;
#endif

// runs kruskal's algorithm
void runKruskals(int n, int m, edge *G)
{
    // total weight of mst
    foi_big mstWeight;
    // array of edges in mst, T
    edge *T;
    T = (edge *)malloc((n-1)*sizeof(edge));

    int nextEdge = 0;
    mstWeight = 0;
    for (int i = 0; i < m && nextEdge < n-1; i++)
    {
        edge e;
#ifndef PARTIAL_SORT
        e = G[i];
#else
#ifdef _PARTIAL_QUICK_
        if (i >= sortedThrough)
        {
            int sortTo = sortedThrough + sortAmt;
            if (sortTo > m-1) {
                int left = sortedThrough+1;
                sortedThrough = m-1;
                quicksort(G, left, m-1);
            }
            else {
                int left = sortedThrough+1;
                sortedThrough += sortAmt;
                quicksortPart(G, left, m-1, sortedThrough);
            }
        }
        e = G[i];
#else
        e = pq_pop_min();
#endif
#endif
        int groupA = find(e.u);
        int groupB = find(e.v);
        // check if same CC
        if (groupA == groupB)
            continue;
        unionCCs(groupA, groupB);
        T[nextEdge].u = e.u;
        T[nextEdge].v = e.v;
        mstWeight += e.weight;
        nextEdge++;
    }

    printf("%f\n", FOI_TO_OUTPUT_WEIGHT(mstWeight));
    for (int i = 0; i < n-1; i++)
        printf("%d %d\n", T[i].u, T[i].v);
}

void kruskal(char* fn)
{
    int n, m;
    edge *G;
#ifndef PARTIAL_SORT
    read_graph_to_edge_list(fn, &n, &m, &G);
    quicksort(G, 0, m-1);
#else
#ifdef _PARTIAL_QUICK_
    read_graph_to_edge_list(fn, &n, &m, &G);
    int density = m/n;
    if (density >= 50)
    {
        float fraction = 0.1;
        if (n < fraction*m)
            sortAmt = fraction*m;
        else
            sortAmt = n;
        sortedThrough = sortAmt;
    }
    else if (density >= 10)
    {
        float fraction = 0.2;
        if (n < fraction*m)
            sortAmt = fraction*m;
        else
            sortAmt = n;
        sortedThrough = sortAmt;
    }
    else
    {
        sortAmt = m-1;
        sortedThrough = m-1;
    }
    quicksortPart(G, 0, m-1, sortAmt);
#else
    read_graph_to_heapified_edge_list(fn, &n, &m, &G);
#endif
#endif
    makeUnionFind(n);
    runKruskals(n, m, G);
}
