# setup.py

from distutils.core import setup, Extension

setup(name="libMCell_cpp",
      py_modules=['libMCell_cpp'], 
      ext_modules=[Extension("_libMCell_cpp",
                     ["libMCell_cpp.i","libMCell_cpp.cpp"],
                     swig_opts=['-c++'],
                  )]
      
)
