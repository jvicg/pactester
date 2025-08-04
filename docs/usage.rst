Usage
=====

Pactester is a command-line tool designed to test PAC/WPAD files quickly and easily. Below are some common usage examples and explanations of available options.

Basic usage using a local PAC file:

.. code-block:: bash

   pactester -f wpad.dat example.com

This will use the default PAC file to determine the proxy for `example.com`.

Specifying a PAC file URL:

.. code-block:: bash

   pactester -u http://example.com/wpad.dat example.com intranet.local

This downloads the PAC file from the given URL and tests the specified hostnames against it.

Using a local PAC file:

.. code-block:: bash

   pactester -f ./wpad.dat example.com

This uses a local PAC file instead of downloading one.

Example with DNS check and verbose output:

.. code-block:: bash

   pactester -u http://example.com/wpad.dat --check-dns -v example.com intranet.local

This downloads the PAC file, verifies DNS resolution for each hostname, and prints verbose logs.

Available options
-----------------

- ``-u, --pac-url``  
  Specify a URL to download the PAC/WPAD file from.

- ``-f, --pac-file``  
  Use a local PAC file path instead of downloading.

- ``--check-dns``  
  Check if each hostname can be resolved via DNS before testing the proxy.

- ``--purge-cache``  
  Remove all cached PAC files and related data.

- ``-c, --cache-dir``  
  Specify a custom directory for cache storage (default is usually a system cache folder).

- ``-e, --cache-expires``  
  Set cache expiration time in seconds (e.g., 3600 for 1 hour).

- ``-n, --no-cache``  
  Disable caching entirely; always fetch fresh PAC files.

- ``-v, --verbose``  
  Increase output verbosity for more detailed logs.

- ``-vvv, --debug``  
  Enable debug mode with very detailed logging for troubleshooting.

- ``--version``  
  Display the current version of Pactester.

.. note::
   ``-pac-url`` and ``--pac-file`` are mutually exclusive. You have to choose one of them only.

-----------

For a complete list of options and their descriptions, run:

.. code-block:: bash

   pactester --help
