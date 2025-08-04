Configuration
=============

Pactester can be configured using a configuration file named ``config.toml``.

Default configuration file locations:

- **Linux/macOS:**  
  ``~/.config/pactester/config.toml``

- **Windows:**  
  ``C:\Users\<YourUser>\AppData\Roaming\pactester\config.toml``  

Example configuration file:

.. code-block:: toml

   pac_url = "http://example.com/wpad.dat"
   pac_file = "/path/to/local/wpad.dat"
   check_dns = false
   use_cache = true
   cache_dir = "/path/to/custom/cache"
   cache_expires = 86400  # expiration time in seconds (e.g. 86400 = 24 hours)

Available options
-----------------

- ``pac_url``  
  URL to the remote PAC file.

- ``pac_file``  
  Path to a local PAC file. This overrides ``pac_url`` if specified.

- ``check_dns``  
  Boolean value: ``true`` or ``false``. Whether to check DNS resolution for hostnames.

- ``use_cache``  
  Boolean value: ``true`` or ``false``. Enable or disable caching.

- ``cache_dir``  
  Path to a custom cache directory. If not set, a default system cache location is used.

- ``cache_expires``  
  Cache expiration time in seconds.

.. note::

   Command-line arguments always take **priority** over configuration file settings.
