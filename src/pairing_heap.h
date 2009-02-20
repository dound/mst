/** interface to a heap */
#ifndef PAIRING_HEAP
#define PAIRING_HEAP

#include <mst.h> /* foi */

typedef struct {
    int v_in_mst, v_not_in_mst;
    foi weight;
} heap_value;

typedef struct heap_node {
    struct heap_node *parent;
    struct heap_node *next_sibling;
    struct heap_node *previous_sibling;
    struct heap_node *first_child;
    struct heap_node *last_child;
    heap_value value;
    int n_subtrees;
} heap_node;

typedef struct heap {
    heap_node * root;
} heap;

/* create a new heap */
heap* heap_new();

/* free heap */
void heap_free();

/* get min value */
int heap_min();

/* decrease the value of the node */
void heap_decrease_key(heap_node *node, foi new_weight);

/* insert element to the heap */
heap_node *heap_insert(foi weight);

/* delete min value. multi-pass */
void heap_delete_min();

#endif /* PAIRING_HEAP */
