# Eye-Tracking Analysis

This repository contains a collection of Python scripts, which analyze the eye-tracking data of our fMRI experiments.

**Disclaimer 1: The code is very specific to our use case and may need substantial changes to work with other setups.**
**Disclaimer 2: I am not a Python programmer. I'm always grateful for feedback on how to improve my code.**

## Setup

The project should run in any Python 3.6 environment. It was developed with the [PyCharms IDE](https://www.jetbrains.com/pycharm/).


## Required File Names

* All files are in the `/data_raw` directory
* EyeLink eye-tracking log: `*participant_id*.asc`
* [Optional] Response: `*participant_id*_response.log`
* [Optional] Physio: `*participant_id*_physio.log`

## Work Flow ##

Before starting the Python script, prepare the data.

* Get `.edf` log file from EyeLink
* Convert `.edf` file to an ASCII-file `.asc` with EyeLink's `edf2asc`-Tool.
* Move `.asc` file to the project's `/data_raw` folder
* [Optional] Add physio and response log files according to the conventions above

Next, you can either run individual analyses or the whole pipeline via `RunPipeline.py`.



# Related Repositories

* [EyeLink Ogama Connector](https://github.com/peitek/eyelink-ogama-connector)
* [Eye-Tracking Visualization Pipeline](https://github.com/peitek/eyetracking-visualizations)


# License #

```
MIT License

Copyright (c) 2018 Norman Peitek
```