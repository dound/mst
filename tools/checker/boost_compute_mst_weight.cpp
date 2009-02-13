#include <boost/graph/adjacency_list.hpp>
#include <boost/graph/kruskal_min_spanning_tree.hpp>
#include <stdio.h>
#include <string.h>

#define USE_DOUBLES 0
#define USE_FLOATS 0
#if USE_DOUBLES == 1
#   define FP_TYPE double
#   define SCANF_FP_STR "%d %d %lf"
#elif USE_FLOATS == 1
#   define FP_TYPE float
#   define SCANF_FP_STR "%d %d %f"
#else
#   define FP_TYPE int
#   define SCANF_FP_STR "%d %d %d.%d"
#endif

int main(int argc, char** argv) {
  using namespace boost;
  typedef adjacency_list < vecS, vecS, undirectedS, no_property, property < edge_weight_t, FP_TYPE > > Graph;
  typedef graph_traits < Graph >::edge_descriptor Edge;
  typedef std::pair<int, int> E;

  if(argc < 2) {
      fprintf(stderr, "checker: usage: %s INPUT_GRAPH [WHETHER_TO_PRINT_EDGE_WEIGHTS]\n", argv[0]);
      exit(1);
  }
  bool print_mst_edges = argc > 2;

  // get the stream to read the input from
  FILE* fp;
  if(strcmp(argv[1],"stdin")==0)
      fp = stdin;
  else {
      fp = fopen(argv[1], "r");
      if(fp == NULL) {
          fprintf(stderr, "checker: unable to open file %s\n", argv[1]);
          exit(1);
      }
  }

  // read the prescribed input format
  unsigned num_verts, num_edges;
  if(fscanf(fp, "%u %u", &num_verts, &num_edges) != 2) {
      fprintf(stderr, "checker: bad header in input %s\n", argv[1]);
      exit(1);
  }
  E* edge_array = new E[num_edges];
  FP_TYPE* weights = new FP_TYPE[num_edges];
  int u, v;
  for(unsigned i=0; i<num_edges; i++){
#if USE_DOUBLES!=0 || USE_FLOATS!=0
      if(fscanf(fp, SCANF_FP_STR, &u, &v, &weights[i]) != 3) {
#else
      int tmp;
      if(fscanf(fp, SCANF_FP_STR, &u, &v, &weights[i], &tmp) == 4)
          weights[i] = weights[i] * 10 + tmp;
      else {
#endif
          fprintf(stderr, "checker: bad line in input %s\n", argv[1]);
          exit(1);
      }
      edge_array[i] = E(u, v);
  }
  fclose(fp);

  // construct the graph object
  Graph g(edge_array, edge_array + num_edges, weights, num_verts);
  property_map < Graph, edge_weight_t >::type weight = get(edge_weight, g);
  std::vector < Edge > spanning_tree;

  // determine the MST
  kruskal_minimum_spanning_tree(g, std::back_inserter(spanning_tree));

  // compute and print the total weight of the MST
  FP_TYPE total_weight = 0;
  for (std::vector < Edge >::iterator ei = spanning_tree.begin();
       ei != spanning_tree.end(); ++ei) {
      total_weight += weight[*ei];
  }
#if USE_DOUBLES!=0 || USE_FLOATS!=0
  printf("%.15f\n", total_weight);
#else
  printf("%.15f\n", total_weight / 10.0f);
#endif

  // print edges if desired
  if(print_mst_edges) {
      for (std::vector < Edge >::iterator ei = spanning_tree.begin();
           ei != spanning_tree.end(); ++ei) {
          int src = source(*ei, g);
          int dst = target(*ei, g);
          printf("%d %d\n", src, dst);
      }
  }

  return 0;
}
