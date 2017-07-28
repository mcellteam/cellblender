
INSTALL_DIR = ~/.config/blender/2.76/scripts/addons/io_mesh_import_mcell_mdl/

SHELL = /bin/sh
OBJS = mdllex.flex.o mdlparse.bison.o mdlmesh_parser.o vector.o mdlmesh_parser_wrap.o

_mdlmesh_parser.so: makefile setup.py mdlobj.py mdllex.flex.c mdlparse.bison.c mdlmesh_parser.c mdlmesh_parser.i vector.c mdlmesh_parser_wrap.c 
	python3.5 setup.py build_ext

mdllex.flex.c mdllex.flex.h: mdllex.l
	flex -Crema mdllex.l

mdlparse.bison.c mdlparse.bison.h: mdlparse.y mdlmesh_parser.h
	bison -v --defines=mdlparse.bison.h mdlparse.y

mdlmesh_parser_wrap.c: mdlmesh_parser.i mdlmesh_parser.c mdlmesh_parser.h
#	swig -python mdlmesh_parser.i
	swig -python -py3 -nothreads mdlmesh_parser.i

clean:
	rm -rf $(OBJS) build mdllex.flex.c mdllex.flex.h mdlparse.bison.c mdlparse.bison.h mdlparse.bison.output mdlmesh_parser_wrap.c mdlmesh_parser.py mdlmesh_parser.pyc _mdlmesh_parser.so

install:
	@if [ "$(INSTALL_DIR)" ]; then \
	  if [ ! -s $(INSTALL_DIR) ]; then \
	    echo mkdir -p $(INSTALL_DIR); \
	    mkdir -p $(INSTALL_DIR); \
	  fi; \
	  echo cp __init__.py $(INSTALL_DIR); \
	  cp __init__.py $(INSTALL_DIR); \
	  echo cp _mdlmesh_parser.so $(INSTALL_DIR); \
	  cp _mdlmesh_parser.so $(INSTALL_DIR); \
	  echo cp mdlobj.py $(INSTALL_DIR); \
	  cp mdlobj.py $(INSTALL_DIR); \
	  echo cp mdlmesh_parser.py $(INSTALL_DIR); \
	  cp mdlmesh_parser.py $(INSTALL_DIR); \
	  echo cp import_mcell_mdl.py $(INSTALL_DIR); \
	  cp import_mcell_mdl.py $(INSTALL_DIR); \
	fi

