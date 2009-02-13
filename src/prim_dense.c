#include <input/adj_matrix.h> /* FLOAT_MAX, AM_INDEX_NO_ADJ */
#include <input/read_graph.h> /* read_graph */
#include <stdio.h> /* printf */
#include <stdlib.h> /* malloc */
#include <string.h> /* memset */

/**
 * Uses Prim's algorithm to find the MST of the specified graph.  Prints the MST
 * to stdout.
 *
 * This simple implementation is optimized for very dense graphs.  It should run
 * in time linear in the number of vertices.  It will *not* perform well on
 * sparse graphs.
 *
 * @param sz_v     number of vertices in the graph
 * @param weights  adjacency matrix of edge weights
 */
void run_prim_dense(int sz_v, float *weights) {\
    /* IMPORTANT: all vertices are 0 indexed (i.e., one off from actual input #s) */
    float mst_weight = 0;

    /** Whether a vertex is NOT in the MST.  Offset 0 unused. */
    char *vertex_not_done = (char*)malloc(sz_v * sizeof(char));
    memset(vertex_not_done, 1, sz_v * sizeof(char));

    /* Value at offset u specifies v.  v is the other endpoint of the edge
     * which connects u to the MST.  Offset 0 is not used. */
    unsigned *mst_edges  = (unsigned*)malloc(sz_v * sizeof(unsigned));

    /* store the best known weight to each vertex (initially infinite) */
    float   *min_w_to_v = (float*)malloc(sz_v * sizeof(float));
    for(int i=0; i<sz_v; i++)
        min_w_to_v[i] = FLOAT_MAX;

    /* node most recently added to the MST */
    unsigned latest_vertex = 0;

    /* next vertex to add to the MST */
    unsigned next_vertex;

    /* loop until we have an MST */
    float w;
    while(1) {
        /* will be replaced by next vertex since min_w_to_v[0] is FLOAT_MAX */
        next_vertex = 0;

        /* find the minimum edge to each node (ignore vertex 0 as it starts our MST) */
        for(int v=1; v<sz_v; v++) {
            if(vertex_not_done[v]) {
                /* get cost to v from the latest vertex added to the MST */
                /* note: if there is no such edge, w will be FLOAT_MAX: this
                 * means we don't need an extra test to see if such an edge exists! */
                w = weights[AM_INDEX_NO_ADJ(sz_v, latest_vertex, v)];

                /* update the cost to get to v if it is shorter through latest_vertex */
                if(w < min_w_to_v[v]) {
                    min_w_to_v[v] = w;              /* remember best cost to v */
                    mst_edges[v] = latest_vertex;   /* remember parent of v */
                }

                /* see if the best edge to v is the shortest edge from from the
                 * current connected compon to a non-connected vertex (e.g., v) */
                if(min_w_to_v[v] < min_w_to_v[next_vertex])
                    next_vertex = v;
            }
        }

        if(next_vertex) {
            mst_weight += min_w_to_v[next_vertex];
            vertex_not_done[next_vertex] = 0;
            latest_vertex = next_vertex;
        }
        else
            break;
    }

    /* print the MST */
    printf("%f\n", mst_weight);
    for(int i=1; i<sz_v; i++)
        printf("%d %d\n", i, mst_edges[i]);

#ifdef _DEBUG_
    /* be nice and free memory when we aren't going for performance */
    free(vertex_not_done);
    free(mst_edges);
    free(min_w_to_v);
#endif
}

/** read in the graph and call run_prim_dense */
void prim_dense(char* fn) {
    int n, m;
    float *weights;
    read_graph_to_adjacency_matrix(fn, &n, &m, &weights);
    run_prim_dense(n, weights);
}
