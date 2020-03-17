# Manifest Validator
A python3 tool to validate the taxonomy id and common names in a manifest spreadsheet

[![Build Status](https://travis-ci.com/sanger-pathogens/manifest-validator.svg?branch=master)](https://travis-ci.com/sanger-pathogens/manifest-validator)
[![codecov](https://codecov.io/gh/sanger-pathogens/manifest-validator/branch/master/graph/badge.svg)](https://codecov.io/gh/sanger-pathogens/manifest-validator)
[![License: GPL v3](https://img.shields.io/badge/License-GPL%20v3-brightgreen.svg)](https://github.com/sanger-pathogens/seroba/blob/master/LICENSE)
[![Docker Build Status](https://img.shields.io/docker/cloud/build/sangerpathogens/manifest-validator.svg)](https://hub.docker.com/r/sangerpathogens/manifest-validator)

## Contents
  * [Introduction](#introduction)
  * [Installation](#installation)
  * [Usage](#usage)
  * [License](#license)

## Introduction
This software is for validating the manifests generated pre-sequencing to ensure they contain accurate and matching identification information for species being studied. This should be done before the manifest is passed to operations SSR for processing.

## Installation

The way to install manifest-validator is provided below.
```
git clone https://github.com/sanger-pathogens/manifest-validator.git
cd manifest-validator
```

Running the tests
```
python3 setup.py test
```
If the tests all pass then install
```
python3 setup.py install
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
After this, follow the errors in the terminal output to clean the manifest before re-testing and submitting.


## License
Manifest-validator is free software, licensed under [GPLv3](https://github.com/sanger-pathogens/vr-codebase/blob/master/LICENSE).
