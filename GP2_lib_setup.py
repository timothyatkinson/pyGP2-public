from distutils.core import setup
from distutils.extension import Extension
from Cython.Build import cythonize
from pyGP2.config import get_config
import pyximport
pyximport.install(reload_support=True)
gp2_path = get_config(0).path
examples_extension = Extension(
    name="GP2_lib",
    sources=["GP2_lib_wrapper.pyx"],
    libraries=["gp2"],
    library_dirs=[gp2_path + "/lib"],
    include_dirs=[gp2_path + "/include"]
)
setup(
    name="cython_example",
    ext_modules=cythonize([examples_extension]),
)
