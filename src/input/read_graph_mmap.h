#include <stdio.h>  /* fopen, sscanf */
#include <sys/mman.h> /* mmap */
#include <sys/stat.h> /* fstat */
#include <stdlib.h> /* malloc */
#include <string.h> /* strchr */

#include <sys/types.h>
#include <fcntl.h>

// read input file, store results in n, m, and G
int read_graph_mmap(char *filename, int *n, int *m, edge **G)
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

    return 1;
}
