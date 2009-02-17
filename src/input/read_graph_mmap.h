#include <fcntl.h> /* O_RDONLY */
#include <stdio.h>  /* fopen, sscanf */
#include <sys/mman.h> /* mmap */
#include <sys/stat.h> /* fstat */
#include <string.h> /* memset, strchr */
#include <input/adj_matrix.h> /* AM_INDEX */
#include <input/initialize_graph.h> /* initialize_* */
#include <input/pq_edge.h> /* pq_* */
#include <input/read_graph.h>
#include <mst.h> /* edge, foi */

// read input file, store results in n, m, and G
#if   GRAPH_TYPE == EDGE_LIST
int read_graph_to_edge_list_mmap(char *filename, int *n, int *m, edge **G)
#elif   GRAPH_TYPE == HEAPIFIED_EDGE_LIST
int read_graph_to_heapified_edge_list_mmap(char *filename, int *n, int *m, edge **G)
#elif GRAPH_TYPE == ADJACENCY_LIST
int read_graph_to_adjacency_list_mmap(char *filename, int *n, int *m, void **G)
#elif GRAPH_TYPE == ADJACENCY_MATRIX
int read_graph_to_adjacency_matrix_mmap(char *filename, int *n, int *m, foi **weights)
#else
#  error unknown GRAPH_TYPE
#endif
{
    struct stat sb;

    int fd = open(filename, O_RDONLY);
    if (fstat (fd, &sb) == -1) {
        perror ("fstat");
        return 0;
    }

    char *start = (char *)mmap(0, sb.st_size, PROT_READ, MAP_SHARED, fd,
                               0);
    if (start == MAP_FAILED) {
        perror ("mmap");
        return 0;
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

#if   GRAPH_TYPE == EDGE_LIST
    initialize_edge_list(G, *m);
    memset(*G, 0, (*m)*sizeof(edge));
#elif GRAPH_TYPE == HEAPIFIED_EDGE_LIST
    pq_init(*m);
    *G = pq;
    memset(*G, 0, (*m + 1)*sizeof(edge));
#elif GRAPH_TYPE == ADJACENCY_LIST
    initialize_adjacency_list(G, *n);
#elif GRAPH_TYPE == ADJACENCY_MATRIX
    initialize_adjacency_matrix(weights, *n);
    int u, v;
    foi w;
#endif
#ifdef _NO_FLOATS_
    int tmp;
#endif

    int i = 0;
#if GRAPH_TYPE == HEAPIFIED_EDGE_LIST
    for (i = 1; i < *m+1; i++)
#else
    for (i = 0; i < *m; i++)
#endif
    {
#if GRAPH_TYPE == ADJACENCY_MATRIX
        u = v = 0;
        w = 0.0f;
#endif
        /*** parse u ***/
        delim = strchr(input, ' ');
        int pwr = 1;
        char *digit = delim-1;
        while (digit >= input)
        {
#if   GRAPH_TYPE == EDGE_LIST || GRAPH_TYPE == HEAPIFIED_EDGE_LIST
            (*G)[i].u += pwr*((*digit)-'0');
#elif GRAPH_TYPE == ADJACENCY_MATRIX
            u += pwr*((*digit)-'0');
#endif
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
#if   GRAPH_TYPE == EDGE_LIST || GRAPH_TYPE == HEAPIFIED_EDGE_LIST
            (*G)[i].v += pwr*((*digit)-'0');
#elif GRAPH_TYPE == ADJACENCY_MATRIX
            v += pwr*((*digit)-'0');
#endif
            pwr *= 10;
            digit--;
        }
        /*** parse weight ***/
#ifdef _NO_FLOAT_
#   error _NO_FLOAT_ is not yet supported by read_graph_*_mmap()
#endif
        pwr = 1;
        input = delim+1;
        delim = strchr(input, '\n');
        char *decimal = strchr(input, '.');
        if (decimal == 0 || decimal > delim)
            decimal = delim;
        digit = decimal-1;
        while (digit >= input)
        {
#if   GRAPH_TYPE == EDGE_LIST || GRAPH_TYPE == HEAPIFIED_EDGE_LIST
            (*G)[i].weight += pwr*((*digit)-'0');
#elif GRAPH_TYPE == ADJACENCY_MATRIX
            w += pwr*((*digit)-'0');
#endif
            pwr *= 10;
            digit--;
        }
        digit = decimal+1;
        float pwr2 = 1.0/10;
        while (digit < delim)
        {
#if   GRAPH_TYPE == EDGE_LIST || GRAPH_TYPE == HEAPIFIED_EDGE_LIST
            (*G)[i].weight += pwr2*((*digit)-'0');
#elif GRAPH_TYPE == ADJACENCY_MATRIX
            w += pwr2*((*digit)-'0');
#endif
            pwr2 /= 10;
            digit++;
        }
        input = delim+1;
#if GRAPH_TYPE == ADJACENCY_MATRIX
        (*weights)[AM_INDEX(*n, u, v)] = w;
#endif
#if GRAPH_TYPE == HEAPIFIED_EDGE_LIST
        pq_heapify_insertion(); /* maintain the heap property */
#endif
    }

    return 1;
}
