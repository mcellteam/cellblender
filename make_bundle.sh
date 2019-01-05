#!/bin/sh

# Steps to create our own Blender distribution bundled with more capable Python (needed for scipy and matplotlib), CellBlender, and all requirements
#  1) untar an official Blender distribution
#  2) ln -s some_path_to_blender_distribution ~/my_blender_dir
#  3) Get and untar version of Python matching the Blender distribution (e.g. Python3.5.3)
#  4) Remove Blender's Python, e.g.:
       a) rm -rf ~/my_blender_dir/2.79/python/*
#  5) Configure, build, and install new Python into Blender distribution, e.g.:
#      a) ./configure --enable-optimizations --prefix=~/my_blender_dir/2.79/python

#       or on Mac:
#       
#      a) first download source for gettext-0.19.8, libiconv-1.15, libressl-2.2.7
#      b) configure each of these to install into /Users/bartol/src/cellblender_bundle_requirements/install_dir/
#
#      c) Next configure build of Python like this:
#       
#           setenv CFLAGS "-I/Users/bartol/src/cellblender_bundle_requirements/install_dir/include"
#
#           ./configure --prefix=/Applications/Blender-2.79-CellBlender/blender.app/Contents/Resources/2.79/python --enable-shared --with-libs='/Users/bartol/src/cellblender_bundle_requirements/install_dir/lib/libiconv.a /Users/bartol/src/cellblender_bundle_requirements/install_dir/lib/libintl.a /Users/bartol/src/cellblender_bundle_requirements/install_dir/lib/libssl.a /Users/bartol/src/cellblender_bundle_requirements/install_dir/lib/libtls.a'
#
#      d) make
#      e) make install
#
#  6) Install required Python modules into the new Blender Python, e.g.:
#      a) ~/my_blender_dir/2.79/python/bin/python3.5 ~/my_blender_dir/2.79/python/bin/pip3.5 install requests
#      b) ~/my_blender_dir/2.79/python/bin/python3.5 ~/my_blender_dir/2.79/python/bin/pip3.5 install numpy
#      c) ~/my_blender_dir/2.79/python/bin/python3.5 ~/my_blender_dir/2.79/python/bin/pip3.5 install scipy
#      d) ~/my_blender_dir/2.79/python/bin/python3.5 ~/my_blender_dir/2.79/python/bin/pip3.5 install matplotlib
#      e) ~/my_blender_dir/2.79/python/bin/python3.5 ~/my_blender_dir/2.79/python/bin/pip3.5 install PyDSTool
#      f) ~/my_blender_dir/2.79/python/bin/python3.5 ~/my_blender_dir/2.79/python/bin/pip3.5 install lxml
#      g) ~/my_blender_dir/2.79/python/bin/python3.5 ~/my_blender_dir/2.79/python/bin/pip3.5 install pyyaml
#      h) ~/my_blender_dir/2.79/python/bin/python3.5 ~/my_blender_dir/2.79/python/bin/pip3.5 install MeshPy
#      i) ~/my_blender_dir/2.79/python/bin/python3.5 ~/my_blender_dir/2.79/python/bin/pip3.5 install python-libsbml
#  7) Build and Install CellBlender
#  8) Build and install GAMer
#  9) Build and install MCell
# 10) Install Bionetgen


