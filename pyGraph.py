from pyGP2.pyLabel import *

class GP2_Edge():
    def __init__(self, source, target, label=[], mark=Mark.NONE):
        if not validate_label(label):
            raise ValueError("Invalid label: " + label_string(label))
        self.label = label
        self.mark = mark
        self.source = source
        self.target = target
        if mark == Mark.GREY:
            raise ValueError("Edges cannot be marked GREY")

    def get_source(self):
        return self.source

    def get_target(self):
        return self.target

    def get_label(self):
        return self.label

    def set_label(self, new_label):
        if not validate_label(new_label):
            raise ValueError("Invalid label: " + label_string(new_label))
        self.label = new_label

    def get_mark(self):
        return self.mark

    def set_mark(self, mark):
        if not validate_mark(mark):
            raise ValueError(str(mark) + " is not a valid mark.")
        self.mark = mark

    def to_string(self, graph):
        return "    (" + str(graph.get_edge_index(self)) + ", " + str(graph.get_node_index(self.source)) + ", " + str(graph.get_node_index(self.target)) + ", " + label_string(self.label) + mark_string(self.mark) + ")"

class GP2_Node():
    def __init__(self, label=[], mark=Mark.NONE, root = False):
        if not validate_label(label):
            raise ValueError("Invalid label: " + label_string(label))
        self.label = label
        self.mark = mark
        self.in_edges = []
        self.out_edges = []
        self.root = root
        if mark == Mark.DASHED:
            raise ValueError("Nodes cannot be marked DASHED.")

    def copy(self):
        label_copy = [item.copy() for item in self.label]
        return GP2_Node(label = label_copy, mark = self.mark, root = self.root)

    def add_in_edge(self, source, label=[], mark=Mark.NONE):
        e = GP2_Edge(source, self, label=label, mark=mark)
        self.in_edges.append(e)
        source.out_edges.append(e)

    def add_out_edge(self, target, label=[], mark=Mark.NONE):
        e = GP2_Edge(self, target, label=label, mark=mark)
        self.in_edges.append(e)
        target.in_edges.append(e)

    def delete_in_edge(self, edge):
        if edge not in self.in_edges:
            raise IndexError("Edge " + str(edge) + " not found.")
        self.in_edges.remove(edge)
        edge.source.out_edges.remove(edge)

    def delete_out_edge(self, edge):
        if edge not in self.out_edges:
            raise IndexError("Edge " + str(edge) + " not found.")
        self.out_edges.remove(edge)
        edge.target.in_edges.remove(edge)

    def get_label(self):
        return self.label

    def set_label(self, new_label):
        if not validate_label(new_label):
            raise ValueError("Invalid label: " + label_string(new_label))
        self.label = new_label

    def get_mark(self):
        return self.mark

    def set_mark(self, mark):
        if not validate_mark(mark):
            raise ValueError(str(mark) + " is not a valid mark.")
        self.mark = mark

    def is_root(self):
        return self.root

    def set_root(self, root):
        self.root = root

    def to_string(self, graph):
        root_str = ""
        if(self.is_root()):
            root_str = "(R)"
        return "    (" + str(graph.get_node_index(self)) + root_str + ", " + label_string(self.label) + mark_string(self.mark) + ")"

class GP2_Graph():
    def __init__(self):
        self.nodes= []

    def count_nodes(self):
        return len(self.nodes)

    def get_edges(self):
        edge_arr = []
        for node in self.nodes:
            edge_arr += [e for e in node.out_edges]
        return edge_arr

    def count_edges(self):
        return len(self.get_edges())

    def get_node_index(self, node):
        return self.nodes.index(node)

    def get_edge_index(self, edge):
        return self.get_edges().index(edge)

    def get_node(self, index):
        return self.nodes[index]

    def get_edge(self, index):
        return self.get_edges()[index]

    def add_node(self, node):
        if not isinstance(node, GP2_Node):
            raise ValueError(str(node) + " is not a GP2 Node.")
        self.nodes.append(node)

    def delete_node(self, node):
        if not node in self.nodes:
            raise IndexError("Node " + str(node) + " not found in graph node list.")
        if len(node.in_edges) > 0 or len(node.out_edges) > 0:
            raise RuntimeError("Node " + str(node) + " has incoming or outgoing edges.")
        self.nodes.remove(node)

    def delete_node_and_context(self, node):
        if not node in self.nodes:
            raise IndexError("Node " + str(node) + " not found in graph node list.")
        for edge in node.in_edges:
            self.delete_edge(edge)
        for edge in node.out_edges:
            self.delete_edge(edge)
        self.delete_node(node)

    def add_edge(self, source, target, label=[], mark=Mark.NONE):
        if source not in self.nodes:
            raise IndexError("Source " + str(source) + " not found in graph node list.")
        if target not in self.nodes:
            raise IndexError("Target " + str(target) + " not found in graph node list.")
        target.add_in_edge(source, label, mark)

    def delete_edge(self, edge):
        if edge not in self.get_edges():
            raise IndexError("Edge " + str(edge) + " not found in graph edge list.")
        edge.target.delete_in_edge(edge)

    def to_string(self):
        string = "[\n"
        for node in self.nodes:
            string += node.to_string(self) + "\n"
        string += "    |\n"
        for edge in self.get_edges():
            string += edge.to_string(self) + "\n"
        string += "]\n"
        return string

    def copy(self):
        node_map = {}
        new_g = GP2_Graph()
        for node in self.nodes:
            node_copy = GP2_Node(label=copy_label(node.label), mark=node.mark, root=node.root)
            new_g.add_node(node_copy)
            node_map[node] = node_copy

        for edge in self.get_edges():
            new_g.add_edge(node_map[edge.source], node_map[edge.target], label=copy_label(edge.label), mark=edge.mark)
        return new_g
