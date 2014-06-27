
# Linux:
INSTALL_DIR = ~/.config/blender/2.70/scripts/addons/

# Mac:
#INSTALL_DIR = ~/Library/Application\ Support/Blender/2.70/scripts/addons/

SHELL = /bin/sh


cellblender.zip: io_mesh_mcell_mdl/_mdlmesh_parser.so
	mkdir -p cellblender/io_mesh_mcell_mdl/
	python3 __init__.py
	cp cellblender_id.py                               cellblender/
	cp __init__.py                                     cellblender/
	cp cellblender_molecules.py                        cellblender/
	cp cellblender_operators.py                        cellblender/
	cp cellblender_panels.py                           cellblender/
	cp cellblender_properties.py                       cellblender/
	cp data_model.py                                   cellblender/
	cp object_surface_regions.py                       cellblender/
	cp parameter_system.py                             cellblender/
	cp run_simulations.py                              cellblender/
	cp utils.py                                        cellblender/
	cp io_mesh_mcell_mdl/__init__.py                   cellblender/io_mesh_mcell_mdl/
	cp io_mesh_mcell_mdl/_mdlmesh_parser.so            cellblender/io_mesh_mcell_mdl/
	cp io_mesh_mcell_mdl/mdlobj.py                     cellblender/io_mesh_mcell_mdl/
	cp io_mesh_mcell_mdl/mdlmesh_parser.py             cellblender/io_mesh_mcell_mdl/
	cp io_mesh_mcell_mdl/import_mcell_mdl.py           cellblender/io_mesh_mcell_mdl/
	cp io_mesh_mcell_mdl/import_mcell_mdl_pyparsing.py cellblender/io_mesh_mcell_mdl/
	cp io_mesh_mcell_mdl/import_shared.py              cellblender/io_mesh_mcell_mdl/
	cp io_mesh_mcell_mdl/pyparsing.py                  cellblender/io_mesh_mcell_mdl/
	cp io_mesh_mcell_mdl/export_mcell_mdl.py           cellblender/io_mesh_mcell_mdl/
	cp -r bng                                          cellblender/
	cp -r data_plotters                                cellblender/
	cp -r mdl                                          cellblender/
	cp glyph_library.blend                             cellblender/
	zip -rv cellblender.zip                            cellblender

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

