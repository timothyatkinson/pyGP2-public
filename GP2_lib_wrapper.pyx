#!python
#cython: language_level=2

from libc.string cimport memset
from libc.stdlib cimport malloc, free
from libc.string cimport strcpy, strlen
from pyGP2.pyLabel import GP2_Atom
from pyGP2.pyGraph import GP2_Node, GP2_Edge, GP2_Graph
cdef extern from "label.h":

  ctypedef enum MarkType:
    NONE, RED, GREEN, BLUE, GREY, DASHED, ANY

  ctypedef struct HostAtom:
    char type
    int num
    char* str

  ctypedef struct HostListItem:
     HostAtom atom
     HostListItem *next
     HostListItem *prev

  ctypedef struct HostList:
    int hash
    HostListItem *first
    HostListItem *last

  ctypedef struct HostLabel:
    MarkType mark
    int length
    HostList *list

  HostList *makeHostList(HostAtom *array, int length, bint free_strings)

  HostLabel makeEmptyLabel(MarkType mark)
  HostLabel makeHostLabel(MarkType mark, int length, HostList *list)

  HostList *cocHostList_wrapper(HostList *list)

  void freeHostList(HostList *list)

import pyGP2.pyLabel as pyLabel

#Mapping from pyLabel.Mark to label.h's MarkType
def get_mark_c(mark) -> MarkType:
  if (mark == pyLabel.Mark.NONE):
    return MarkType.NONE
  elif mark == pyLabel.Mark.RED:
    return MarkType.RED
  elif mark == pyLabel.Mark.GREEN:
    return MarkType.GREEN
  elif mark == pyLabel.Mark.BLUE:
    return MarkType.BLUE
  elif mark == pyLabel.Mark.GREY:
    return MarkType.GREY
  elif mark == pyLabel.Mark.DASHED:
    return MarkType.DASHED

#Mapping from label.h's markType and pyLabel.Mark
def get_mark_py(mark: MarkType) -> MarkType:
  if (mark == MarkType.NONE):
    return pyLabel.Mark.NONE
  elif (mark == MarkType.RED):
    return pyLabel.Mark.RED
  elif (mark == MarkType.GREEN):
    return pyLabel.Mark.GREEN
  elif (mark == MarkType.BLUE):
    return pyLabel.Mark.BLUE
  elif (mark == MarkType.GREY):
    return pyLabel.Mark.GREY
  elif (mark == MarkType.DASHED):
    return pyLabel.Mark.DASHED

#Wrapper for a c-based HostAtom
cdef class cAtom_wrapper:
  cdef HostAtom atom

#Converts a python string to c
cdef char* string_to_c(py_string):
  cdef char* c_argv
  # Allocate memory
  c_argv = <char*>malloc((len(py_string) + 1) * sizeof(char))
  # Check if allocation went fine
  if c_argv is NULL:
    raise MemoryError()
  # Convert str to char* and store it into our char**
  py_string = py_string.encode('UTF-8')
  for i in range(len(py_string)):
    c_argv[i] = py_string[i]
  c_argv[len(py_string)] = '\0'
  return c_argv

#Mapping from pyLabel.GP2_Atom to label.h's HostAtom
cdef HostAtom atom_to_c(gp2_atom):
  cdef HostAtom atom
  if gp2_atom.get_type() == pyLabel.Type.NUM:
    atom.num = gp2_atom.num
    atom.type = 'i'
  elif gp2_atom.get_type() == pyLabel.Type.CHAR:
    atom.str = string_to_c(gp2_atom.ch)
    atom.type = 's'
  elif gp2_atom.get_type() == pyLabel.Type.STRING:
    atom.str = string_to_c(gp2_atom.string)
    atom.type = 's'
  return atom

#Returns label.h's HostAtom equivalent of pyLabel.GP2_Atom input gp2_atom, wrapped in
#cAtom_wrapper wrapper.
def get_atom_c(gp2_atom) -> cAtom_wrapper:
  at = cAtom_wrapper()
  atom = atom_to_c(gp2_atom)
  at.atom = atom
  return at

#Returns pyLabel.Gp2_Atom equivalent of label.h's HostAtom wrapped in cAtom_wrapper wrapper atom.
def get_atom_py(atom: cAtom_wrapper):
  cdef HostAtom c_atom = atom.atom
  if c_atom.type == 's':
    py_atom = GP2_Atom(string=c_atom.str.decode("UTF-8"))
  elif c_atom.type == 'i':
    py_atom = GP2_Atom(num=c_atom.num)
  return py_atom

#Wrapper for a c-based HostList
cdef class cHostList_wrapper:
  cdef HostList* list

  def free(self):
    freeHostList(self.list)

#Mapping from a list of pyLabel.GP2_Atoms to label.h's HostList
cdef HostList* hostlist_to_c(gp2_atoms):
  length = len(gp2_atoms)
  cdef HostAtom *atoms = <HostAtom*>malloc(length * sizeof(HostAtom))
  i = 0
  for gp2_atom in gp2_atoms:
    host_atom = atom_to_c(gp2_atom)
    atoms[i] = host_atom
    i += 1
  cdef HostList* list
  list = makeHostList(atoms, length, 0)
  return list

def get_hostlist_c(gp2_atoms):
  hl = cHostList_wrapper()
  hl.list = hostlist_to_c(gp2_atoms)
  print("Successfully converted")
  return hl

def get_hostlist_py(host_list: cHostList_wrapper):
  cdef HostListItem* item = host_list.list.first
  list = []
  cdef HostAtom atom
  while item != NULL:
    atom = item.atom
    wrap_atom = cAtom_wrapper()
    wrap_atom.atom = item.atom
    py_atom = get_atom_py(wrap_atom)
    list.append(py_atom)
    item = item.next
  return list

#Wrapper for a c-based HostLabel
cdef class cHostLabel_wrapper:
  cdef HostLabel label

  def free(self):
    freeHostList(self.label.list)

cdef HostLabel hostlabel_to_c(gp2_atoms, mark):
  length = len(gp2_atoms)
  cdef HostList* list = hostlist_to_c(gp2_atoms)
  cdef MarkType c_mark = get_mark_c(mark)
  return makeHostLabel(c_mark, length, list)

def get_hostlabel_c(gp2_atoms, mark):
  hlab = cHostLabel_wrapper()
  hlab.label = hostlabel_to_c(gp2_atoms, mark)
  return hlab

def get_hostlabel_py(host_label: cHostLabel_wrapper):
  list = host_label.label.list
  wrapper_list = cHostList_wrapper()
  wrapper_list.list = list
  hostlist = get_hostlist_py(wrapper_list)
  mark = get_mark_py(host_label.label.mark)
  return hostlist, mark

cdef extern from "graph.h":
  ctypedef struct IntArray:
    int capacity
    int size
    int *items

  IntArray makeIntArray(int initial_capacity)
  void addToIntArray(IntArray *array, int item)
  void removeFromIntArray(IntArray *array, int index)

  ctypedef struct Node:
     int index
     bint root
     HostLabel label
     int outdegree, indegree
     int first_out_edge, second_out_edge
     int first_in_edge, second_in_edge
     IntArray out_edges, in_edges
     bint matched

  ctypedef struct RootNodes:
    int index
    RootNodes *next

  ctypedef struct Edge:
    int index
    HostLabel label
    int source, target
    bint matched

  ctypedef struct NodeArray:
    int capacity
    int size
    Node *items
    IntArray holes

  ctypedef struct EdgeArray:
    int capacity
    int size
    Edge *items
    IntArray holes

  ctypedef struct Graph:
    NodeArray nodes
    EdgeArray edges
    int number_of_nodes, number_of_edges
    RootNodes *root_nodes

  Graph *newGraph(int nodes, int edges)
  int addNode(Graph *graph, bint root, HostLabel label)
  void addRootNode(Graph *graph, int index)
  int addEdge(Graph *graph, HostLabel label, int source_index, int target_index)
  void removeNode(Graph *graph, int index)
  void removeRootNode(Graph *graph, int index)
  void removeEdge(Graph *graph, int index)
  void relabelNode(Graph *graph, int index, HostLabel new_label)
  void changeNodeMark(Graph *graph, int index, MarkType new_mark)
  void changeRoot(Graph *graph, int index)
  void resetMatchedNodeFlag(Graph *graph, int index)
  void relabelEdge(Graph *graph, int index, HostLabel new_label)
  void changeEdgeMark(Graph *graph, int index, MarkType new_mark)
  void resetMatchedEdgeFlag(Graph *graph, int index)

  Node *getNode(Graph *graph, int index)
  Edge *getEdge(Graph *graph, int index)
  RootNodes *getRootNodeList(Graph *graph)
  Edge *getNthOutEdge(Graph *graph, Node *node, int n)
  Edge *getNthInEdge(Graph *graph, Node *node, int n)
  Node *getSource(Graph *graph, Edge *edge)
  Node *getTarget(Graph *graph, Edge *edge)
  HostLabel getNodeLabel(Graph *graph, int index)
  HostLabel getEdgeLabel(Graph *graph, int index)
  int getIndegree(Graph *graph, int index)
  int getOutdegree(Graph *graph, int index)
  void printfGraph(Graph *graph)
  void freeGraph(Graph *graph)

#Wrapper for a C based GP 2 graph
cdef class cGraph_wrapper:
    cdef Graph* graph

    cdef Graph* get_graph(self):
      return self.graph

#Converts a pyGraph GP2_Graph object to a c-based Graph* from graph.h, wrapper in a cGraph_wrapper
def graph_to_c(py_graph, size_n = 1000, size_e = 2000):
  if size_n == None:
    nodes = py_graph.count_nodes()
    size_n = nodes * 2
  if size_e == None:
    edges = py_graph.count_edges()
    size_e = edges * 2
  cdef Graph* graph = newGraph(size_n, size_e)
  node_map = {}
  cdef int index = -1
  cdef HostLabel label
  for node in py_graph.nodes:
    label = hostlabel_to_c(node.label, node.mark)
    index = addNode(graph, node.root, label)
    node_map[node] = index
  for edge in py_graph.get_edges():
    source_index = node_map[edge.source]
    target_index = node_map[edge.target]
    label = hostlabel_to_c(edge.label, edge.mark)
    addEdge(graph, label, source_index, target_index)
  cdef cGraph_wrapper wrapper = cGraph_wrapper()
  wrapper.graph = graph
  return wrapper

def print_cGraph(wrapper: cGraph_wrapper):
  printfGraph(wrapper.graph)

#Converts a Graph* from graph.h wrapped in a cGraph_wrapper to a pyGraph Gp2_Graph object
def graph_to_py(c_graph: cGraph_wrapper):
  py_graph = GP2_Graph()
  node_map = {}
  cdef Graph* graph = c_graph.graph
  cdef int n_max = graph.nodes.size
  cdef int e_max = graph.edges.size
  cdef Node* v = NULL
  for i in range(n_max):
      v = getNode(graph, i)
      if v != NULL and v.index != -1:
        wrapper = cHostLabel_wrapper()
        wrapper.label = v.label
        list, mark = get_hostlabel_py(wrapper)
        r = v.root
        node_copy = GP2_Node(label=list, mark=mark, root=r)
        py_graph.add_node(node_copy)
        node_map[i] = node_copy
  cdef Edge* e = NULL
  for i in range(e_max):
    e = getEdge(graph, i)
    if e != NULL and e.index != -1:
      wrapper = cHostLabel_wrapper()
      wrapper.label = e.label
      list, mark = get_hostlabel_py(wrapper)
      source_node = node_map[e.source]
      target_node = node_map[e.target]
      py_graph.add_edge(source_node, target_node, label=list, mark=mark)
  return py_graph

def free_graph_c(c_graph: cGraph_wrapper):
  freeGraph(c_graph.graph)

#When imported, srand is reset
cdef extern from "stdlib.h":
    void srand(long int seedval)

cdef extern from "time.h":
  cdef struct time_t:
    pass
  time_t time(time_t *t)

srand(<long int>time(NULL))
