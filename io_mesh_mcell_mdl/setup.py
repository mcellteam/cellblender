#!/usr/bin/env python

"""
setup.py file for mdlmesh_parser
"""

from distutils.core import setup, Extension


mdlmesh_parser_module = Extension(name='_mdlmesh_parser',
                           sources=['mdlmesh_parser_wrap.c', 'mdlmesh_parser.c', 'mdllex.flex.c', 'mdlparse.bison.c', 'vector.c'],
                           extra_compile_args=['-O3'],
                           extra_link_args=['-o_mdlmesh_parser.so'],
                           )

setup (name = 'mdlmesh_parser',
       version = '1.00',
       author      = "Tom Bartol",
       description = """Parse files in MCell MDL mesh format""",
       ext_modules = [mdlmesh_parser_module],
       py_modules = ["mdlmesh_parser"],
       )

