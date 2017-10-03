UNAME_S := $(shell uname -s)
ifeq ($(UNAME_S),Linux)
	SUBDIRS = command_line open_gl java java_object
else
	SUBDIRS = command_line java java_object
endif

.PHONY: all
all: subdirs

.PHONY: subdirs $(SUBDIRS)
subdirs: makefile $(SUBDIRS)

$(SUBDIRS):
	-$(MAKE) -C $@

.PHONY: clean
clean:
	-(cd java ; make clean)
	-(cd open_gl ; make clean)


