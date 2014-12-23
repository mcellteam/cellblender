
# Linux:
INSTALL_DIR = ~/.config/blender/2.73/scripts/addons/

# Mac:
#INSTALL_DIR = ~/Library/Application\ Support/Blender/2.73/scripts/addons/

SHELL = /bin/sh

SOURCES = $(shell python cellblender_source_info.py)
#SUBDIRS = data_plotters io_mesh_mcell_mdl
SUBDIRS = icons io_mesh_mcell_mdl data_plotters developer_utilities

.PHONY: all
all: cellblender subdirs cellblender.zip SimControl.jar SimControl

cellblender:
	ln -s . cellblender

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


SimControl.jar: SimControl.java makefile
	rm -f *.class
	javac SimControl.java
	touch -t 201407160000 *.class
	zip -X SimControl.jar META-INF/MANIFEST.MF SimControl.java *.class
	rm -f *.class


SimControl: SimControl.o makefile
	gcc -lGL -lglut -lGLU -o SimControl SimControl.o

SimControl.o: SimControl.c makefile
	gcc -c -std=c99 -I/usr/include/GL SimControl.c


.PHONY: clean
clean:
	rm -f cellblender.zip
	rm -f SimControl.jar
	rm -f SimControl.o
	rm -f SimControl
	(cd io_mesh_mcell_mdl ; make clean)
	(cd data_plotters ; make clean)



.PHONY: install
install: cellblender.zip
	@if [ "$(INSTALL_DIR)" ]; then \
	  unzip -o cellblender.zip -d $(INSTALL_DIR); \
	fi

