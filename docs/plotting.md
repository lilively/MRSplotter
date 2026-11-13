# Plot layouts

## Superimposed plots

All selected cases are shown on a single plot, with colors indicating their labels (Figure 22).

![Superimposed plot style](img/fig22-superimposed.png)

*Figure 22. Superimposed layout.*

## Subplots

Each label is rendered on its own plot within an automatically configured grid layout (Figure 23).

![Subplot plot style](img/fig23-subplots.png)

*Figure 23. Subplot layout.*

The grid dimensions can be customized with the settings button (gear icon); see [Configure the grid size](#configure-the-grid-size-for-subplots).

### Configure the grid size for subplots

The default subplot configuration uses up to three columns, adding rows as needed to fit all plots. To change the grid dimensions, click the gear icon to open the grid configuration dialog (Figure 24). Uncheck the automatically determined grid layout option to edit the number of rows and columns. This lets you arrange the layout according to the number of spectra and your display preferences.

![Configure grid window](img/fig24-configure-grid.png){width="350"}

*Figure 24. Configure grid window.*

## Multivoxel grid

Available only for multivoxel cases. Displays the processed spectra for all voxels using the original grid dimensions from the source file (Figure 25). When multiple files are selected, only the first case is displayed by default, though additional cases can be [exported](exporting.md#export-multivoxel-grids).

![Multivoxel plot style](img/fig25-multiv.png)

*Figure 25. Multivoxel layout.*
