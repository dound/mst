/** implements a multipass pairing heap */
#include <pairing_heap.h>
#include <stdlib.h>

heap* hp;
heap_node* hnodes;
int hnode_on;

/***********************************************
 * PRIVATE FUNCTIONS
 ***********************************************/

/* link two node trees */
static heap_node* heap_node_meld(heap_node *small, heap_node *big) {
    heap_node *tmp;

    if (!small) return big;

    if (small->value.weight > big->value.weight) {
        tmp=small; small=big; big=tmp;
    }

    big->parent = small; /* small becomes the partent of big */
    if (small->first_child) { /* if small has children */
        big->next_sibling = small->first_child; /* big has a new sibling */
        big->next_sibling->previous_sibling = big; /* big is the new sibling of someone*/
    } else { /* big is to be only child */
        small->last_child = big; /* big is the last child of small */
    }
    small->first_child = big; /* big is the first child of small */

    return small;
}

/* isolate node from parent and siblings */
static void heap_node_isolate(heap_node *node) {
    heap_node *prev_tmp,*next_tmp;

    prev_tmp = node->previous_sibling;
    next_tmp = node->next_sibling;

    /* remove */
    node->previous_sibling = NULL;
    if (prev_tmp) prev_tmp->next_sibling=next_tmp;
    else if (node->parent) node->parent->first_child=next_tmp;

    node->next_sibling=NULL;
    if (next_tmp) next_tmp->previous_sibling=prev_tmp;
    else if (node->parent) node->parent->last_child=prev_tmp;

    node->parent=NULL;
}

/* create a new node */
static heap_node* heap_node_new(foi weight) {
    heap_node *h;

    h = &hnodes[hnode_on++];
    /* if you want speed, use memset instead */
    h->parent = NULL;
    h->previous_sibling = NULL;
    h->next_sibling = NULL;
    h->first_child = NULL;
    h->last_child = NULL;
    h->value.weight = weight;
    return h;
}

/***********************************************
 * PUBLIC FUNCTIONS
 ***********************************************/

/* free heap */
void heap_free() {
    free(hp);
    free(hnodes);
}

/* get min value */
int heap_min() {
    return hp->root->value.v_not_in_mst;
}

/* decrease the value of the node */
void heap_decrease_key(heap_node *node, foi new_weight) {
    node->value.weight = new_weight;
    /* if the node is not at the root of the tree, remove it and
       merge it with the root */
    if (node!=hp->root) {
        /* remove the node tree from the siblings and parents*/
        heap_node_isolate(node);
        /* merge with root*/
        hp->root = heap_node_meld(hp->root,node);
    }
}

/* insert element to the heap */
heap_node * heap_insert(foi weight) {
    heap_node *node = heap_node_new(weight);
    hp->root = heap_node_meld(hp->root,node);
    return node;
}

/* delete min value. multi-pass */
void heap_delete_min() {
    heap_node *a,*b,*next_tmp,*new_root=NULL;

    heap_node * h = hp->root;

    /* until there is one node */
    /* heap_node_meld in pairs, 1st and 2nd, 3rd and 4th, ...*/
    while(h->first_child!=h->last_child) {

        a = h->first_child;
        while(a!=NULL)
        {
            next_tmp=NULL;
            b = a->next_sibling;
            heap_node_isolate(a);
            if (b) {
                next_tmp=b->next_sibling;
                heap_node_isolate(b);
                a = heap_node_meld(a,b);
            }
            h = heap_node_meld(h,a);
            a = next_tmp;
        }
    }

    if (h->first_child) {
        new_root = h->first_child;
        h->first_child->parent=NULL;
    }

    hp->root = new_root;
}

/* create a new heap */
heap* heap_new(int sz_v) {
    hp = (heap*)malloc(sizeof(heap));
    hp->root = NULL;
    hnodes = (heap_node*)malloc(sz_v * sizeof(heap_node));
    hnode_on = 0;
    return hp;
}

#ifdef _PH_TEST_
#include <stdio.h>
int main() {
    heap_node* n[5];

    heap *ph = heap_new();
    n[4] = heap_insert(ph, 4);
    n[1] = heap_insert(ph, 1);
    n[0] = heap_insert(ph, 0);
    n[3] = heap_insert(ph, 3);
    n[2] = heap_insert(ph, 2);

    int i;
    for(i=0; i<5; i++) {
        n[i]->value.v_in_mst = -i;
        n[i]->value.v_not_in_mst = i;
    }

    heap_decrease_key(ph, n[3], -1);

    for(i=0; i<5; i++) {
        int v_not_in_mst = heap_min(ph);
        heap_value* val = &n[v_not_in_mst]->value;
        printf("%d %d %f\n", val->v_in_mst, v_not_in_mst, val->weight);
        heap_delete_min(ph);
    }

    return 0;
}
#endif
