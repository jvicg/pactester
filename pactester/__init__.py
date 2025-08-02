#!/usr/bin/env python3

from importlib.metadata import metadata

try:
    meta = metadata("pactester")
    __version__ = meta["version"]
    __author__ = meta["Author-email"]
except Exception:
    __version__ = "dev"
    __author__ = "Not specified"

__progname__ = "pactester"
__progdesc__ = """
Command-line tool to check proxy resolution using WPAD/PAC files.
"""
__progepilog__ = """
examples:
  pactester example.com
  pactester -u http://example.com/wpad.dat example.com intranet.local
  pactester -f ./wpad.dat --check--dns --verbose test.example.com
"""

__all__ = [
    "__version__",
    "__author__",
    "__progname__",
    "__progdesc__",
    "__progepilog__",
]
