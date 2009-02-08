#include <boost/graph/adjacency_list.hpp>
#include <boost/graph/kruskal_min_spanning_tree.hpp>
#include <stdio.h>
#include <string.h>

int main(int argc, char** argv) {
  using namespace boost;
  typedef adjacency_list < vecS, vecS, undirectedS, no_property, property < edge_weight_t, float > > Graph;
  typedef graph_traits < Graph >::edge_descriptor Edge;
  typedef std::pair<int, int> E;

  if(argc < 2) {
      fprintf(stderr, "checker: usage: %s INPUT_GRAPH [WHETHER_TO_PRINT_EDGE_WEIGHTS]", argv[0]);
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
          fprintf(stderr, "checker: unable to open file %s", argv[1]);
          exit(1);
      }
  }

  // read the prescribed input format
  unsigned num_verts, num_edges;
  fscanf(fp, "%u %u", &num_verts, &num_edges);
  E* edge_array = new E[num_edges];
  float* weights = new float[num_edges];
  int u, v;
  for(unsigned i=0; i<num_edges; i++){
      fscanf(fp, "%d %d %f", &u, &v, &weights[i]);
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
  float total_weight = 0;
  for (std::vector < Edge >::iterator ei = spanning_tree.begin();
       ei != spanning_tree.end(); ++ei) {
      total_weight += weight[*ei];
  }
  printf("%.1f\n", total_weight);

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
