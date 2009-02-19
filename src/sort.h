/* interface for sorting functions */
#ifndef SORT_H
#define SORT_H

#include <mst.h> /* edge */

void quicksortPart(edge *edges, int left, int right, int sortTo);

void qsort_edges(edge *arr, unsigned n);

#endif /* SORT_H */
