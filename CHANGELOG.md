CHANGELOG
===============================================================================

Changes in 1.0.1 (since 1.0RC3)
-------------------------------------------------------------------------------

* New Features:
  * New and improved CB UI:
    * CB now presents itself in Blender's ToolShelf in the "CellBlender" tab.
    * UI buttons to show/hide sub-panels if CB UI
    * Reorganized and consolidated CB UI functions for better workflow
  * New stand-alone data model
    * Isolates persistent CB data from Blender's ID/RNA property system.
    * Allows upgrade of older CB files to newer versions of CB.
    * Allows migration of data from older data models into new data models.
    * Protects against incompatibility and CB file corruption 
  * New multi-threaded simulation runner
    * Pure python and cross-compatible with all platforms
    * Any or all queued processes may be terminated by the user
    * Icons report status of processes: queued, running, completed,
      terminated by user, or exited with errors.
    * Collects stdout and stderr as separate streams from each simulation
      process:
      * Streams stdout and stderr in real-time to console
      * Streams stdout and stderr in real-time of each process to a separate
        Blender "text" datablock, viewable in a Blender Text window.
    * Running jobs are terminated when quitting from Blender.
* Bug Fixes:
  * Many, too numerous to mention!

Changes since 0.1.52
-------------------------------------------------------------------------------

* New Features:
  * Optional initialization commands
  * Partition generation
  * Surface classes
  * Modification of surface regions by surface classes
  * Hid advanced molecule options
  * Compatible with Blender 2.66
    (Not compatible with previous versions of Blender)
  * Export of reaction and visualization data
  * Plotting of reaction data
  * Run MCell simulations from within Blender
  * Updated status system
  * Better error checking
  * New project directory layout
  * CellBlender preferences
  * MDL geometry importer implemented in c/flex/bison/swig/python
* Bug Fixes:
  * Meshes could be exported with the wrong rotation
  * Molecule positions and shapes (glyphs) could be offset on import
