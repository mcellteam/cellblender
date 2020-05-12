SUBDIRS =  mcell3 mcell3dm mcell3r cBNGL limited_python smoldyn248 Proto_Andreas_1


ifneq ($(OS),Windows_NT)
  # limited_cpp uses obsoleted drand48 call
  SUBDIRS_ALL = $(SUBDIRS) limited_cpp  
else
  SUBDIRS_ALL = $(SUBDIRS)
endif 

.PHONY: all
all: subdirs


.PHONY: subdirs $(SUBDIRS_ALL)
subdirs: makefile $(SUBDIRS_ALL)

$(SUBDIRS_ALL):
	$(MAKE) -C $@


.PHONY: clean
clean:
	(cd mcell3 ; make clean)
	(cd limited_python ; make clean)
	-(cd limited_cpp ; make clean)

