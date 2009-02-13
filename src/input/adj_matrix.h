#ifndef ADJ_MATRIX_H
#define ADJ_MATRIX_H

/**
 * Returns the index in an adjacency matrix which represents the weight between
 * edge u,v
 */
int AM_INDEX(int num_verts, int u, int v);

/* index to edge u, v in an adjacency matrix; u <= v must hold */
#define AM_INDEX_FAST(num_verts, u, v) ((u-1) * num_verts + (v-1))

#endif /* ADJ_MATRIX_H */
