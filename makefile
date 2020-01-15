UNAME_S := $(shell uname -s)
#ifeq ($(UNAME_S),Linux)
#	INSTALL_DIR = ~/.config/blender/2.78/scripts/addons/
##	INSTALL_DIR = ~/src/blender/Blender-2.78c-CellBlender-linux/2.78/scripts/addons/
#else
#	INSTALL_DIR = /Applications/Blender-2.78c-CellBlender/blender.app/Contents/Resources/2.78/scripts/addons/
#endif

# CellBlender will be installed here. This should typically be a link to the desired location on your platform.
# For example, on a Linux machine it might be done with: ln -s ~/.config/blender/2.78/scripts/addons/ ~/my_cellblender_link
# For example, on a MacOSX machine it might be done with: ln -s ~/Library/Application\ Support/Blender/2.78/scripts/addons/ ~/my_cellblender_link
# For example, for a link pointing into a Linux bundle: ln -s ~/src/blender/Blender-2.78c-CellBlender-linux/2.78/scripts/addons/ ~/my_cellblender_link
# For example, for a link pointing into a MacOSX bundle: ln -s /Applications/Blender-2.78c-CellBlender/blender.app/Contents/Resources/2.78/scripts/addons/ ~/my_cellblender_link

<<<<<<< HEAD
INSTALL_DIR ?= ~/my_cellblender_link/
=======
INSTALL_DIR = ~/my_cellblender_link/
>>>>>>> refs/remotes/origin/master

# Linux:
<<<<<<< HEAD
#INSTALL_DIR = ~/.config/blender/2.78/scripts/addons/
=======
#INSTALL_DIR = ~/.config/blender/2.76/scripts/addons/
>>>>>>> refs/remotes/origin/master

# Mac:
#INSTALL_DIR = ~/Library/Application\ Support/Blender/2.78/scripts/addons/
#INSTALL_DIR = /Applications/Blender-2.78c_bundle/blender.app/Contents/Resources/2.78/scripts/addons/

SHELL = /bin/sh

ifeq ($(UNAME_S),Linux)
	SUBDIRS = icons io_mesh_mcell_mdl engine_runner_combos sim_engines sim_runners data_plotters developer_utilities
else
	SUBDIRS = icons io_mesh_mcell_mdl sim_engines sim_runners data_plotters developer_utilities
endif

SOURCES = $(shell python cellblender_source_info.py)

# These are generally binary files that are built by this makefile and included in the .zip file
IOMESHFILES = cellblender/io_mesh_mcell_mdl/_mdlmesh_parser.so cellblender/io_mesh_mcell_mdl/mdlmesh_parser.py

MCELLENGINE = cellblender/sim_engines/mcell3/_mdlmesh_parser.so cellblender/sim_engines/mcell3/mdlmesh_parser.py

ifeq ($(UNAME_S),Linux)
  SIMCTLFILES = cellblender/sim_runners/java/SimControl.jar cellblender/sim_runners/open_gl/SimControl
else
  SIMCTLFILES = cellblender/sim_runners/java/SimControl.jar
endif
SIMLIBMCFILES = cellblender/sim_engines/limited_cpp/_libMCell.so cellblender/sim_engines/limited_cpp/mcell_main cellblender/sim_engines/sim_engines/limited_cpp/_libMCell.so cellblender/sim_engines/sim_engines/limited_cpp/mcell_main
PLOTTERFILES = cellblender/data_plotters/java_plot/PlotData.jar
BNGFILES = cellblender/bng/bin/sbml2json

ZIPFILES = $(SOURCES) $(IOMESHFILES) $(MCELLENGINE) $(SIMCTLFILES) $(SIMLIBMCFILES) $(PLOTTERFILES) $(BNGFILES) cellblender/cellblender_id.py

ZIPOPTS = -X -0 -D -o

.PHONY: all
all: cellblender subdirs cellblender.zip

ifeq ($(OS),Windows_NT)
	MKLINK_CMD="mklink /J cellblender ."
else
	MKLINK_CMD="ln -s . cellblender "
endif

cellblender:
	$(MKLINK_CMD) 

.PHONY: subdirs $(SUBDIRS)
subdirs: makefile $(SUBDIRS)

$(SUBDIRS):
	$(MAKE) -C $@


# https://www.gnu.org/software/make/manual/html_node/Phony-Targets.html
# A phony target should not be a prerequisite of a real target file;
# if it is, its recipe will be run every time make goes to update that file.
# As long as a phony target is never a prerequisite of a real target, the phony
# target recipe will be executed only when the phony target is a specified goal
#  (see Arguments to Specify the Goals). 

# Note that files which auto-change but are included in the zip file are not part of the source list
cellblender.zip: cellblender $(SOURCES)
	@echo Updating cellblender.zip
	touch -t 201502050000 cellblender_id.py
	@zip $(ZIPOPTS) cellblender.zip $(ZIPFILES)


.PHONY: clean
clean:
	rm -f cellblender.zip
	(cd io_mesh_mcell_mdl ; make clean)
	-(cd engine_runner_combos ; make clean)
	-(cd sim_engines ; make clean)
	-(cd sim_runners ; make clean)
	-(cd data_plotters ; make clean)

id:
	@echo ===========================================================
	@cat cellblender_id.py
	@echo Installation path:
	@echo $(INSTALL_DIR)cellblender
	@echo Real Installation path:
	@realpath $(INSTALL_DIR)cellblender
	@echo ===========================================================

.PHONY: install
install: cellblender.zip
	@if [ "$(INSTALL_DIR)" ]; then \
	  unzip -o cellblender.zip -d $(INSTALL_DIR); \
	fi
	@echo ===========================================================
	@cat $(INSTALL_DIR)/cellblender/cellblender_id.py
	@echo ===========================================================

