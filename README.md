<!-- # MRSplotter -->


[![DOI](https://img.shields.io/badge/DOI-10.5281/zenodo.18186338-383B96?style=for-the-badge)](https://doi.org/10.5281/zenodo.20627314)

<h1><img src="resources\icon-512x512.png" alt="MRS Plotter Logo" height="60" style="vertical-align: middle;"> MRSplotter</h1>

<!-- <h1><img src="resources\icon-512x512.png" alt="MRS Plotter Logo" height="150" style="vertical-align: middle;"> </h1> -->

Open source software for visualizing and generating publication-ready plots from processed <sup>1</sup>H magnetic resonance spectroscopy data.

### License

This project is licensed under the MIT License. See [LICENSE](LICENSE) for full details.

 
## Overview

MRSplotter is a specialized software tool designed for visualizing magnetic resonance spectroscopy data and generating publication-quality figures from various file formats. The application accommodates both single-voxel and multivoxel spectral data files. Users can view and edit the data and subsequently export it in CSV or standardized XML format. This workflow enables modifications, such as adding missing information, before using the files for plotting. MRSPlotter produces a range of plot types, including subplots and overlaid spectra, and exports figures suitable for both publication and presentation.

<h1><img src="resources\GUI.png" alt="MRS Plotter GUI" height="440" style="vertical-align: middle;"> </h1> 

*Full software documentation can be found [here](MRSplotterInstructions.pdf).*

## Windows Installation

Download the latest release from the GitHub releases page. Extract the contents of the ZIP file to a desired location on your computer. Navigate to the extracted folder and run `MRSplotter.exe` to launch the application.

[![Download](https://img.shields.io/badge/Download_Latest_Release-383B96?style=for-the-badge)](https://github.com/lilively/MRSplotter/releases/latest)


## Installation from Source
The software can also be run from source using Python. Ensure you have Python 3.8 or higher installed. The simplest way to obtain the program is downloading the source code as a ZIP file from this repository and extracting it, or cloning with git.

Clone the repository from GitHub to your local machine:
```bash
git clone https://github.com/lilively/MRSplotter
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


