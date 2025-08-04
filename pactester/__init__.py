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
    __version__ = "dev"
    __author__ = "Not specified"
    __email__ = "Not specified"
    __progname__ = "Not specified"
    __progdesc__ = "Not specified"

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
