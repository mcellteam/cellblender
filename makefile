
# Linux:
INSTALL_DIR = ~/.config/blender/2.70/scripts/addons/

# Mac:
#INSTALL_DIR = ~/Library/Application\ Support/Blender/2.70/scripts/addons/

SHELL = /bin/sh
# This version worked as a shell command but not as a dependency:
#SOURCES = `python cellblender_source_info.py`

# This versoion seems to work as a dependency and a shell command:
SOURCES = $(shell python cellblender_source_info.py)

cellblender.zip: io_mesh_mcell_mdl/_mdlmesh_parser.so $(SOURCES)
	@echo Updating cellblender.zip
	@zip -q cellblender.zip $(SOURCES)

io_mesh_mcell_mdl/_mdlmesh_parser.so: io_mesh_mcell_mdl/makefile io_mesh_mcell_mdl/*.py io_mesh_mcell_mdl/*.c io_mesh_mcell_mdl/*.h io_mesh_mcell_mdl/*.l io_mesh_mcell_mdl/*.y io_mesh_mcell_mdl/*.i
	(cd io_mesh_mcell_mdl ; make)

clean:
	rm -rf cellblender.zip
	#rm -rf cellblender ### No longer needed because make only adds selected files to zip file
	(cd io_mesh_mcell_mdl ; make clean)

install: cellblender.zip
	@if [ "$(INSTALL_DIR)" ]; then \
	  unzip -o cellblender.zip -d $(INSTALL_DIR); \
	fi

