import pyGP2.config as config
import pyGP2.GP2_lib as GP2_lib
import sys
from shutil import copyfile
import subprocess
import shutil
import importlib
import os

#Change this to 'gp2.exe' on windows
default_execute = 'gp2'

class GP2_Program:
    def __init__(self, name):
        self.name = name
        self.compiled = False

    def load_from_string(self, string):
        self.string = string
        self.file_path = None
        self.mode = "from_string"

    def load_from_file(self, file_path):
        self.string = None
        self.file_path = file_path
        self.mode = "from_file"

    def compile(self, clean=True):
        self.compiled = True
        #Get gp2_directory
        gp2_directory = config.get_config(0).path

        #Set up args
        working_dir = os.path.abspath("build_pyGP2_") + self.name
        if not os.path.exists(working_dir):
            os.makedirs(working_dir)
        else:
            for the_file in os.listdir(working_dir):
                file_path = os.path.join(working_dir, the_file)
                try:
                    if os.path.isfile(file_path):
                        os.unlink(file_path)
                    elif os.path.isdir(file_path): shutil.rmtree(file_path)
                except Exception as e:
                    print(e)
        execute_cmd = gp2_directory + "/bin/" + default_execute
        program_path = working_dir + "/program.gp2"

        #If we're compiling from a string, we have to now dump the string into a file.
        if self.mode == "from_string":
            with open(program_path, "w") as text_file:
                text_file.write(self.string)
        #If we're compiling from a file, we will copy the file to make sure we don't
        #break the original
        elif self.mode == "from_file":
            copyfile(self.file_path, program_path)

        #Now we can actually compile the program
        compile_args = execute_cmd + " -l " + gp2_directory + " -m " + self.name + " -o "  + working_dir + " " + program_path
        process = subprocess.Popen(compile_args, shell=True, stdout=subprocess.DEVNULL)
        process.wait()

        #Generate a makefile
        make_file_string = get_make_file(self.name, gp2_directory, clean=clean)
        make_file_path = working_dir + "/Makefile"
        with open(make_file_path, "w") as text_file:
            text_file.write(make_file_string)

        #JANKY FIX: should be fixed IN the compiler
        with open(working_dir + "/" + self.name + ".h", 'r') as file:
            data = file.read()
        data = "#include \"graph.h\"\n#include \"morphism.h\"\n" + data
        with open(working_dir + "/" + self.name + ".h", "w") as text_file:
            text_file.write(data)

        #Generate a pyx file for wrapping the shared library
        pyx_file_string = get_pyx_file(self.name)
        pyx_file_path = working_dir + "/pyGP2_" + self.name + ".pyx"
        with open(pyx_file_path, "w") as text_file:
            text_file.write(pyx_file_string)

        #Generate a setup file for compiling the pyx file
        setup_file_string = get_cython_setup(self.name, gp2_directory, working_dir)
        setup_file_path = working_dir + "/" + self.name + "_setup.py"
        with open(setup_file_path, "w") as text_file:
            text_file.write(setup_file_string)


        #Build the c gp2 code into a shared library
        process = subprocess.Popen("make -C " + working_dir + "/", shell=True, stdout=subprocess.DEVNULL)
        process.wait()

        sys.path.insert(0, working_dir)
        i = importlib.import_module("pyGP2_" + self.name)
        sys.path.pop(0)
        self.apply = i.apply

    #Applies the compiled program directly to a c_graph wrapper in GP2_lib's
    #cGraph_wrapper class
    def execute_c(self, c_graph_wrapper):
        if not self.compiled:
            raise Exception("Attempt to call non-compiled GP2 Program", self.name)
        self.apply(c_graph_wrapper)

    #Applies the compiled program to a pyGP2 GP2_Graph objectself.
    #Converts to c, wrapped in cGraph_wrapper, uses execute_c, and converts back to
    #python, remembering to free the transformed c graph.
    def execute_py(self, py_graph):
        c_graph_wrapper = GP2_lib.graph_to_c(py_graph)
        self.execute_c(c_graph_wrapper)
        py_graph = GP2_lib.graph_to_py(c_graph_wrapper)
        GP2_lib.free_graph_c(c_graph_wrapper)
        return py_graph

def get_make_file(name, gp2_dir, clean=True):
    my_string = '''INCDIR=''' + gp2_dir + '''/include\n
LIBDIR=''' + gp2_dir + '''/lib\n
OBJECTS := *.c
CC=gcc

CFLAGS = -shared -I$(INCDIR) -L$(LIBDIR) -O2 -Wall -Wextra -lgp2 -lm -fPIC -fno-semantic-interposition

default:	$(OBJECTS)
		$(CC) $(OBJECTS) $(CFLAGS) -o lib''' + name + '''.so
		python3 ''' + name + '''_setup.py build_ext --inplace\n'''
    if clean:
        my_string += '''		rm -r -f build *.log *.demo Makefile *.gp2 *.c *.pyx *.py *.h\n'''
    my_string += '''clean:
		rm *'''
    return my_string

def get_pyx_file(name):
    my_string = '''#!python
#cython: language_level=2

cdef extern from "graph.h":
  ctypedef struct Graph:
    pass

#Wrapper for a C based GP 2 graph
cdef class cGraph_wrapper:
    cdef Graph* graph

    cdef Graph* get_graph(self):
      return self.graph

cdef extern from "''' + name + '''.h":
  int ''' + name + '''_execute(Graph* host_graph)

def apply(graph):
  cdef cGraph_wrapper c_graph = <cGraph_wrapper> graph
  ''' + name + '''_execute(c_graph.graph)'''
    return my_string

def get_cython_setup(name, gp2_dir, working_dir):
    my_string = '''from distutils.core import setup
from distutils.extension import Extension
from Cython.Build import cythonize
gp2_path = "''' + gp2_dir + '''"
working_dir = "''' + working_dir + '''"
examples_extension = Extension(
    name="pyGP2_''' + name + '''",
    sources=["pyGP2_''' + name + '''.pyx"],
    libraries=["gp2", "''' + name + '''"],
    library_dirs=[gp2_path + "/lib", working_dir],
    include_dirs=[gp2_path + "/include", working_dir],
    runtime_library_dirs=[working_dir + '/']
)
setup(
    name="cython_''' + name + '''",
    ext_modules=cythonize([examples_extension])
)'''
    return my_string

def load_compiled_program(name, directory):
    sys.path.insert(0, directory + "/build_pyGP2_" + name)
    i = importlib.import_module("pyGP2_" + name)
    sys.path.pop(0)
    program = GP2_Program(name)
    program.compiled = True
    program.apply = i.apply
    return program
