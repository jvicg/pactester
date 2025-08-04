#!/usr/bin/env python3

from importlib.metadata import metadata

try:
    meta = metadata("pactester")
    __version__ = meta["Version"]
    __author__ = meta["Author"]
    __email__ = meta["Author-email"]
    __progname__ = meta["Name"]
    __progdesc__ = meta["Summary"]
except Exception:
    __version__ = "v1.0.0"
    __author__ = "Javier Correa Guerrero"
    __email__ = "jcorreag@pm.me"
    __progname__ = "pactester"
    __progdesc__ = "Command-line tool to check proxy resolution using PAC files"

__progepilog__ = f"""
examples:
  {__progname__} example.com
  {__progname__} -u http://example.com/wpad.dat example.com intranet.local
  {__progname__} -f ./wpad.dat --check--dns --verbose test.example.com
"""

__all__ = [
    "__author__",
    "__progdesc__",
    "__progepilog__",
    "__progname__",
    "__version__",
]
