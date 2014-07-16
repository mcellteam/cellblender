
# Linux:
INSTALL_DIR = ~/.config/blender/2.70/scripts/addons/

# Mac:
#INSTALL_DIR = ~/Library/Application\ Support/Blender/2.70/scripts/addons/

SHELL = /bin/sh

SOURCES = $(shell python cellblender_source_info.py)
#SUBDIRS = data_plotters io_mesh_mcell_mdl
SUBDIRS = io_mesh_mcell_mdl data_plotters

.PHONY: all
all: subdirs cellblender.zip


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
cellblender.zip: makefile $(SOURCES)
	@echo Updating cellblender.zip
	@echo Sources = $(SOURCES)
	@zip -q cellblender.zip $(SOURCES) cellblender/cellblender_id.py



.PHONY: clean
clean:
	rm -f cellblender.zip
	(cd io_mesh_mcell_mdl ; make clean)
	(cd data_plotters ; make clean)



.PHONY: install
install: cellblender.zip
	@if [ "$(INSTALL_DIR)" ]; then \
	  unzip -o cellblender.zip -d $(INSTALL_DIR); \
	fi

