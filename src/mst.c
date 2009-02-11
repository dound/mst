// mst main

#include <stdio.h>
#include <malloc.h>
#include <string.h>
#include <stdlib.h>
#include <sys/types.h>
#include <sys/stat.h>
#include <sys/mman.h>
#include <fcntl.h>
#include "mst.h"


/*** output data ***/
// total weight of mst
float mstWeight;
// array of edges in mst, T
edge *T;


bool readG(char *filename, int *n, int *m, edge **G);
bool readG2(char *filename, int *n, int *m, edge **G);


int main(int argc, char **argv) {
    if (argc < 2)
    {
        printf("usage: ./mst <inputfile>\n");
        return 0;
    }

    int n, m;
    edge *G;
    readG2(argv[1], &n, &m, &G);
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

// read input file, store results in n, m, and G
bool readG2(char *filename, int *n, int *m, edge **G)
{
    struct stat sb;

    int fd = open(filename, O_RDONLY);
    if (fstat (fd, &sb) == -1) {
        perror ("fstat");
        return 1;
    }
    
    char *start = (char *)mmap(0, sb.st_size, PROT_READ, MAP_SHARED, fd,
                               0);
    if (start == MAP_FAILED) {
        perror ("mmap");
        return 1;
    }
    char *input = start;
    // todo dpi remove = char *end = start + sb.st_size;
    char *delim;
    delim = strchr(input, '\n');
    sscanf(input, "%d", n);
    input = delim+1;
    delim = strchr(input, '\n');
    sscanf(input, "%d", m);
    input = delim+1;

    *G = (edge *)malloc((*m)*sizeof(edge));
    memset(*G, 0, (*m)*sizeof(edge));

    int i = 0;
    for (i = 0; i < *m; i++)
    {
        /*** parse u ***/
        delim = strchr(input, ' ');
        int pwr = 1;
        char *digit = delim-1;
        while (digit >= input)
        {
            (*G)[i].u += pwr*((*digit)-'0');
            pwr *= 10;
            digit--;
        }
        /*** parse v ***/
        input = delim+1;
        delim = strchr(input, ' ');
        pwr = 1;
        digit = delim-1;
        while (digit >= input)
        {
            (*G)[i].v += pwr*((*digit)-'0');
            pwr *= 10;
            digit--;
        }
        /*** parse weight ***/
        pwr = 1;
        input = delim+1;
        delim = strchr(input, '\n');
        char *decimal = strchr(input, '.');
        if (decimal == 0 || decimal > delim)
            decimal = delim;
        digit = decimal-1;
        while (digit >= input)
        {
            (*G)[i].weight += pwr*((*digit)-'0');
            pwr *= 10;
            digit--;
        }
        digit = decimal+1;
        float pwr2 = 1.0/10;
        while (digit < delim)
        {
            (*G)[i].weight += pwr2*((*digit)-'0');
            pwr2 /= 10;
            digit++;
        }
        input = delim+1;
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
