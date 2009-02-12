#include <stdio.h> /* fclose, fopen, fprintf, sprintf */
#include <stdlib.h> /* system */
#include <string.h> /* strcmp */
#include <unistd.h> /* unlink */
#include <input/read_graph.h> /* read_graph */

/* where checker will store temporary outputs */
#define TMP_OUT ".input_checker_out.tmp"

/* diff to exclude lines which start with a hash mark, if present */
#define DIFF_CMD "diff -I '^#'"

/**
 * Reads a graph from fn.  The graph is printed back out and then checked to see
 * if it is identical to the input file using diff unless read_only is specified.
 */
int check_input(char* fn, int read_only);

int main(int argc, char **argv) {
    int read_only;

    if(argc < 2 || argc > 3) {
        fprintf(stderr, "usage: %s <inputfile> [-r]\n", argv[0]);
        return -1;
    }
    else if(argc == 3) {
        read_only = (strcmp("-r", argv[2])==0);
        if(!read_only) {
            fprintf(stderr, "second argument must be -r if supplied\n");
            return -1;
        }
    }
    else
        read_only = 0;

    return check_input(argv[1], read_only);
}

int check_input(char* fn, int read_only) {
    /* read in the graph */
    int n, m;
    edge *G;
    if(!read_graph(fn, &n, &m, &G)) {
        fprintf(stderr, "ERROR: failed to read in graph: %s\n", fn);
        return -1;
    }
    else if(read_only) {
        fprintf(stdout, "read only successful: %s\n", fn);
        return 0;
    }

    /* write out the graph */
    FILE *out = fopen(TMP_OUT, "w");
    if(!out) {
        fprintf(stderr, "FAILED to open %s for writing\n", TMP_OUT);
        return -1;
    }
    fprintf(out, "%d\n%d\n", n, m);
    for(int i=0; i<m; i++)
        fprintf(out, "%d %d %.1f\n", G[i].u, G[i].v, G[i].weight);
    fclose(out);

    /* diff it */
    char cmd[1024];
    snprintf(cmd, 1024, "%s %s %s", DIFF_CMD, fn, TMP_OUT);
    int ret = system(cmd);
    if(ret != 0)
        fprintf(stderr, "ERROR: output does not match: %s\n", fn);
    else
        fprintf(stdout, "output is correct: %s\n", fn);

    unlink(TMP_OUT);
    return ret;
}
