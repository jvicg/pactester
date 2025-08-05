.. pactester documentation master file, created by
   sphinx-quickstart on Mon Aug  4 20:12:48 2025.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Pactester
=========

Release |version|.

.. image:: https://img.shields.io/pypi/v/pactester.svg
    :target: https://pypi.org/project/pactester/
    :alt: Pactester latest version
    
.. image:: https://github.com/jvicg/pactester/actions/workflows/test.yml/badge.svg
    :target: https://github.com/jvicg/pactester
    :alt: CI tests status

.. image:: https://img.shields.io/pypi/pyversions/pactester.svg
    :target: https://pypi.org/project/pactester/
    :alt: Current available Python versions

.. image:: https://img.shields.io/badge/License-GPLv3-blue.svg
    :target: https://github.com/jvicg/pactester/blob/main/LICENSE
    :alt: License: GPL v3

A CLI tool to easily test PAC/WPAD files.
It provides a straightforward command-line interface to check the outgoing proxy for a given host or URL.

---------------------------------------------------------------

.. toctree::
   :caption: Contents
   :maxdepth: 1

   Home <self>
   usage
   configuration

.. note::

   This documentation is a work in progress. If you find any errors or have suggestions, please open an issue on
   `GitHub <https://github.com/jvicg/pactester/issues>`_.

Installation
------------

Pactester can be installed using pip:

.. code-block:: bash

   pip install pactester

You can also download the wheel file from the
`releases page <https://github.com/jvicg/pactester/releases>`_.

Features
--------

- Support for loading PAC/WPAD files from remote WPAD URLs or local file paths
- Configuration via config file and CLI parameters
- Optional automatic DNS checking  
- Caching for improved performance on repeated queries  
- Clear output with adjustable verbosity levels  
- Compatible with Windows and Linux  
- Verbose and debug modes

License
-------

This project is licensed under the GNU General Public License v3.0 (GPL-3.0).

You are free to use, modify, and distribute this software under the terms of the license.  
See the `LICENSE <https://github.com/jvicg/pactester/blob/main/LICENSE>`_ file for full details.
