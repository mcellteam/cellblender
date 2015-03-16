# CellBlender Build System #

We're using a somewhat complicated build/ID system for CellBlender and this document offers a bit of an explanation.


Our build system is complicated because we wanted the ability to "fingerprint" the version of CellBlender that any user is running so we can tell:

  1. Which version they're running (which git commit)
  1. If they've modified any files from our release

The way we accomplish this is to maintain a list (literally a Python list) of files that are part of each release. Then we can compute a hash (currently the SHA1) of each of those files to come up with an ID of the currently running version.

The list of files is maintained in "cellblender\_source\_info.py". That's the one file that we should manually update when we add or remove source files from our build. It contains a pretty obvious list of files in "cellblender\_source\_list" within the "cellblender\_info" dictionary. Here's a shortened version of what that dictionary entry looks like:
```
  "cellblender_source_list": [
    "__init__.py",
    "cellblender_source_info.py",
    "data_model.py",
    "parameter_system.py",
    "cellblender_properties.py",
    "cellblender_panels.py",
    "cellblender_operators.py",
    "cellblender_molecules.py",
    "icons"+os.sep+"cellblender_icon.png",
    "icons"+os.sep+"mol_sel.png",
    "SimControl.java",
    "glyph_library.blend",
    "io_mesh_mcell_mdl"+os.sep+"__init__.py",
    "io_mesh_mcell_mdl"+os.sep+"export_mcell_mdl.py",
    "io_mesh_mcell_mdl"+os.sep+"mdlmesh_parser.py",
    "data_plotters"+os.sep+"java_plot"+os.sep+"PlotData.jar",
    "mdl"+os.sep+"__init__.py",
    "bng"+os.sep+"__init__.py",
    "bng"+os.sep+"sbml2blender.py",
    "bng"+os.sep+"sbml2json.py",
    ],
```
The running version of CellBlender can go through that list of files to compute and report the current version that we refer to as the "CellBlender Source ID". If the user has changed any of those files, that difference will produce a different CellBlender Source ID.

But that still doesn't tell us which git commit created any particular Source ID. To accomplish that, we simply compute the Source ID at make time, and use it to update a file named "cellblender\_id.py". Here's what that entire 1-line file looks like:
```
  cellblender_id = '0e0d7fdda03628f919d1209f1f356331a2f6b501'
```
Since this file is tracked by git, we can search the git database to find any given ID in the file named "cellblender\_id.py". Here's how to do it:
```
  git log -S'0e0d7fdda03628f919d1209f1f356331a2f6b501' -- cellblender_id.py
```
In this example, that command will show something like this:
```
  commit c5a306cd21fbd9461e1870fc38f326b6312330ee
  Author: Bob Kuczewski <email address>
  Date:   Thu Sep 18 15:28:09 2014 -0700
  Reworked the panels to combine model initialization with run simulation.
```
This allows us to identify the commit used to generate any version of CellBlender that any end user might report to us.

Now on to the make file itself ...

Since we have this nice list of source files in a python list already, it makes sense to use it in the make file (rather than maintaining two separate but identical lists). We accomplish this by attaching a "main" section to the end of our "cellblender\_source\_info.py" file. That "main" section is called when cellblender\_source\_info.py is run via the python interpreter on the command line:
```
  python cellblender_source_info.py
```
When run like that, it will print (to standard out) a list of the file names contained in the cellblender\_source\_list. This is exactly what make needs. So there's a line in the make file that does this:
```
  SOURCES = $(shell python cellblender_source_info.py)
```
The $(SOURCES) variable can then be used in dependency rules and for other handy purposes (like selecting files to include in a zip file).

The moral of the story is that it's important to keep the source list (in cellblender\_source\_info.py) updated with whatever files we want in the final zip file. The ONLY file not included in that list is the SHA1 file "cellblender\_id.py" itself because that file is auto-generated to contain the SHA1 of the files in the list. It cannot be included in the SHA1 for obvious reasons (since it IS the SHA1).

There's one more wrinkle in this system related to older versions.

We've been reporting the SHA1 of the source files to the user since April 4th, 2013. So we can identify a particular version that the user is running since that time. However, we've only been storing that SHA1 in git since June 26th, 2014. This means that we can't easily search the git database for CellBlender Source IDs earlier than that. We could probably come up with some way to automatically check out each version, compute the CellBlender Source ID, and then associate that ID with the git commit ID. Fortunately, we don't have much need for that, so it hasn't been done. There are, however, a few cases where we might want to be able to associate the Source ID reported by CellBlender with a particular commit. Those are the candidate releases that we've tagged in git before June 26th, 2014. Here's that list:
```
  May 15th, 2013
  git tag: v1.0RC
  git commit:  a1abdd291b75176d6581df41329781ae5d5e1b7d
  CellBlender Source ID:  82a39aca4fb6c5b3fb455ee96896fcd4018dbf5c

  May 19th, 2013
  git tag: v1.0RC2
  git commit:  fd1bcc6194f5d7f4afda3c474331787d9d2cbd12
  CellBlender Source ID:  4ee693eb5dccc2698950ac88554d96bde9f0d7e5

  April 20th, 2014
  git tag: v1.0RC3
  git commit:  e804f0e44b792bfa04df0c55393f6433ad9a67f1
  CellBlender Source ID:  a6a38d85b6a1efb362dba46b3b07f944a49948ed
  (also released with ID:  7edb9d06a4a2f5a3ce195b2a0e9899d9b1e3fd34)
```
So if a user is running any of those versions, they should be able to report one of those Source IDs which identifies the source they're using. Any other IDs (since June 26th, 2014) can be searched directly in git:
```
  git log -S'### Source ID Here #####' -- cellblender_id.py
```