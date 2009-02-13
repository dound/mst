// mst main
#include <mst.h>
#include <stdio.h> /* fprintf */

int main(int argc, char **argv) {
#ifdef _DEBUG_
    if(argc != 2) {
        fprintf(stderr, "usage: ./mst <inputfile>\n");
        return 0;
    }
#endif

    kruskal(argv[1]);
    return 0;
}
