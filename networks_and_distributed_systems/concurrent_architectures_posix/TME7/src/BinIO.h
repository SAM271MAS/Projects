// BinIO.h
#pragma once

#include "Graph.h"
#include <cerrno>
#include <cstdint>
#include <cstdlib>
#include <fcntl.h>
#include <iostream>
#include <sys/types.h>
#include <unistd.h>
#include <unordered_map>
#include <vector>

struct NodeHeader {
  size_t id;
  size_t child_count;
};


/**
 * Sérialise un noeud et le sous graphe qu'il permet d'atteindre dans le fichier.
 * Arguments :
 * - fd : descripteur de fichier ouvert en écriture
 * - node : pointeur vers le Vertex à sérialiser
 * - ptr_to_offset : table de hash associant aux pointeurs de Vertex les offsets dans le fichier où ils ont été sérialisés
 * Retourne l'offset dans le fichier où le noeud a été sérialisé.
 */

off_t serialize(int fd, const Vertex *node, std::unordered_map<const Vertex *, off_t> &ptr_to_offset) {

    auto it = ptr_to_offset.find(node);
    if (it != ptr_to_offset.end()){
        return it->second;
    }


    off_t current_offset = lseek(fd, 0, SEEK_END);
    ptr_to_offset[node] = current_offset;

    NodeHeader nd;
    nd.child_count = node->children.size();
    nd.id = node->id;

    write(fd, &nd, sizeof(nd));



    ftruncate(fd, current_offset + sizeof(NodeHeader) + (nd.child_count * sizeof(off_t)));



    for (size_t i = 0; i < nd.child_count; ++i){
        off_t child_offset = serialize(fd, node->children[i], ptr_to_offset);
        pwrite(fd, &child_offset, sizeof(off_t), current_offset + sizeof(NodeHeader) +  (i * sizeof(off_t)));
    }
  return current_offset;
}

/**
 * Désérialise un noeud à partir du fichier.
 * Arguments :
 * - fd : descripteur de fichier ouvert en lecture
 * - offset : position dans le fichier du noeud à désérialiser
 * - offset_to_vertex : table de hash associant aux offsets des pointeurs vers les Vertex déjà
 * désérialisés
 * - graph : le graphe dans lequel insérer les Vertex désérialisés
 * Retourne un pointeur vers le Vertex désérialisé.
 */
Vertex *deserialize(int fd, off_t offset, std::unordered_map<off_t, Vertex *> &offset_to_vertex, Graph &graph) {



    auto it = offset_to_vertex.find(offset);                                                                               
    if (it != offset_to_vertex.end()){                                      
        return it->second;                                               
    }

    NodeHeader node;
    lseek(fd,  offset, SEEK_SET);
    read(fd, &node,  sizeof(NodeHeader));

    Vertex *sommet = graph.findNode(node.id);
    offset_to_vertex[offset] = sommet;


    for (size_t i = 0; i < node.child_count; ++i){
        off_t child_offset;
        pread(fd, &child_offset, sizeof(child_offset), offset + sizeof(node) + (i * sizeof(child_offset)));
        sommet->children.push_back( deserialize(fd, child_offset, offset_to_vertex, graph));
    }

    return sommet;
}

void writeBin(const Graph &graph, const std::string &filename) {
  int fd = open(filename.c_str(), O_RDWR | O_CREAT | O_TRUNC, 0666);
  if (fd == -1) {
    perror("open output");
    exit(1);
  }

    size_t foo = 0;
    write(fd, &foo, sizeof(size_t));

  std::unordered_map<const Vertex *, off_t> ptr_to_offset;
  serialize(fd, graph.findNode(0), ptr_to_offset);

  size_t N = ptr_to_offset.size();

    lseek(fd, 0, SEEK_SET);
    write(fd, &N, sizeof(size_t));
    

  close(fd);
}

Graph parseBin(const std::string &filename) {
  int fd = open(filename.c_str(), O_RDONLY);
  if (fd == -1) {
    perror("open input");
    exit(1);
  }

  size_t N;

    read(fd, &N, sizeof(size_t));

  Graph graph(N);

  off_t root_offset = sizeof(size_t);

  std::unordered_map<off_t, Vertex *> offset_to_vertex;
  deserialize(fd, root_offset, offset_to_vertex, graph);

  close(fd);

  return graph;
}
