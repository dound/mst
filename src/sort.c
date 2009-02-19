#include <mst.h> /* edge */

void quicksort(edge *edges, int left, int right)
{
    int i, j;
    edge x, y;

    i = left;
    j = right;
    x = edges[(left+right)/2];

    do {
        while((edges[i].weight < x.weight) && (i < right))
            i++;
        while((x.weight < edges[j].weight) && (j > left))
            j--;

        if(i <= j) {
            y = edges[i];
            edges[i] = edges[j];
            edges[j] = y;
            i++; j--;
        }
    } while(i <= j);

    if(i < right)
        quicksort(edges, i, right);
    if(left < j)
        quicksort(edges, left, j);
}

void quicksortPart(edge *edges, int left, int right, int sortTo)
{
    int i, j;
    edge x, y;

    i = left;
    j = right;
    x = edges[(left+right)/2];

    do {
        while((edges[i].weight < x.weight) && (i < right))
            i++;
        while((x.weight < edges[j].weight) && (j > left))
            j--;

        if(i <= j) {
            y = edges[i];
            edges[i] = edges[j];
            edges[j] = y;
            i++; j--;
        }
    } while(i <= j);

    if(i < right && i <= sortTo)
        quicksortPart(edges, i, right, sortTo);
    if(left < j && j > sortTo)
        quicksortPart(edges, left, j, sortTo);
    else
        quicksort(edges, left, j);
}
