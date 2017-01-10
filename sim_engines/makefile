SUBDIRS = mcell pure_python

.PHONY: all
all: subdirs

.PHONY: subdirs $(SUBDIRS)
subdirs: makefile $(SUBDIRS)

$(SUBDIRS):
	$(MAKE) -C $@

.PHONY: clean
clean:
	(cd mcell ; make clean)
	(cd pure_python ; make clean)


