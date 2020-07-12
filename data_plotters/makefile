SUBDIRS = java_plot

.PHONY: all
all: subdirs

.PHONY: subdirs $(SUBDIRS)
subdirs: makefile $(SUBDIRS)

$(SUBDIRS):
	-$(MAKE) -C $@

.PHONY: clean
clean:
	-(cd java_plot ; make clean)


