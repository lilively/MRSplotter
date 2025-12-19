<h1><img src="resources\icon-512x512.png" alt="MRS Plotter Logo" height="32" style="vertical-align: middle;"> MRSPlotter 1.0</h1>

**Developed by:** Lili Fanni Tóth at MIDAlab, Institute of Biotechnology
and Biomedicine (IBB), Universitat Autònoma de Barcelona (UAB)

**Contact:**
[lilifanni.toth@uab.cat](mailto:LiliFanni.Toth@uab.cat)**,**
<margarita.julia@uab.cat>

**Overview:**

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

**Requirements**

- Operating System: Windows 10 or 11 (may work on Windows 7/8)
- RAM: Minimum 4GB recommended (8GB+ for larger datasets)
- Disk Space: At least 200MB free space
- Permissions: Write access to folders where you intend to save exported plots
- Python 3.7 or higher
- Required Python Libraries:
    - PyQt5
    - Matplotlib
    - NumPy
    - Pandas
    - lxml
    - seaborn
    - openpyxl
    - scipy
    - scikit-learn
    - statsmodels
    - adjustText
    - tifffile
    - pillow
    - python-pptx
    - docx
    - xlrd

**Windows Installation**

Download the latest executable from the [Releases page](https://github.com/lilively/MRSPlotter/releases).

Extract the contents of the MRSPlotter compressed archive and execute the MRSPlotter.exe file.

**Installation from Source**

Clone the repository from GitHub to your local machine:
```bash
git clone https://github.com/lilively/MRSPlotter
```

Navigate to the project directory and run the main script:
```bash
python main.py
```
