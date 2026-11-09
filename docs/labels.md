# Labels

Unique classes from the loaded files are listed in a list box in alphabetical order. Initially, random colors are assigned to each class.

Double-clicking a class opens a color picker menu, where you can assign a specific color:

- Create custom colors by clicking one of the white squares, selecting a color, and clicking **Add to Custom Colors**. Custom colors are saved, so they can be reused after closing and reopening the application.
- Colors can also be entered as hexadecimal codes, which makes it easy to replicate previous plots.

The <kbd>Ctrl</kbd>+<kbd>A</kbd> (select all) and <kbd>Ctrl</kbd>+<kbd>D</kbd> (deselect all) shortcuts also work in the label list.

## Combine labels

Custom labels can be created by combining the available labels into classes (Figure 16). Up to four classes can be created at the same time, and clicking **Combine Labels** again creates new combinations.

![Combine labels window](img/fig16-combine-labels.png)

*Figure 16. A pop-up window that allows the creation of classes from labels.*

Clicking **Reset Combinations** (Figure 17) reloads the original labels with randomly assigned colors.

![Confirm resetting the labels](img/fig17-reset-labels.png)

*Figure 17. Pop-up window for confirming resetting the labels.*

## Importing labels from MRSdecomposer results

The MRSdecomposer output files contain, for each file, the X and Y positional coordinates and the winning source contribution. Using the **Load labels** option, this file can be used to assign labels to the input file. If multiple repetitions are detected, a pop-up window prompts you to select one of them.
