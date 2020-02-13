# Manifest Validator
A python3 library to validate the taxonomy id and common names in a manifest spreadsheet

[![Build Status](https://travis-ci.com/sanger-pathogens/manifest-validator.svg?branch=master)](https://travis-ci.com/sanger-pathogens/manifest-validator)
[![codecov](https://codecov.io/gh/sanger-pathogens/manifest-validator/branch/master/graph/badge.svg)](https://codecov.io/gh/sanger-pathogens/manifest-validator)
[![License: GPL v3](https://img.shields.io/badge/License-GPL%20v3-brightgreen.svg)](https://github.com/sanger-pathogens/seroba/blob/master/LICENSE)   

## Contents (edit as fit)
  * [Introduction](#introduction)
  * [Installation](#installation)
    * [Required dependencies](#required-dependencies)
    * [Docker](#docker)
    * [From Source](#from-source)
  * [Usage](#usage)
  * [License](#license)

## Introduction
This software is for validating the manifests generated after sequencing to ensure they contain accurate and matching identification information for species being studied. This should be done before the manifest is passed to operations SSR for processing.

## Installation
Manifest-validator has the following dependencies:

### Required dependencies
```
Python 3.6.9
```

The ways to install manifest-validator and details are provided below. If you encounter an issue when installing manifest-validator please email us at path-help@sanger.ac.uk.

### Docker
WIP

### From Source
```
python3 -m venv manifest_validator
source manifest_validator/bin/activate
git clone https://github.com/sanger-pathogens/manifest-validator.git
```

Running the tests
```
python3 setup.py test
```
If the tests all pass then install
```
cd manifest-validator
pip install .
```

### Uninstallation
To uninstall manifest-validator obtained from the source use the following commands.
```
source manifest_validator/bin/activate
pip uninstall manifest-validator
```
## Usage
```
positional arguments:
  spreadsheet  Manifest spreadsheet to be checked for matching taxon and
               common name

optional arguments:
  -h, --help   show this help message and exit

  manifest-validator path/spreadsheet.xlsx
```

Enter the command as shown above, replacing 'path/spreadsheet.xlsx' with your own manifest.spreadsheet
After this, follow the errors in the terminal output to clean the manifest before retesting and submitting.


## License
Manifest-validator is free software, licensed under [GPLv3](https://github.com/sanger-pathogens/vr-codebase/blob/master/LICENSE).
