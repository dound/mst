// mst main

#include <stdio.h>
#include <malloc.h>
#include "mst.h"


/*** output data ***/
// total weight of mst
float mstWeight;
// array of edges in mst, T
edge *T;


bool readG(char *filename, int *n, int *m, edge **G);


int main(int argc, char **argv) {
    if (argc < 2)
    {
        printf("usage: ./mst <inputfile>\n");
        return 0;
    }

    int n, m;
    edge *G;
    readG(argv[1], &n, &m, &G);
    calculateMst(n, m, G);
    printGraph(T, n-1, mstWeight);

    return 0;
}

// read input file, store results in n, m, and G
bool readG(char *filename, int *n, int *m, edge **G)
{
    FILE *input = fopen(filename, "r");
    fscanf(input, "%d", n);
    fscanf(input, "%d", m);

    *G = (edge *)malloc((*m)*sizeof(edge));

    int i = 0;
    int charsRead = 1;
    for (i = 0; i < *m; i++)
    {
        charsRead = fscanf(input, "%d %d %f",
                           &(*G)[i].u, &(*G)[i].v, &(*G)[i].weight);
        if (charsRead == EOF) {
            printf("premature EOF in input\n");
            return false;
        }
    }

    return true;
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
