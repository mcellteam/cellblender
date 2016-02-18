PYTHON_INCLUDE = /usr/include/python3.4m

all: _libMCell.so mcell_main

_libMCell.so: libMCell.cpp libMCell.h libMCell.i makefile
	swig -python -c++ -o libMCell_wrap.cpp libMCell.i
	g++ -c -Wno-write-strings -fpic -I. -I/usr/include libMCell_wrap.cpp libMCell.cpp -I/usr/include/python2.7 -I/usr/lib/python2.7/config
	g++ -shared -I/usr/include libMCell.o libMCell_wrap.o -o _libMCell.so
	rm -f *.o

libMCell.o: libMCell.cpp libMCell.h makefile
	g++ -c -Wno-write-strings libMCell.cpp -o libMCell.o

mcell_main.o: mcell_main.cpp libMCell.h makefile
	g++ -c -Wno-write-strings mcell_main.cpp -o mcell_main.o

mcell_main: mcell_main.o libMCell.o makefile
	g++ -lm -o mcell_main mcell_main.o libMCell.o

clean:
	rm -rf __pycache__
	rm -f *_wrap* *.pyc
	rm -f core
	rm -f *.o *.so
	rm -f libMCell.py
	rm -f mcell_main

test_py: mcell_main.py _libMCell.so
	python mcell_main.py

test_c: mcell_main
	./mcell_main proj_path=/home/bobkuczewski/proj/SWIG/downloads/swig.org/swig-3.0.8/Examples/python/class/libMCell/mcell_output data_model=dm.json


