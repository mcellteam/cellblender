
# Linux:
INSTALL_DIR = ~/.config/blender/2.70/scripts/addons/

# Mac:
#INSTALL_DIR = ~/Library/Application\ Support/Blender/2.70/scripts/addons/

SHELL = /bin/sh


cellblender.zip: io_mesh_mcell_mdl/_mdlmesh_parser.so
	mkdir -p cellblender/io_mesh_mcell_mdl/
	cp *.py cellblender/
	cp io_mesh_mcell_mdl/__init__.py cellblender/io_mesh_mcell_mdl/
	cp io_mesh_mcell_mdl/_mdlmesh_parser.so cellblender/io_mesh_mcell_mdl/
	cp io_mesh_mcell_mdl/mdlobj.py cellblender/io_mesh_mcell_mdl/
	cp io_mesh_mcell_mdl/mdlmesh_parser.py cellblender/io_mesh_mcell_mdl/
	cp io_mesh_mcell_mdl/import_mcell_mdl.py cellblender/io_mesh_mcell_mdl/
	cp io_mesh_mcell_mdl/import_mcell_mdl_pyparsing.py cellblender/io_mesh_mcell_mdl/
	cp io_mesh_mcell_mdl/import_shared.py cellblender/io_mesh_mcell_mdl/
	cp io_mesh_mcell_mdl/pyparsing.py cellblender/io_mesh_mcell_mdl/
	cp io_mesh_mcell_mdl/export_mcell_mdl.py cellblender/io_mesh_mcell_mdl/
	cp -r bng cellblender/
	cp -r data_plotters cellblender/
	cp -r mdl cellblender/
	zip -rv cellblender.zip cellblender

io_mesh_mcell_mdl/_mdlmesh_parser.so: 
	(cd io_mesh_mcell_mdl ; make)

clean:
	rm -rf cellblender.zip
	rm -rf cellblender
	(cd io_mesh_mcell_mdl ; make clean)

install: cellblender.zip
	@if [ "$(INSTALL_DIR)" ]; then \
	  unzip -o cellblender.zip -d $(INSTALL_DIR); \
	fi

