# TPDAnalysisToolkit
Python-based program for analysing TPD data. Currently in the alpha stage!

# Prerequisites
A python 3.x.x distribution. See https://www.python.org/downloads/ (Tested with 3.8.5)

Packages:
matplotlib

# Installation
Download the code, install missing packages via pip, and run ToolkitGUI.py

# Quickstart Guide
The workflow of the Toolkit is a two-step process:
1) Process the raw data from the .csv from into .pdat format (pdat is short for processed data). The starting screen is the "Process TPD Data" control panel. This "processing" corrects the reported temperature data from the thermocouples by correcting the slope and offset, and interpolates the data so it is available on a one-dimensional grid with a constant delta between data points. The calibration values can be adapted in RawDataWrapper.py.
2) Use the .pdat file to perform further calculations in other control panels (accessed by clicking on their names on the left side of the software). Peak integration and inversion analysis are currently functional.

Any plot can be exported as an image or as raw data (.txt extension) using the save icon at the bottom of the graph. To save the plotted data in text format either select the .txt data type from the filetype dropdown, or simply add .txt to the end of the filename in the save dialog.
