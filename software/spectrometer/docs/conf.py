# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

import sphinx_rtd_theme
from spectrometer import __about__
import os
import sys

sys.path.insert(0, os.path.abspath("."))  # feels like a hack

project = "magnETHical"
copyright = "2023, Maximilian Stabel"
author = "Maximilian Stabel"
release = __about__.__version__

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    "myst_nb",  # Jupyter Notebook support, loads myst_parser - don't include separately
    "sphinx.ext.napoleon",  # Google Style docstrings, load before autodoc
    "sphinx.ext.duration",
    "sphinx.ext.doctest",
    "sphinx.ext.autodoc",  # auto generate API Reference
    "sphinx.ext.autosummary",
    "sphinx.ext.intersphinx",
    "sphinx.ext.mathjax",  # LaTeX Math in docstring
]
myst_enable_extensions = ["html_image"]
source_suffix = {
    ".rst": "restructuredtext",
    ".ipynb": "myst-nb",
    ".myst": "myst-nb",
    ".md": "myst-nb",
}

templates_path = ["_templates"]
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]

# Don't execute notebooks
nb_execution_mode = "off"


# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = "sphinx_rtd_theme"  # default: alabaster
html_static_path = [
    "_static"  # [sphinx_rtd_theme.get_html_theme_path()]  # default: _static
]
