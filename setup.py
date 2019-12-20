import os
import shutil
import sys
import glob
from setuptools import setup, find_packages

def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

version = 'x.y.z'
if os.path.exists('VERSION'):
  version = open('VERSION').read().strip()

setup(
    name='validation_components',
    version=version,
    description='What Charles did next',
	long_description=read('README.md'),
    packages = ['validation_components'],
    author='Charles Nunn',
    author_email='path-help@sanger.ac.uk',
    url='https://github.com/sanger-pathogens/manifest-validator',
    scripts=glob.glob('scripts/*'),
    test_suite='nose.collector',
    tests_require=['nose >= 1.3'],
    install_requires=[
         'xlrd >= 1.2',
         #'pyfastaq >= 3.12.0'
       ],
    license='GPLv3',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience  :: Science/Research',
        'Topic :: Scientific/Engineering :: Bio-Informatics',
        'Programming Language :: Python :: 3.6 :: Only',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)'
    ],
)
