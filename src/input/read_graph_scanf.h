#include <stdio.h>  /* fopen, fscanf */
#include <stdlib.h> /* malloc */

// read input file, store results in n, m, and G
int read_graph_scanf(char *filename, int *n, int *m, edge **G)
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
            return 0;
        }
    }

    return 1;
}
