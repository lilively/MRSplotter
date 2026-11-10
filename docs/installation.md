# Installation

## Requirements

### System requirements

- **Operating system:** Windows 10 or 11 (may work on Windows 7/8)
- **RAM:** 4 GB minimum, 8 GB+ recommended for larger datasets
- **Disk space:** at least 200 MB free
- **Permissions:** write access to the folders where you intend to save exported plots

### Python packages (when running from source)

Python 3.8 or higher with the following packages (see [`requirements.txt`](https://github.com/lilively/MRSplotter/blob/main/requirements.txt)):

- PyQt6 >= 6.4.0
- matplotlib >= 3.5.0
- numpy >= 1.21.0
- pandas >= 1.3.0
- regex >= 2022.1.18
- openpyxl >= 3.1.0

## Windows installation (standalone executable)

1. Download the latest version from the [GitHub releases page](https://github.com/lilively/MRSplotter/releases/latest).
2. Extract the contents of the ZIP file to a location of your choice.
3. Start the application by double-clicking `MRSplotter.exe`.

## Installation from source

Clone the repository to your local machine (or download it as a ZIP file and extract it):

```bash
git clone https://github.com/lilively/MRSplotter
cd MRSplotter
```

Install the dependencies:

```bash
pip install -r requirements.txt
```

Run the main script:

```bash
python main.py
```

## Supported formats

- Single-voxel files created with jMRUI2XML<sup>[1, 2](references.md)</sup>
- Multivoxel files generated with jMRUI2XML<sup>[1, 2](references.md)</sup>
- Datasets created with SpectraClassifier<sup>[3](references.md)</sup>
- Single-voxel jMRUI Data Text files created with jMRUI version 6 or 7<sup>[4](references.md)</sup>
- Multivoxel jMRUI Data Text files created with jMRUI version 6 or 7<sup>[4](references.md)</sup>
- Comma-separated values (CSV) files exported from the application
- Input data matrix exported from MRSdecomposer
