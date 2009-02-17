/** Interface to a static priority queue. */
#ifndef PQ_EDGE_H
#define PQ_EDGE_H

#include <mst.h> /* edge */

/** static priority queue these methods operate on */
extern edge *pq;

/** initialize the PQ */
void pq_init(unsigned maxN);

/** check to see if the PQ is empty */
unsigned pq_empty();

/** add a new edge to the PQ */
void pq_insert(edge v);

/** use the edge in pq[N] as a new edge to add to the PQ */
void pq_heapify_insertion();

/** remove the edge with the minimum weight from the PQ */
edge pq_pop_min();

#endif /* PQ_EDGE_H */
