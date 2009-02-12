// mst main

#include <stdio.h> /* printf */

#include <mst.h> /* edge */
#include <input/read_graph.h> /* read_graph */

/*** output data ***/
// total weight of mst
float mstWeight;
// array of edges in mst, T
edge *T;

int main(int argc, char **argv) {
    if (argc < 2)
    {
        printf("usage: ./mst <inputfile>\n");
        return 0;
    }

    int n, m;
    edge *G;
    read_graph_to_edge_list(argv[1], &n, &m, &G);
    calculateMst(n, m, G);
    printGraph(T, n-1, mstWeight);

    return 0;
}

// outputs graph
void printGraph(edge *G, int size, float weight)
{
    printf("%f\n", weight);
    for (int i = 0; i < size; i++)
    {
        printf("%d %d\n", G[i].u, G[i].v);
    }
}
