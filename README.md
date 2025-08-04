# pactester

**pactester** is a command-line tool that checks which proxy is used to access a given URL or hostname according to a PAC/WPAD file.

## Requirements

- Python >= 3.8 and < 3.13

## Installation

```bash
pip install pactester
```

## Usage

```bash
pactester [-h] [-u URL | -f FILE] [-d] [-n] [-p] [-c CACHE_DIR] [-e CACHE_EXPIRES] [-v] [-vvv] [--version] hostname [hostname ...]
```
