# Configuration file for the Sphinx documentation builder.

import os
import sys

sys.path.insert(0, os.path.abspath('..'))

from pactester import __author__, __progname__, __version__

# Project information

project = __progname__
copyright = f"2025, {__author__}"
author = __author__
version = __version__
release = __version__

# General configuration

extensions = []
templates_path = ["_templates"]
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]
html_theme = "sphinx_rtd_theme"
