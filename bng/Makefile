SHELL = /bin/sh
BUILD = ./build
DIST = ./dist

.PHONY: all install clean


all: 
	if ! test -d pyinstaller2 ; then \
		unzip pyinstaller2.zip;   \
	fi ;
	python pyinstaller2/pyinstaller.py sbml2json.spec;




install:
ifeq ($(OS),Windows_NT)
    ifeq ($(shell uname -o),Cygwin)
	    cp  ${DIST}/sbml2json ./bin/sbml2json.exe;
    else
	    cp  ${DIST}/sbml2json.exe ./bin/sbml2json.exe;
    endif
else
	cp  ${DIST}/sbml2json ./bin/sbml2json;
endif

	
clean:
	if test -d ${BUILD} ; then \
	    rm -rf ${BUILD} ;          \
	fi ;
	if test -d ${DIST} ; then \
	    rm -rf ${DIST} ;          \
	fi ;

	find . -name '*.pyc' -delete
	if test -d pyinstaller2 ; then \
	    rm -rf pyinstaller2 ;          \
	fi ;		