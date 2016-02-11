PYTHON_INCLUDE = /usr/include/python3.4m

all: mcell_main mcell_main_cpp _libMCell_cpp.so

mcell_main: mcell_main.c libMCell.c libMCell.h libMCell.i JSON.o makefile
	gcc -c mcell_main.c libMCell.c
	gcc -lm -o mcell_main mcell_main.o libMCell.o JSON.o
	swig -python libMCell.i
	gcc -c libMCell.c libMCell_wrap.c -fPIC -I$(PYTHON_INCLUDE)
	ld -lm -shared libMCell.o libMCell_wrap.o JSON.o -o _libMCell.so

JSON.o: JSON.c JSON.h makefile
	gcc -o JSON.o -c JSON.c -fPIC -I$(PYTHON_INCLUDE)

clean:
	rm -f libMCell.py
	rm -f libMCell_wrap.c
	rm -f mcell_main
	rm -f mcell_main_cpp
	rm -f libMCell_cpp.py
	rm -f libMCell_cpp_wrap.cpp
	rm -f *.o
	rm -f *.so
	rm -f *.pyc
	rm -f *~
	rm -f __pycache__/*
	rmdir __pycache__
	rm -f react_data/*
	rmdir react_data
	rm -f viz_data/seed_00001/*
	rmdir viz_data/seed_00001
	rm -f viz_data/*
	rmdir viz_data

install: libMCell.py mcell_python.py mcell_main _libMCell.so makefile 
	cp libMCell.py ~/.config/blender/2.76/scripts/addons/cellblender/libMCell/
	cp mcell_python.py ~/.config/blender/2.76/scripts/addons/cellblender/libMCell/
	cp mcell_main ~/.config/blender/2.76/scripts/addons/cellblender/libMCell/
	cp _libMCell.so ~/.config/blender/2.76/scripts/addons/cellblender/libMCell/
	cp makefile ~/.config/blender/2.76/scripts/addons/cellblender/libMCell/


test_c: mcell_main
	./mcell_main proj_path=. data_model=dm.json

test_py: mcell_python.py mcell_main
	python3 mcell_python.py proj_path=. data_model=dm.txt


# These are the C++ versions being added

mcell_main_cpp.o: mcell_main_cpp.cpp libMCell_cpp.h makefile
	g++ -o mcell_main_cpp.o -c mcell_main_cpp.cpp

libMCell_cpp.o: libMCell_cpp.cpp libMCell_cpp.h makefile
	g++ -o libMCell_cpp.o -c libMCell_cpp.cpp

mcell_main_cpp: mcell_main_cpp.o libMCell_cpp.o libMCell.o JSON.o makefile
	g++ -o mcell_main_cpp mcell_main_cpp.o libMCell.o libMCell_cpp.o JSON.o

_libMCell_cpp.so: setup.py libMCell_cpp.i libMCell_cpp.h libMCell_cpp.cpp makefile
	python setup.py build_ext --inplace

test_cpp: mcell_main_cpp
	./mcell_main_cpp proj_path=. data_model=dm.json

#test_cpp_py: mcell_main_cpp.py _libMCell_cpp.so _libMCell.so
test_cpp_py: mcell_main_cpp.py _libMCell_cpp.so
	python setup.py build_ext --inplace
	python mcell_main_cpp.py proj_path=. data_model=dm.txt

