PYTHON_INCLUDE = /usr/include/python3.4m

# Linux:
INSTALL_DIR = ~/.config/blender/2.77/scripts/addons/

# Mac:
#INSTALL_DIR = ~/Library/Application\ Support/Blender/2.74/scripts/addons/


all: mcell_pipe_cpp mcell_pipe_c mcell_main_c _libMCell.so mcell_main mcell_main_c StorageClasses mcell_simple mcell_simple_count


mcell_pipe_cpp: mcell_pipe_cpp.o JSON.o makefile
	g++ -lm -o mcell_pipe_cpp mcell_pipe_cpp.o JSON.o

mcell_pipe_cpp.o: mcell_pipe_cpp.cpp JSON.h makefile
	g++ -c -std=c++11 -Wno-write-strings mcell_pipe_cpp.cpp


mcell_pipe_c: mcell_pipe_c.o JSON.o makefile
	gcc -lm -o mcell_pipe_c mcell_pipe_c.o JSON.o

mcell_pipe_c.o: mcell_pipe_c.c JSON.h makefile
	gcc -c mcell_pipe_c.c


mcell_main_c: mcell_main_c.o JSON.o makefile
	gcc -lm -o mcell_main_c mcell_main_c.o JSON.o

mcell_main_c.o: mcell_main_c.c JSON.h makefile
	gcc -c mcell_main_c.c


JSON.o: JSON.c JSON.h makefile
	gcc -o JSON.o -c JSON.c -fPIC -I$(PYTHON_INCLUDE)


rng.o: rng.cpp rng.h makefile
	g++ -o rng.o -c rng.cpp -fPIC -I$(PYTHON_INCLUDE)


StorageClasses.o: StorageClasses.cpp StorageClasses.h makefile
	g++ -g -c StorageClasses.cpp -o StorageClasses.o

StorageClasses: StorageClasses.o makefile
	g++ -g -lm -o StorageClasses StorageClasses.o


_libMCell.so: libMCell.cpp rng.cpp libMCell.h rng.h libMCell.i makefile
	swig -python -c++ -o libMCell_wrap.cpp libMCell.i
	g++ -c -Wno-write-strings -fpic -I. -I/usr/include libMCell_wrap.cpp rng.cpp libMCell.cpp -I/usr/include/python2.7 -I/usr/lib/python2.7/config
	g++ -shared -I/usr/include rng.o libMCell.o libMCell_wrap.o -o _libMCell.so

libMCell.o: libMCell.cpp libMCell.h makefile
	g++ -c -Wno-write-strings libMCell.cpp -o libMCell.o

mcell_main.o: mcell_main.cpp libMCell.h StorageClasses.h makefile
	g++ -c -Wno-write-strings mcell_main.cpp -o mcell_main.o

mcell_main: mcell_main.o rng.o JSON.o libMCell.o makefile
	g++ -lm -o mcell_main mcell_main.o rng.o JSON.o libMCell.o


mcell_simple.o: mcell_simple.cpp libMCell.h makefile
	g++ -c -Wno-write-strings mcell_simple.cpp -o mcell_simple.o

mcell_simple: mcell_simple.o rng.o JSON.o libMCell.o makefile
	g++ -lm -o mcell_simple mcell_simple.o JSON.o rng.o libMCell.o


mcell_simple_count.o: mcell_simple_count.cpp libMCell.h makefile
	g++ -c -std=c++11 -Wno-write-strings mcell_simple_count.cpp -o mcell_simple_count.o

mcell_simple_count: mcell_simple_count.o rng.o JSON.o libMCell.o makefile
	g++ -lm -o mcell_simple_count mcell_simple_count.o JSON.o rng.o libMCell.o


clean:
	rm -f mcell_pipe_cpp
	rm -f mcell_pipe_c
	rm -f mcell_main
	rm -f mcell_main_c
	rm -f StorageClasses
	rm -f mcell_simple
	rm -f mcell_simple_count
	rm -f *_wrap* *.pyc
	rm -f core
	rm -f *.o *.so
	rm -f libMCell.py
	rm -f *.class *.jar
	rm -f *~

cleansubs:
	rm -f react_data/*
	rmdir react_data
	rm -f viz_data/seed_00001/*
	rmdir viz_data/seed_00001
	rm -f viz_data/*
	rmdir viz_data
	rm -f __pycache__/*
	rmdir __pycache__

test_storage: StorageClasses
	./StorageClasses

# Alternate Implementation Test Cases (may not be part of final libMCell)

test_c: mcell_main_c
	./mcell_main_c proj_path=. data_model=dm.json

test_ppy: pure_python_sim.py
	python pure_python_sim.py proj_path=. data_model=dm.txt

# Primary Usage Test Cases - These should work with libMCell

# Note: the Python version accepts a Python data model,
#       and the C++ version accepts a JSON data model.

test_cpp: mcell_main
	./mcell_main proj_path=. data_model=dm.json

test_py: mcell_main.py _libMCell.so
	python mcell_main.py proj_path=. data_model=dm.txt

install: mcell_main mcell_main_c
	cp -v mcell_main $(INSTALL_DIR)cellblender/libMCell/
	cp -v mcell_main_c $(INSTALL_DIR)cellblender/libMCell/
