#ifndef ADJ_LIST_H
#define ADJ_LIST_H

#include <assert.h> /* assert */
#include <mst.h> /* foi */
#include <stdlib.h> /* malloc, realloc */

typedef struct {
    int other;  /* index of the other vertex */
    foi weight; /* weight to get the other vertex */
} edge_to;

#ifdef ADJ_LIST_WITH_VECTORS

typedef struct {
    edge_to *a;
    unsigned used;
    unsigned avail;
} edge_list;

/** adds an edge to an edge_list (assumes memory allocation, if needed, does not fail) */
#define AL_EDGE_LIST_ADD(pel, v, w) if((pel)->used >= (pel)->avail) { \
                                        (pel)->avail *= 2; \
                                        (pel)->a = realloc((pel)->a, (pel)->avail * sizeof(edge_to)); \
                                        assert((pel)->a); \
                                    } \
                                    (pel)->a[(pel)->used].other = v; \
                                    (pel)->a[(pel)->used].weight = w; \
                                    (pel)->used += 1;

/** initializes a (local) iterator for an edge_list */
#define AL_EDGE_LIST_BEGIN(pel) int __itr_edge_list = 0

/** returns a pointer to the next edge in the edge_list, or NULL if there are no more edges */
#define AL_EDGE_LIST_GET(pel) ((__itr_edge_list<(pel)->used) ? &((pel)->a[__itr_edge_list]) : NULL)

/** advances the iterator to the next edge */
#define AL_EDGE_LIST_NEXT() __itr_edge_list += 1

#else /* adjacency list with linked-lists of edges */

typedef struct edge_list_item {
    edge_to e;
    struct edge_list_item *next;
} edge_list_item;

typedef struct {
    edge_list_item* head;
} edge_list;

#define AL_EDGE_LIST_ADD(pel, v, w) { edge_list_item *c = malloc(sizeof(edge_list_item)); \
                                      assert(c); \
                                      c->e.other = v; \
                                      c->e.weight = w; \
                                      c->next = (pel)->head; \
                                      (pel)->head = c; }

#define AL_EDGE_LIST_BEGIN(pel) edge_list_item *__itr_edge_list = (pel)->head

#define AL_EDGE_LIST_GET(pel) &(__itr_edge_list->e)

#define AL_EDGE_LIST_NEXT() __itr_edge_list = __itr_edge_list->next

#endif

#endif /* ADJ_LIST_H */
