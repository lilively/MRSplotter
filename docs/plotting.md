# Plot layouts

## Superimposed plots

All selected cases are shown on a single plot, with colors indicating their labels.

## Subplots

Each label is rendered on its own plot within an automatically configured grid layout. The grid dimensions can be customized with the settings button (gear icon); see [Configure the grid size](#configure-the-grid-size-for-subplots).

## Multivoxel grid

Available only for multivoxel cases. Displays the processed spectra for all voxels using the original grid dimensions from the source file. When multiple files are selected, only the first case is displayed by default, though additional cases can be [exported](exporting.md#export-multivoxel-grids).

## Display configuration

### Each selected spectrum

When selected, the spectrum of each case is shown, as in Figure 18.

![Each selected spectrum, superimposed](img/fig18-each-spectra.png)

*Figure 18. Each selected spectrum of the meningioma dataset (short echo) on a superimposed plot.*

### Means by tumor label

When selected, the mean spectrum of each class is shown. If **Each selected spectra** is also selected, the mean of each label is plotted with a darker and thicker version of the chosen color to avoid confusion.

### Add standard deviation

Available when **Means by tumor label** is selected (Figure 19).

![Mean and standard deviation on subplots](img/fig19-mean-sd.png)

*Figure 19. Mean and standard deviation of the meningioma dataset (short echo) on subplots.*

### Add vertical lines

Adds reference lines at key metabolite positions to make peak assessment easier. When **isBrainH** is selected, the fields are automatically filled with 1.29, 3.03, and 3.21 ppm. Up to three values can be used at the same time (Figure 20).

![Mean spectra with vertical lines](img/fig20-vertical-lines.png)

*Figure 20. Mean spectra of meningiomas with vertical lines at 3.2, 3.03, and 1.29 ppm.*

### Configure the grid size for subplots

The default subplot configuration uses up to three columns, adding rows as needed to fit all plots. To change the grid dimensions, click the gear icon to open the grid configuration dialog (Figure 21). Uncheck the automatically determined grid layout option to edit the number of rows and columns. This lets you arrange the layout according to the number of spectra and your display preferences (Figure 22).

![Configure grid window](img/fig21-configure-grid.png)

*Figure 21. Configure grid window.*

![Short echo spectra of SFTs](img/fig22-sft-subplots.png)

*Figure 22. Short echo spectra of SFTs.*
