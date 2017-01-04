SUBDIRS = open_gl java

.PHONY: all
all: subdirs

.PHONY: subdirs $(SUBDIRS)
subdirs: makefile $(SUBDIRS)

$(SUBDIRS):
	$(MAKE) -C $@

.PHONY: clean
clean:
	(cd java ; make clean)
	(cd open_gl ; make clean)


