from setuptools import setup, find_packages
import os
import py_compile

"""
setup.py is used with pyproject.toml and setup.cfg to configure and install
SQL Antipattern Scanner package.

File purposes:
- setup.py: Handles package setup, compilation, and distribution.
- pyproject.toml: Specifies build system requirements, project metadata, and dependencies.
- setup.cfg: Contains additional package configuration details.

This script performs following tasks:
1. Compiles .py files to .pyc for improved runtime performance.
2. Defines packages to be included in distribution.
3. Configures package data and exclusions.
4. Calls setup() to create package based on provided configuration.

Note: Most metadata and configuration details are in pyproject.toml and setup.cfg, setup.py 
is used for custom build steps and configurations that cannot be easily specified in other 
configuration files.
"""

# Compile .py files to .pyc
for root, dirs, files in os.walk("sql_antipattern_scanner"):
    for file in files:
        if file.endswith(".py"):
            py_compile.compile(os.path.join(root, file))

# Setup configuration
setup(
    packages=find_packages(include=['sql_antipattern_scanner', 'sql_antipattern_scanner.*']),
    package_data={
        'sql_antipattern_scanner': [
            '**/*.pyc',
            'config/*.json',
            'static/*.css',
        ]
    },
    exclude_package_data={
        '': ['*.py'],
    },
)