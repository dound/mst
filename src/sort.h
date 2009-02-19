/* interface for sorting functions */
#ifndef SORT_H
#define SORT_H

#include <mst.h> /* edge */

void quicksort(edge *edges, int left, int right);
void quicksortPart(edge *edges, int left, int right, int sortTo);

#endif /* SORT_H */
