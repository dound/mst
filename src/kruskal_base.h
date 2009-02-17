#include <input/read_graph.h> /* read_graph */
#include <mst.h> /* edge, foi */
#include <sort.h> /* quicksort */
#include <stdio.h> /* printf */
#include <stdlib.h> /* malloc */

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

void kruskal(char* fn)
{
    int n, m;
    edge *G;
    read_graph_to_edge_list(fn, &n, &m, &G);

    makeUnionFind(n);
    quicksort(G, 0, m-1);
    runKruskals(n, m, G);
}
