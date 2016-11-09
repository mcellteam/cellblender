CellBlender 1.0.1
===============================================================================

Introduction:
-------------------------------------------------------------------------------

CellBlender development is supported by the NIGMS-funded (P41GM103712) National
Center for Multiscale Modeling of Biological Systems (MMBioS).

CellBlender is an addon for Blender (2.6x-2.7x) to create computational cell
biology models for use in MCell and potentially other cell simulation
biophysics engines. In CellBlender 1.0.1 you can define molecules and
reactions, create geometric objects, define named surface regions on the
objects, assign properties to those regions, run an MCell simulation based off
of the CellBlender project, create plots of said simulation, visualize an
animation of the molecule trajectories, and render the results. MDL import
currently only supports mesh data, but full support will be added in future
versions of CellBlender.

One goal for CellBlender is to provide a comprehensive model building and
visualization environment which completely encapsulates all of MCell's MDL
language in GUI form such that the user need not ever edit an MDL file by hand
(or even know that such files exist). CellBlender is already nearly feature
complete with respect to MCell, but there may still be a few minor ones missing
for now.

Installing CellBlender Addon:
-------------------------------------------------------------------------------

Startup Blender and go to the **File->User Preferences** menu. In the **User
Preferences** control panel choose the **Addons** tab. Click the **Install from
File** button at the bottom of the window. Navigate to the unextracted zip file
that you downloaded (cellblender_v1.0.1.zip), select it, and click the
**Install from File** button near the upper-right hand corner.

Activating CellBlender Addon in Blender:
-------------------------------------------------------------------------------

In the **Addons** panel scroll down till you see **Cell Modeling: CellBlender**
and check the check box to enable it. Then click **Save as Default** to enable
the addon permanently in Blender for any future projects you make.

Using CellBlender:
-------------------------------------------------------------------------------

For detailed instructions with images, please see http://mcell.org/tutorials/.
If you have any questions about CellBlender, feel free to ask us at
http://mmbios.org/index.php/mcell-cellblender-forum/.

Additional notes:
-------------------------------------------------------------------------------

If you are hand-editing MDLs, note that **CELLBLENDER** mode **VIZ_OUTPUT**
will output molecules but will not output meshes. We assume that your meshes
are already present in your CellBlender/Blender project. The philosophy here is
that the CellBlender/Blender project IS your MCell project and that the MCell
compute kernel is a physics engine driving the dynamics of objects created and
visualized in Blender.

Depending on your graphics hardware beware, of exporting more than 10000
molecules or so, if you want good performance (>10 frames per second) in
CellBlender playback. But if your goal is to render a movie you should be able
to export and render many 100s of thousands of molecules per frame with
CellBlender. 


Parameter Sweeping:
-------------------------------------------------------------------------------

Some newer versions of **CELLBLENDER** support parameter sweeping via controls
in the "Parameters" panel. This creates a subdirectory tree structure containing
many different MCell runs.

In order to contain the potentially large number of directories produced, these
newer versions of CellBlender put all generated output into the "output_data"
subdirectory below the "mcell" folder. Older (non-sweeping) versions did not add
this extra subdirectory layer. Those older versions used the following standard
directory tree for a Blender file named "**MyProject.blend**" in **some_directory**:
```
.../some_directory/MyProject.blend                   (Blender file)
.../some_directory/MyProject_files                   (Directory of related files)
.../some_directory/MyProject_files/mcell             (MDL files for running MCell)
.../some_directory/MyProject_files/mcell/react_data  (Contains a Directory per seed)
.../some_directory/MyProject_files/mcell/viz_data    (Contains a Directory per seed)
```

The newer format adds the "output_data" directory directly below the "mcell" folder
as shown here:
```
.../some_directory/MyProject.blend                               (Blender file)
.../some_directory/MyProject_files                               (Directory of related files)
.../some_directory/MyProject_files/mcell/output_data             (MDL files for running MCell)
.../some_directory/MyProject_files/mcell/output_data/react_data  (Contains a Directory per seed)
.../some_directory/MyProject_files/mcell/output_data/viz_data    (Contains a Directory per seed)
```

That would be the directory layout for a run with no parameters being swept. If
any parameters are swept, then an additional subdirectory tree is inserted below
the "output_data" subdirectory of that tree and above the react_data and viz_data
directories. For example, if a single parameter named **"a"** were to be swept
with values of **{3.5, 3.7, and 3.8}**, then the directory structure produced by 
CellBlender would be:
```
.../some_directory/MyProject.blend                                         (Blender file)
.../some_directory/MyProject_files                                         (Directory of related files)
.../some_directory/MyProject_files/mcell/output_data                       (Files related to running MCell)
.../some_directory/MyProject_files/mcell/output_data/a_index_0             (MDL files for a=3.5)
.../some_directory/MyProject_files/mcell/output_data/a_index_0/react_data  (Contains a Directory per seed)
.../some_directory/MyProject_files/mcell/output_data/a_index_0/viz_data    (Contains a Directory per seed)
.../some_directory/MyProject_files/mcell/output_data/a_index_1             (MDL files for a=3.7)
.../some_directory/MyProject_files/mcell/output_data/a_index_1/react_data  (Contains a Directory per seed)
.../some_directory/MyProject_files/mcell/output_data/a_index_1/viz_data    (Contains a Directory per seed)
.../some_directory/MyProject_files/mcell/output_data/a_index_2             (MDL files for a=3.8)
.../some_directory/MyProject_files/mcell/output_data/a_index_2/react_data  (Contains a Directory per seed)
.../some_directory/MyProject_files/mcell/output_data/a_index_2/viz_data    (Contains a Directory per seed)
```

If two parameter (**a** and **b**) were being swept with **a** taking values
**{3.5, 3.7, 3.8}** and **b** taking values **{100, 200}** then the directory
structure would be:
```
.../some_directory/MyProject.blend                                                   (Blender file)
.../some_directory/MyProject_files                                                   (Directory of related files)
.../some_directory/MyProject_files/mcell/output_data                                 (Files related to running MCell)
.../some_directory/MyProject_files/mcell/output_data/a_index_0                       (Directory for a=3.5)
.../some_directory/MyProject_files/mcell/output_data/a_index_0/b_index_0             (MDL files for a=3.5, b=100)
.../some_directory/MyProject_files/mcell/output_data/a_index_0/b_index_0/react_data  (Contains a Directory per seed)
.../some_directory/MyProject_files/mcell/output_data/a_index_0/b_index_0/viz_data    (Contains a Directory per seed)
.../some_directory/MyProject_files/mcell/output_data/a_index_0/b_index_1             (MDL files for a=3.5, b=200)
.../some_directory/MyProject_files/mcell/output_data/a_index_0/b_index_1/react_data  (Contains a Directory per seed)
.../some_directory/MyProject_files/mcell/output_data/a_index_0/b_index_1/viz_data    (Contains a Directory per seed)
.../some_directory/MyProject_files/mcell/output_data/a_index_1                       (Directory for a=3.7)
.../some_directory/MyProject_files/mcell/output_data/a_index_1/b_index_0             (MDL files for a=3.7, b=100)
.../some_directory/MyProject_files/mcell/output_data/a_index_1/b_index_0/react_data  (Contains a Directory per seed)
.../some_directory/MyProject_files/mcell/output_data/a_index_1/b_index_0/viz_data    (Contains a Directory per seed)
.../some_directory/MyProject_files/mcell/output_data/a_index_1/b_index_1             (MDL files for a=3.7, b=200)
.../some_directory/MyProject_files/mcell/output_data/a_index_1/b_index_1/react_data  (Contains a Directory per seed)
.../some_directory/MyProject_files/mcell/output_data/a_index_1/b_index_1/viz_data    (Contains a Directory per seed)
.../some_directory/MyProject_files/mcell/output_data/a_index_2                       (Directory for a=3.8)
.../some_directory/MyProject_files/mcell/output_data/a_index_2/b_index_0             (MDL files for a=3.8, b=100)
.../some_directory/MyProject_files/mcell/output_data/a_index_2/b_index_0/react_data  (Contains a Directory per seed)
.../some_directory/MyProject_files/mcell/output_data/a_index_2/b_index_0/viz_data    (Contains a Directory per seed)
.../some_directory/MyProject_files/mcell/output_data/a_index_2/b_index_1             (MDL files for a=3.8, b=200)
.../some_directory/MyProject_files/mcell/output_data/a_index_2/b_index_1/react_data  (Contains a Directory per seed)
.../some_directory/MyProject_files/mcell/output_data/a_index_2/b_index_1/viz_data    (Contains a Directory per seed)
```

In addition to these output files, two additional files are produced
during a typical run:
```
.../some_directory/MyProject_files/mcell/data_model.json    (JSON CellBlender Data Model)
.../some_directory/MyProject_files/mcell/data_layout.json   (JSON description of directory tree)
```

The first file ("data_model.json") contains a JSON representation of CellBlender's
Data Model. This file describes the model and also contains all of the parameter
sweeping specifications.

The second file ("data_layout.json") contains a JSON description of the data produced
by the run. It can be used by CellBlender and other applications to navigate the
directory structure and know the values used for each parameter in the output data
directory tree. Here's the "data_layout.json" file for the previous example where two
parameters (**a** and **b**) are being swept with **a** taking values **{3.5, 3.7, 3.8}**
and **b** taking values **{100, 200}**:
```
{
  "version": 0,
  "data_layout": [
    ["dir", ["output_data"]],
    ["a", [3.5, 3.7, 3.8]],
    ["b", [100, 200]],
    ["file_type", ["react_data", "viz_data"]],
    ["SEED", [1, 2, 3]]
  ]
}
```

This file facilitates automated processing of the output_data tree with the implied
assumption that the data is "hyper-rectangular".

Using these two files (**data_model.json** and **data_layout.json**) a relatively
simple program (or script) can make use of CellBlender's parameters sweeping output.
