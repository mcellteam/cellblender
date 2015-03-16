# Components #

  * [libMCell](libMCell.md) - C API for MCell
  * pyMCell - Python API (just a SWIG wrapper around libMCell?)
  * CellBlender - Uses pyMCell (or libMCell) to perform its work
  * MDL Parser - May end up calling the libMCell API to do its work

# Methods of Use #

  * Traditional MDL approach
  * Python "MDL" where end-user actually codes in python rather than MDL
  * C "MDL" where end-user actually codes in C rather than MDL
  * CellBlender where all model creation and simulation is done withing the Blender/CellBlender application

# Definition of "The Model" in MCell/CellBlender ? #

In a recent discussion, we raised the issue of what _is_ the model. Is it MDL? Is it a .blend file? Is it Python or C?

The current thinking is that the API interfaces (Python and C) will enable compact programmatic creation (expression) of models that are not easily expressed in the current MDL. Those compact expressions will be much more descriptive of the model than the resulting MDL files in the same way that source code is much more descriptive of an algorithm than the resulting compiled machine code. For that reason, it was suggested that the true "model" of a project cannot always be expressed in MDL, and maybe the better "true" representation would be the Python and/or C program that calls the libMCell API. If we take this approach, then it's not clear if there's a need for MDL any more.

Currently MDL fills a need for researchers who may not have the programming experience (or desire) to code their models in Python or C. However, as CellBlender becomes more capable, much of that "ease of use" functionality will be even easier through CellBlender than through direct coding of MDL. So the "ease of use" benefits of MDL are likely to diminish over time.

With those thoughts in mind, it may turn out that "The Model" is either a Python script or C program which calls the libMCell API and is either written by hand or generated automatically by CellBlender. These scripts/programs can be written by hand (without any assistance from CellBlender) or they can be generated automatically from within CellBlender as an expression of the GUI-assisted model building process.

**Note that this is still an ongoing topic of discussion!!**