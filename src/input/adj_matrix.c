#ifdef _HALF_ADJ_MATRIX_

#include <input/adj_matrix.h>

int AM_INDEX(int num_verts, int u, int v) {
    if(u <= v)
        return AM_INDEX_FAST(num_verts, u, v);
    else
        return AM_INDEX_FAST(num_verts, v, u);
}

int AM_INDEX_NO_ADJ(int num_verts, int u, int v) {
    if(u <= v)
        return AM_INDEX_FAST_NO_ADJ(num_verts, u, v);
    else
        return AM_INDEX_FAST_NO_ADJ(num_verts, v, u);
}

#endif
