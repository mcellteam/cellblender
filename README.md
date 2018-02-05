CellBlender 1.2
===============================================================================

Introduction:
-------------------------------------------------------------------------------

CellBlender development is supported by the NIGMS-funded (P41GM103712) National
Center for Multiscale Modeling of Biological Systems (MMBioS).

CellBlender 1.2 is an addon for Blender (2.7x) to create computational cell
biology models for use in MCell and potentially other cell simulation
biophysics engines. With CellBlender, you can define molecules and reactions,
create geometric objects, define named surface regions on the objects, assign
properties to those regions, run an MCell simulation based off of the
CellBlender project, create plots of said simulation, visualize an animation of
the molecule trajectories, and render the results.

One goal for CellBlender is to provide a comprehensive model building and
visualization environment which completely encapsulates all of MCell's MDL
language in GUI form such that the user need not ever edit an MDL file by hand
(or even know that such files exist).

Installing CellBlender Addon:
-------------------------------------------------------------------------------

Note that you will not be getting the full value out of CellBlender with
Blender and this repo alone, since CellBlender also depends on many other
tools. As such, we've begun to produce what we call a *CellBlender bundle*,
which includes Blender itself, the CellBlender addon, a custom verion of Python
and necessary libraries, MCell, GAMer, and many other useful tools. To build a
bundle, please see the
[bundle_cellblender](https://github.com/mcellteam/bundle_cellblender) repo. If
you would still like to use Blender the traditional way, please continue with
these instructions.

Blender looks for addons in one of three directories, which are referred to as
**LOCAL**, **USER**, and **SYSTEM**. See this [Blender
documentation](https://docs.blender.org/manual/en/dev/getting_started/installing/configuration/directories.html)
for more information. To install in the **LOCAL** addons directory, you would
navigate to whatever directory you extracted or installed Blender. Inside of
that main Blender directory, you should find the following file path:

`./2.79/scripts/addons`

Simply place CellBlender in this addons directory, such that the full path is:

`<Blender Directory>./2.79/script/addons/cellblender`

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

The newer format adds the **"output_data"** directory directly below the **"mcell"** folder
as shown here:
```
.../some_directory/MyProject.blend                               (Blender file)
.../some_directory/MyProject_files                               (Directory of related files)
.../some_directory/MyProject_files/mcell                         (MCell-Specific files)
.../some_directory/MyProject_files/mcell/output_data             (MDL files for running MCell)
.../some_directory/MyProject_files/mcell/output_data/react_data  (Contains a Directory per seed)
.../some_directory/MyProject_files/mcell/output_data/viz_data    (Contains a Directory per seed)
```

That would be the directory layout for a run with no parameters being swept. If
any parameters are swept, then an additional subdirectory tree is inserted below
the **"output_data"** subdirectory of that tree and above the **react_data** and **viz_data**
directories. For example, if a single parameter named **"a"** were to be swept
with values of **{3.5, 3.7, and 3.8}**, then the directory structure produced by 
CellBlender would be:
```
.../some_directory/MyProject.blend                                         (Blender file)
.../some_directory/MyProject_files                                         (Directory of related files)
.../some_directory/MyProject_files/mcell                                   (MCell-Specific files)
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

If two parameters (**a** and **b**) were being swept with **a** taking values
**{3.5, 3.7, 3.8}** and **b** taking values **{100, 200}** then the directory
structure would be:
```
.../some_directory/MyProject.blend                                                   (Blender file)
.../some_directory/MyProject_files                                                   (Directory of related files)
.../some_directory/MyProject_files/mcell                                             (MCell-Specific files)
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

The first file (**"data_model.json"**) contains a JSON representation of CellBlender's
Data Model. This file describes the model and also contains all of the parameter
sweeping specifications.

The second file (**"data_layout.json"**) contains a JSON description of the data produced
by the run. It can be used by CellBlender and other applications to navigate the
directory structure and know the values used for each parameter in the output data
directory tree. Here's the "data_layout.json" file for the previous example where two
parameters (**a** and **b**) are being swept with **a** taking values **{3.5, 3.7, 3.8}**
and **b** taking values **{100, 200}** and 3 seeds **{1, 2, 3}**:
```
{
  "version": 0,
  "data_layout": [
    ["/DIR", ["output_data"]],
    ["a", [3.5, 3.7, 3.8]],
    ["b", [100, 200]],
    ["/FILE_TYPE", ["react_data", "viz_data"]],
    ["/SEED", [1, 2, 3]]
  ]
}
```

This file facilitates automated processing of the output_data tree with the implied
assumption that the data is "hyper-rectangular".

These two files (**data_model.json** and **data_layout.json**) allow a relatively
simple program (or script) to make use of CellBlender's parameters sweeping output
for a variety of purposes. At the present time, they are used by CellBlender for
plotting and visualization. They are also being used to integrate MCell into Galaxy.

Note that the **data_layout.json** specification is still under development. It may
be redefined so that the special keys of "/DIR" and "/FILE_TYPE" are changed to names
or symbols that are not legal MCell parameter names. Note also that the "/DIR" level
provides flexibility to change the name "output_data" to some other name or eliminate
that directory layer altogether.
