PYTHON_INCLUDE = /usr/include/python3.4m

all: mcell_main_c _libMCell.so mcell_main mcell_main_c StorageClasses mcell_simple

mcell_main_c: mcell_main_c.o JSON.o makefile
	gcc -lm -o mcell_main_c mcell_main_c.o JSON.o

mcell_main_c.o: mcell_main_c.c JSON.h makefile
	gcc -c mcell_main_c.c

JSON.o: JSON.c JSON.h makefile
	gcc -o JSON.o -c JSON.c -fPIC -I$(PYTHON_INCLUDE)

StorageClasses.o: StorageClasses.cpp makefile
	g++ -g -c StorageClasses.cpp -o StorageClasses.o

StorageClasses: StorageClasses.o makefile
	g++ -g -lm -o StorageClasses StorageClasses.o


_libMCell.so: libMCell.cpp libMCell.h libMCell.i makefile
	swig -python -c++ -o libMCell_wrap.cpp libMCell.i
	g++ -c -Wno-write-strings -fpic -I. -I/usr/include libMCell_wrap.cpp libMCell.cpp -I/usr/include/python2.7 -I/usr/lib/python2.7/config
	g++ -shared -I/usr/include libMCell.o libMCell_wrap.o -o _libMCell.so

libMCell.o: libMCell.cpp libMCell.h makefile
	g++ -c -Wno-write-strings libMCell.cpp -o libMCell.o

mcell_main.o: mcell_main.cpp libMCell.h makefile
	g++ -c -Wno-write-strings mcell_main.cpp -o mcell_main.o

mcell_main: mcell_main.o JSON.o libMCell.o makefile
	g++ -lm -o mcell_main mcell_main.o JSON.o libMCell.o

mcell_simple.o: mcell_simple.cpp libMCell.h makefile
	g++ -c -Wno-write-strings mcell_simple.cpp -o mcell_simple.o

mcell_simple: mcell_simple.o JSON.o libMCell.o makefile
	g++ -lm -o mcell_simple mcell_simple.o JSON.o libMCell.o

clean:
	rm -f mcell_main
	rm -f mcell_main_c
	rm -f StorageClasses
	rm -f mcell_simple
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



test_py: mcell_main.py _libMCell.so
	python mcell_main.py

test_cpp: mcell_main
	./mcell_main data_model=dm.json

test_c: mcell_main_c
	./mcell_main_c proj_path=. data_model=dm.json

test_ppy: pure_python_sim.py
	python pure_python_sim.py proj_path=. data_model=dm.txt

test_storage: StorageClasses
	./StorageClasses
