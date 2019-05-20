import pyGP2.GP2_lib as GP2_lib
import pyGP2.pyLabel as pyLabel

#Label tests
x = pyLabel.Mark.RED
y = GP2_lib.get_mark_c(x)
print(y)
z = GP2_lib.get_mark_py(y)
print(pyLabel.mark_string(z))
a = GP2_lib.get_atom_c(pyLabel.GP2_Atom(string="ABC"))
print(GP2_lib.get_atom_py(a))
print("Converted")
atoms = pyLabel.list_to_label([0, "HI", 1])
print(pyLabel.label_string(atoms))
b = GP2_lib.get_hostlist_c(atoms)
c = GP2_lib.get_hostlist_py(b)
print("Converted")
print("Host list in python")
print(pyLabel.label_string(c))
b.free()
d = GP2_lib.get_hostlabel_c(atoms, x)
e, f = GP2_lib.get_hostlabel_py(d)
print("Converted")
print("Host label in python")
print(pyLabel.label_string(e) + pyLabel.mark_string(f))

import pyGP2.pyGraph as pyGraph

#Graph tests
py_g = pyGraph.GP2_Graph()
v1 = pyGraph.GP2_Node(label=pyLabel.list_to_label(["A", 0]), mark=pyLabel.Mark.NONE)
py_g.add_node(v1)
v2 = pyGraph.GP2_Node(label=pyLabel.list_to_label(["B", 1]), mark=pyLabel.Mark.NONE, root=True)
py_g.add_node(v2)
py_g.add_edge(v1, v2, label=pyLabel.list_to_label(["C", 2]), mark=pyLabel.Mark.NONE)
print("Python graph.")
print(py_g.to_string())
c_g = GP2_lib.graph_to_c(py_g)
print("C graph.")
GP2_lib.print_cGraph(c_g)
print("Back in Python.")
print(GP2_lib.graph_to_py(c_g).to_string())

import pyGP2.program as program
test_program  = '''Main = [r1]

r1(a, b : list)
[
    (n0, a)
    (n1, b)
    |
]
=>
[
    (n0, a)
    (n1, b)
    |
    (e0, n0, n0, "A":1:"B")
    (e1, n1, n1, "X":0:"Y")
]
interface = {
    n0, n1
}'''
prog = program.GP2_Program('test')
prog.load_from_string(test_program)
prog.compile()

import build_pyGP2_test.pyGP2_test as test
test.apply(c_g)
GP2_lib.print_cGraph(c_g)
test.apply(c_g)
GP2_lib.print_cGraph(c_g)
test.apply(c_g)
GP2_lib.print_cGraph(c_g)
test.apply(c_g)
GP2_lib.print_cGraph(c_g)
GP2_lib.free_graph_c(c_g)
