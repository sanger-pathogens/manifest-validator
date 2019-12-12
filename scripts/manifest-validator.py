#!/usr/bin/env python3

import argparse
from modules.validation import main

parser = argparse.ArgumentParser()
parser.add_argument('spreadsheet', type=str,
					help='Manifest spreadsheet to be checked for matching taxon and common name')
args = parser.parse_args()
main(args)
