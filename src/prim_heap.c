#include <input/adj_list.h> /* edge_to, AL_EDGE_LIST_* */
#include <input/read_graph.h> /* read_graph */
#include <mst.h> /* foi */
#include <pairing_heap.h> /* heap_* */
#include <stdio.h> /* printf */
#include <stdlib.h> /* malloc */
#include <string.h> /* memset */

/**
 * Uses Prim's algorithm to find the MST of the specified graph.  Prints the MST
 * to stdout.
 *
 * This implementation should work well over a wide range of graphs.
 *
 * @param sz_v  number of vertices in the graph
 * @param al    adjacency list
 */
void run_prim_heap(int sz_v, edge_list *al) {
    foi_big mst_weight = 0;

    /* a heap to remember the next shortest edge to a vertex not on the MST */
    heap *ph = heap_new(sz_v);

    /* Value at offset u specifies v.  v is the other endpoint of the edge
     * which connects u to the MST.  Offset 0 and 1 are not used. */
    unsigned *mst_edges  = (unsigned*)malloc((sz_v+1) * sizeof(unsigned));
    memset(mst_edges, 0, (sz_v+1) * sizeof(unsigned));

    /* space to store the best known edge to each vertex (ignore offset 0) */
    heap_node **min_edge_to_vertex = (heap_node**)malloc((sz_v+1) * sizeof(heap_node*));
    memset(min_edge_to_vertex, 0, (sz_v+1) * sizeof(heap_node*));

    /* start with vertex 1 in the MST */
    int v = 1;

    /* since vertex 1 starts in the MST it needs no edge to get to the MST */
    min_edge_to_vertex[1] = (heap_node*)-1;
    mst_edges[1] = -1;

    /* expand our territory one vertex per loop */
    do {
        /* see if edges from v might be useful for our MST */
        AL_EDGE_LIST_BEGIN(&al[v]);
        edge_to *e;
        while( (e=AL_EDGE_LIST_GET(&al[v])) ) {
            heap_node *min_edge = min_edge_to_vertex[e->other];
            if(!min_edge) {
                /* first edge to e->other! */
                min_edge_to_vertex[e->other] = heap_insert(e->weight);
                min_edge_to_vertex[e->other]->value.v_not_in_mst = e->other;
                min_edge_to_vertex[e->other]->value.v_in_mst = v;
            }
            else if(!mst_edges[e->other]) {
                /* already have an edge to e->other but it is NOT in the MST yet */
                /* is this one better? */
                if(min_edge->value.weight > e->weight) {
                    /* replace the edge with this better edge */
                    heap_decrease_key(min_edge, e->weight);
                    min_edge->value.v_in_mst = v;
                }
            }

            AL_EDGE_LIST_NEXT();
        }

        /* get the next vertex to process, if any */
        if(ph->root) {
            v = heap_min(); /* gets v_not_in_mst */

            /* add v to our MST - use the best edge we have to it */
            mst_edges[v] = min_edge_to_vertex[v]->value.v_in_mst;
            mst_weight += min_edge_to_vertex[v]->value.weight;
            heap_delete_min();
        }
        else
            break; /* loop until the heap is empty */
    }
    while(1);

    /* print the MST */
    printf("%f\n", FOI_TO_OUTPUT_WEIGHT(mst_weight));
    int i = 0;
    for(i=2; i<=sz_v; i++)
        printf("%d %u\n", i, mst_edges[i]);

#ifdef _DEBUG_
    /* be nice and free memory when we aren't going for performance */
    heap_free();
    free(mst_edges);
    free(min_edge_to_vertex);
#endif
}

/** read in the graph and call run_prim_dense */
void prim_heap(char* fn) {
    int n, m;
    edge_list *al;
    read_graph_to_adjacency_list(fn, &n, &m, &al);
    run_prim_heap(n, al);
}
