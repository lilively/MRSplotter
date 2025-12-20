<!-- # MRSPlotter -->


[![DOI](https://img.shields.io/badge/DOI-1https://doi.org/10.5281/zenodo.17987686-383B96?style=for-the-badge)](https://doi.org/10.5281/zenodo.17987686)  [![License: CC BY-NC-ND 4.0 Plus](https://img.shields.io/badge/License-CC_BY--NC--ND_4.0_Plus-383B96?style=for-the-badge)](https://creativecommons.org/licenses/by-nc-nd/4.0)

<h1><img src="resources\icon-512x512.png" alt="MRS Plotter Logo" height="60" style="vertical-align: middle;"> MRSPlotter</h1>

<!-- <h1><img src="resources\icon-512x512.png" alt="MRS Plotter Logo" height="150" style="vertical-align: middle;"> </h1> -->

Open source software for visualizing and generating publication-ready plots from processed <sup>1</sup>H magnetic resonance spectroscopy data.


Full software documentation can be found [here](MRS%20Plotter%20Instructions.pdf).
 
# Overview

MRSPlotter is a specialized software tool for the visualization and
generating publication-ready plots from jMRUI text format or the
standardized XML format produced by jMRUI2XML. . The application
supports loading both single- and multivoxel files containing spectral
data, viewing, editing, and exporting the data in CSV format. This
allows for modifications, such as filling in missing information, before
using the created CSV file as input data. Additionally, MRSPlotter
enables the generation of various plot types, including subplots and
superimposed plots, and facilitates the export of visualizations for
publications and presentations.


## Windows Installation

Download the latest release from the GitHub releases page. Extract the contents of the ZIP file to a desired location on your computer. Navigate to the extracted folder and run `MRSPlotter.exe` to launch the application.

[![Download](https://img.shields.io/badge/Download_Latest_Release-383B96?style=for-the-badge)](https://github.com/lilively/MRSPlotter/releases/latest)


## Installation from Source
The software can also be run from source using Python. Ensure you have Python 3.8 or higher installed. The simplest way to obtain the program is downloading the source code as a ZIP file from this repository and extracting it, or cloning with git.

Clone the repository from GitHub to your local machine:
```bash
git clone https://github.com/lilively/MRSPlotter
```
Navigate to the project directory and run the main script:
```bash
python main.py
```


## Requirements

### System Requirements
- **Operating System:** Windows 10 or 11 (may work on Windows 7/8)
- **RAM:** 4GB minimum, 8GB+ recommended for larger datasets
- **Disk Space:** 200MB minimum
- **Permissions:** Write access for saving plots

### For Python Installation

**Python 3.8+** with the following packages (see [requirements.txt](requirements.txt)):
- PyQt6 >= 6.4.0
- matplotlib >= 3.5.0
- numpy >= 1.21.0
- pandas >= 1.3.0
- regex >= 2022.1.18

Install dependencies:
```bash
pip install -r requirements.txt
```


