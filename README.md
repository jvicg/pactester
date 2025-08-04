# Pactester

[![Pactester latest version](https://img.shields.io/pypi/v/pactester.svg)](https://pypi.org/project/pactester/)
[![CI tests status](https://github.com/jvicg/pactester/actions/workflows/test.yml/badge.svg)](https://github.com/jvicg/pactester/actions/workflows/tests.yml)
[![Current available Python versions](https://img.shields.io/pypi/pyversions/pactester.svg)](https://pypi.org/project/pactester/)
[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)

A CLI tool to easily test PAC/WPAD files in a cross-platform way.  
It provides a straightforward command-line interface to check the outgoing proxy for a given host or URL.

## Features

- Support for loading PAC/WPAD files from remote WPAD URLs or local file paths
- Configuration via config file and CLI parameters
- Optional automatic DNS checking  
- Caching for improved performance on repeated queries  
- Clear output with adjustable verbosity levels  
- Compatible with Windows and Linux  
- Verbose and debug modes

## Documentation

You can find the full documentation on [Read the Docs](https://pactester-docs.readthedocs.io).

## Installation

Pactester can be installed using pip:

```bash
pip install pactester
```

You can also download the wheel file from the [releases page](https://github.com/jvicg/pactester/releases/tag/v1.0.0).

## License

This project is licensed under the GNU General Public License v3.0 (GPL-3.0).

You are free to use, modify, and distribute this software under the terms of the license.  
See the [LICENSE](LICENSE) file for full details.
