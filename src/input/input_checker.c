#include <stdio.h> /* fclose, fopen, fprintf, sprintf */
#include <stdlib.h> /* system */
#include <string.h> /* strcmp */
#include <unistd.h> /* unlink */
#include <input/adj_list.h> /* edge_list, AL_EDGE_LIST_* */
#include <input/adj_matrix.h> /* AM_WEIGHT_FAST, AM_NO_EDGE */
#include <input/pq_edge.h> /* pq_* */
#include <input/read_graph.h> /* read_graph */
#include <mst.h> /* edge, foi */

/* where checker will store temporary outputs */
#define TMP_OUT ".input_checker_out.tmp"
#define TMP_OUT2 ".input_checker_out.tmp2"

/* diff to exclude lines which start with a hash mark, if present */
#define DIFF_CMD "diff -I '^#'"

/**
 * Reads a graph from fn.  The graph is printed back out and then checked to see
 * if it is identical to the input file using diff unless read_only is specified.
 */
int check_input(char* fn, int read_only, int graph_type);

int main(int argc, char **argv) {
    int read_only=0;
    int edge_list=0, heapified_edge_list=0, adjacency_list=0, adjacency_matrix=0;

    if(argc < 2 || argc > 6) {
        fprintf(stderr, "usage: %s <inputfile> [-r] [el] [hel] [al] [am]\n", argv[0]);
        return -1;
    }
    int argc_on = 2;
    while(argc_on > 0 && argc_on < argc) {
        if(strcmp("el", argv[argc_on])==0)
            edge_list = 1;
        else if(strcmp("hel", argv[argc_on])==0)
            heapified_edge_list = 1;
        else if(strcmp("al", argv[argc_on])==0)
            adjacency_list = 1;
        else if(strcmp("am", argv[argc_on])==0)
            adjacency_matrix = 1;
        else if(strcmp("-r", argv[argc_on])==0)
            read_only = 1;
        else {
            fprintf(stderr, "unknown argument %s\n", argv[argc_on]);
            return -1;
        }
        argc_on += 1;
    }

    int do_all = (!edge_list && !heapified_edge_list && !adjacency_list && !adjacency_matrix);
    int ret = 1;
    if(do_all || edge_list)
        ret = ret && check_input(argv[1], read_only, EDGE_LIST)==0;
    if(do_all || heapified_edge_list)
        ret = ret && check_input(argv[1], read_only, HEAPIFIED_EDGE_LIST)==0;
    if(do_all || adjacency_list)
        ret = ret && check_input(argv[1], read_only, ADJACENCY_LIST)==0;
    if(do_all || adjacency_matrix)
        ret = ret && check_input(argv[1], read_only, ADJACENCY_MATRIX)==0;
    return ret;
}

int check_input(char* fn, int read_only, int graph_type) {
    char* str_graph_type;
    char* fn_to_diff = fn;

    /* read in the graph */
    int n, m;
    void *VG;
    switch(graph_type) {
    case EDGE_LIST:
        str_graph_type = "EL";
        if(!read_graph_to_edge_list(fn, &n, &m, (edge**)&VG)) {
            fprintf(stderr, "%s ERROR: failed to read in graph: %s\n", str_graph_type, fn);
            return -1;
        }
        break;
    case HEAPIFIED_EDGE_LIST:
        str_graph_type = "HEL";
        if(!read_graph_to_heapified_edge_list(fn, &n, &m, (edge**)&VG)) {
            fprintf(stderr, "%s ERROR: failed to read in graph: %s\n", str_graph_type, fn);
            return -1;
        }
        break;
    case ADJACENCY_LIST:
        str_graph_type = "AL";
        if(!read_graph_to_adjacency_list(fn, &n, &m, (edge_list**)&VG)) {
            fprintf(stderr, "%s ERROR: failed to read in graph: %s\n", str_graph_type, fn);
            return -1;
        }
        break;
    case ADJACENCY_MATRIX:
        str_graph_type = "AM";
        if(!read_graph_to_adjacency_matrix(fn, &n, &m, (foi**)&VG)) {
            fprintf(stderr, "%s ERROR: failed to read in graph: %s\n", str_graph_type, fn);
            return -1;
        }
        break;
    default:
        str_graph_type = "???";
    }

    /* stop if we were only supposed to read the graph */
    if(read_only) {
        fprintf(stdout, "%s read only successful: %s\n", str_graph_type, fn);
        return 0;
    }

    /* write out the graph */
    FILE *out = fopen(TMP_OUT, "w");
    if(!out) {
        fprintf(stderr, "FAILED to open %s for writing\n", TMP_OUT);
        return -1;
    }
    fprintf(out, "%d\n%d\n", n, m);
    switch(graph_type) {
    case EDGE_LIST: {
        edge *G = (edge*)VG;
        for(int i=0; i<m; i++)
            fprintf(out, "%d %d %.1f\n", G[i].u, G[i].v, FOI_TO_OUTPUT_WEIGHT(G[i].weight));
        break;
    }
    case HEAPIFIED_EDGE_LIST: {
        edge e;
        for(int i=0; i<m; i++) {
            e = pq_pop_min();
            fprintf(out, "%d %d %.1f\n", e.u, e.v, FOI_TO_OUTPUT_WEIGHT(e.weight));
        }
        break;
    }
    case ADJACENCY_LIST: {
        edge_list *pel = ((edge_list*)VG) + 1; /* first vertex is at offset 1 */
        edge_to *pe;
        for(int i=1; i<=n; i++) {
            AL_EDGE_LIST_BEGIN(pel);
            pe = AL_EDGE_LIST_GET(pel);
            while(pe) {
                /* we have two copies of each edge, so just print the first copy */
                if(pe->other > i)
                    fprintf(out, "%d %d %.1f\n", i, pe->other, FOI_TO_OUTPUT_WEIGHT(pe->weight));
                AL_EDGE_LIST_NEXT();
                pe = AL_EDGE_LIST_GET(pel);
            }
            pel += 1; /* go to the next vertex's edge list */
        }
        break;
        break;
    }
    case ADJACENCY_MATRIX: {
        foi *weights = (foi*)VG;
        foi w;
        for(int i=1; i<=n; i++) {
            for(int j=i+1; j<=n; j++) {
                w = AM_WEIGHT_FAST(weights, n, i, j);
                if(w != AM_NO_EDGE)
                    fprintf(out, "%d %d %.1f\n", i, j, FOI_TO_OUTPUT_WEIGHT(w));
            }
        }
        break;
    }
    }
    fclose(out);

    /* need to sort input/output since edge order does not matter */
    char cmd[1024];
    int ret;
    if(graph_type != EDGE_LIST) { /* order will be fine for edge list */
        snprintf(cmd, 1024, "./input/sort_and_order.py %s > .tmp", TMP_OUT);
        ret = (system(cmd)==0);
        snprintf(cmd, 1024, "mv .tmp %s", TMP_OUT);
        ret = (system(cmd)==0);

        snprintf(cmd, 1024, "./input/sort_and_order.py %s > .tmp", fn);
        ret = (ret && system(cmd)==0);
        fn_to_diff = TMP_OUT2;
        snprintf(cmd, 1024, "mv .tmp %s", fn_to_diff);
        ret = (ret && system(cmd)==0);

        if(!ret) {
            fprintf(stderr, "sorting failed\n");
            return -1;
        }
    }

    /* diff it */
    snprintf(cmd, 1024, "%s %s %s", DIFF_CMD, fn_to_diff, TMP_OUT);
    ret = system(cmd);
    if(ret != 0)
        fprintf(stderr, "%s ERROR: output does not match: %s\n", str_graph_type, fn);
    else
        fprintf(stdout, "%s output is correct: %s\n", str_graph_type, fn);

    unlink(TMP_OUT);
    unlink(TMP_OUT2);
    return ret;
}
