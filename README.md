# EyeLinkOgamaConnector

EyeLinkOgamaConnector is a Python script, which reads converted log files from [EyeLink](http://www.sr-research.com/mount_longrange_1000plus.html) to create a .csv compatible with [Ogama](http://www.ogama.net).

**Disclaimer 1: The code is very specific to our use case and may need substantial changes to work with other setups.**
**Disclaimer 2: I am not a Python programmer. I'm always grateful for feedback on how to improve my code.**

## Setup

The project should run in any Python 3.6 environment. It was developed with the [PyCharms IDE](https://www.jetbrains.com/pycharm/).


# Conversion from EyeLink to Ogama

## Required File Names

* All files are in the same directory
* Eye tracking: `*participant_id*.asc`
* [Optional] Response: `*participant_id*_response.log`
* [Optional] Physio: `*participant_id*_physio.log`

## Work Flow ##

Before starting the Python script, prepare the data.

* Get `.edf` log file from EyeLink
* Convert `.edf` file to an ASCII-file `.asc` with EyeLink's `edf2asc`-Tool.
* Move `.asc` file to the project's `/data_raw` folder
* [Optional] Add physio and response log files according to the conventions above

Next, use EyeLinkOgamaConnector:

* Check and make necessary configuration adjustments to `OgamaConnector.py`
* Run `OgamaConnector.py`

Possible usages after everything is done:

* Import to Ogama with the output `.csv` file
* Use analysis scripts/pipeline directly on the `.csv` file (see related repositories)


# Related Repositories

* Eye-Tracking Analysis Pipeline
* Eye-Tracking Visualization Pipeline


# License #

```
MIT License

Copyright (c) 2018 Norman Peitek
```