SUBDIRS = limited_python limited_cpp

.PHONY: all
all: subdirs


.PHONY: subdirs $(SUBDIRS)
subdirs: makefile $(SUBDIRS)

$(SUBDIRS):
	$(MAKE) -C $@


.PHONY: clean
clean:
	(cd limited_python ; make clean)
	-(cd limited_cpp ; make clean)

