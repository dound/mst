/**
 * This code is from "Algorithms in C, Third Edition," by Robert Sedgewick,
 * Addison-Wesley, 1998."  It was adapted and enhanced by David Underhill.
 */

#include <input/pq_edge.h>
#include <mst.h> /* edge */
#include <stdlib.h> /* malloc */

/** swap two edges */
#define exch(a,b) { edge __e = a; a = b; b = __e; }

/** compare two edges' weights */
#define greater(a,b) ((a.weight) > (b.weight))

edge *pq;
static unsigned N;

static inline void pq_fix_up(unsigned k) {
    while(k > 1 && greater(pq[k/2], pq[k])) {
        exch(pq[k], pq[k/2]);
        k = k / 2;
    }
}

/** bubble down the kth edge */
static inline void pq_fix_down(unsigned k, unsigned N) {
    unsigned j;
    while(2 * k <= N) {
        j = 2 * k;
        if (j < N && greater(pq[j], pq[j+1])) j++;
        if (!greater(pq[k], pq[j])) break;
        exch(pq[k], pq[j]);
        k = j;
    }
}

void pq_init(unsigned maxN) {
    pq = malloc((maxN+1)*sizeof(edge));
    N = 0;
}

unsigned pq_empty() {
    return N == 0;
}

void pq_insert(edge v) {
    pq[++N] = v;
    pq_fix_up(N);
}

void pq_heapify_insertion() {
    pq_fix_up(++N);
}

edge pq_pop_min() {
    exch(pq[1], pq[N]);
    pq_fix_down(1, N-1);
    return pq[N--];
}

