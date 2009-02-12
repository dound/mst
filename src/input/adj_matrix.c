#include <input/adj_matrix.h>

int AM_INDEX(int num_verts, int u, int v) {
    if(u <= v)
        return AM_INDEX_FAST(num_verts, u, v);
    else
        return AM_INDEX_FAST(num_verts, v, u);
}
