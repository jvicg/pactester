#!/usr/bin/env python3

import os
import re
import sys
import time
import socket
import logging
import argparse
import requests
from hashlib import sha1

import pacparser

from pactester.config import Cache, Config
from pactester import (
    __version__,
    __progname__,
    __progdesc__,
    __progepilog__
)


SUCCESS = 0
ERR_NO_PAC_FILE = 1
ERR_NO_DATA_PROVIDED = 2
ERR_UNABLE_TO_DOWNLOAD_PAC = 3
ERR_COULD_NOT_PARSE_PAC_FILE = 4

logger = logging.getLogger(__name__)

def gen_sha_hash(s: str, length: int = 16) -> str:
    """
    Generate a SHA256 hash based on a string.

    Args:
        s (str): String input.
        length (int, optional): Length of the output string.

    Returns:
        str: Hashed string.
    """
    return sha1(s.encode("utf-8")).hexdigest()[:length]

def gen_pac_file_based_on_url(wpad_url: str) -> str:
    """
    Generate a PAC file based on the URL hash. This will store an unique name for each PAC url.

    Args:
        wpad_url (str): PAC file URL.

    Returns:
        Path: Object with the file.
    """
    return gen_sha_hash(wpad_url)

def gen_pac_file_based_on_timestamp(wpad_file: str) -> str:
    """
    Generate a cache filename for the formatted WPAD file based on the original file path and last modification time.

    Args:
        wpad_file (str): Path to the WPAD.
    
    Returns:
        Path: Object with the file.
    """
    stat = os.stat(wpad_file)
    unique_str = f"{wpad_file}:{stat.st_mtime}"
    return gen_sha_hash(unique_str)

def format_wpad_file(wpad_file: str, cache: Cache, use_cache: bool = True) -> str:
    """
    Properly format PAC file as utf-8-sig.
    
    Args:
        wpad_file (str): Path to the PAC file.
        cache (Path): Cache object.
        use_cache (bool, optional): Use cached files.

    Returns:
        str: Path of the file.
    """
    cache_file = cache.dir / gen_pac_file_based_on_timestamp(wpad_file)

    if cache_file.exists() and use_cache:
        logger.info(f"Using cached formatted WPAD file: '{cache_file}'")
        return str(cache_file)

    with open(wpad_file, "r", encoding="utf-8-sig") as f:
        content = f.read()
    
    with open(cache_file, "w", encoding="utf-8") as f:
        f.write(content)
    
    logger.info(f"Formatted WPAD file saved at: '{cache_file}'")
    return str(cache_file)

def get_wpad_from_http(wpad_url: str, cache: Cache, use_cache: bool = True) -> str:
    """
    Download the WPAD file and write it into a file.

    Args:
        wpad_url (str): URL of the WPAD file.
        cache (Cache): Cache object.
        use_cache (bool, optional): Use cached files.
    
    Returns:
        str: Path to the downloaded WPAD file.
    """
    wpad_file = cache.dir / gen_pac_file_based_on_url(wpad_url)

    # Get file from cache if exists and didn't expire
    if wpad_file.exists() and use_cache:
        cache_age = time.time() - wpad_file.stat().st_mtime
        
        if cache_age < cache.expires:
            logger.info(f"Using cached WPAD file: '{wpad_file}'")
            return str(wpad_file)
        else:
            logger.info(f"Cache expired, removing: '{wpad_file}'")
            wpad_file.unlink() # Delete file since it expired

    # Download if cache file expires or doesn't exist
    logger.info(f"Downloading WPAD from: '{wpad_url}'")
    r = requests.get(wpad_url)
    r.raise_for_status()

    with open(wpad_file, "w", encoding="utf-8") as f:
        f.write(r.text)
    
    logger.info(f"Saved WPAD to cache: '{wpad_file}'")
    return str(wpad_file)

def purge_cache_dir(cache_dir) -> None:
    """
    Purge the cache directory.

    Args:
        cache_dir (Path, optional): Cache directory path. Defaults to CACHE_DIR.
    """
    files_removed = 0

    for file in cache_dir.iterdir():
        if file.is_file():
            try:
                file.unlink()
                logger.debug(f"Deleting file: '{file}'.")
                files_removed += 1
            except Exception as e:
                logger.warning(f"Could not delete file '{file}': {e}")

    logger.info(f"Cleared {files_removed} cached file(s) from '{cache_dir}'.")

def format_hostname(hostname: str) -> str:
    """
    Convert the hostname to URL format. E.g: example.com -> http://example.com/

    Args:
        hostname (str): Hostname.

    Returns:
        str: Formatted URL.
    """
    return f"http://{hostname}" 

def is_resolvable(host: str) -> bool:
    """
    Check if the IP of the given host can be resolved

    Args:
        host (str): Host FQDN.

    Returns:
        bool: Returns True if resolvable, False otherwise.
    """
    try:
        socket.gethostbyname(host)
        return True
    
    except socket.gaierror:
        return False

def is_url(url: str) -> bool:
    """
    Check if the passed string has URL format. 
    E.g: http://example.com returns True; example.com returns False

    Args:
        url (str): URL to test.

    Returns:
        bool: Returns True if the passed string has URL format, False otherwise.
    """
    return bool(re.match(r"^https?://", url))

def build_arg_parse() -> argparse.ArgumentParser:
    """
    Function to build the argparse object.
    
    Returns:
        argparse.ArgumentParser: Object responsible of managing the arguments.
    """
    parser = argparse.ArgumentParser(
        prog=__progname__,
        description=__progdesc__,
        epilog=__progepilog__,
        formatter_class=argparse.RawTextHelpFormatter
    )

    exclusive_group = parser.add_mutually_exclusive_group(required=False)

    exclusive_group.add_argument(
        "-u", "--wpad-url", 
        default=None,
        metavar="URL",
        type=str,
        help=f"Get the WPAD file from an HTTP server."
    )

    exclusive_group.add_argument(
        "-f", "--wpad-file",
        default=None,
        metavar="FILE",
        type=str,
        help="Path to the WPAD file."
    )

    parser.add_argument(
        "hostnames",
        nargs="+",
        metavar="hostname",
        type=str,
        help="URLs or hostnames to test."
    )

    parser.add_argument(
        "-d", "--check-dns",
        default=None,
        action="store_true",
        help="Check the DNS resolution of the FQDN."
    )

    parser.add_argument(
        "-n", "--no-cache",
        default=None,
        action="store_true",
        help="Not used cached files."
    )

    parser.add_argument(
        "-p", "--purge-cache",
        default=False,
        action="store_true",
        help="Clear cache directory."
    )

    parser.add_argument(
        "-c", "--cache-dir",
        type=str,
        help="Use a custom cache directory."
    )

    parser.add_argument(
        "-e", "--cache-expires",
        type=int,
        help="Cache expiration time in seconds.."
    )

    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Enable verbose logging output."
    )

    parser.add_argument(
        "-vvv", "--debug",
        action="store_true",
        help="Enable debug logging output."
    )

    parser.add_argument(
        "--version",
        action="version",
        version=f"%(prog)s {__version__}",
        help="Show program's version number and exit."
    )
    return parser

def setup_logging(debug: bool, verbose: bool) -> None:
    """
    Setup the logging configuration. Logs are printed to console and optionally to a log file.

    Args:
        debug (bool): If True, set logging level to DEBUG.
        verbose (bool): If True, set logging level to INFO.
    """
    if debug:
        level = logging.DEBUG
    elif verbose:
        level = logging.INFO
    else:
        level = logging.WARNING

    logging.basicConfig(
        level=level,
        format="%(levelname)s: %(message)s"
    )

def main():
    parser = build_arg_parse()
    args = parser.parse_args()
    setup_logging(debug=args.debug, verbose=args.verbose)
    
    # Read the config file
    config = Config.load()
    
    # Get options
    options = {
        "hostnames": args.hostnames,
        "check_dns": args.check_dns or config.get("check_dns", False),
        "purge_cache": args.purge_cache,
        "wpad_url": args.wpad_url or config.get("wpad_url", ""),
        "wpad_file": args.wpad_file or config.get("wpad_file", ""),
        "use_cache": not args.no_cache or not config.get("use_cache", False),
    }

    # Init cache
    cache = Cache.from_sources(args, config)

    # Raise error if no wpad_url or wpad_file were provided
    if not options.get("wpad_url") and not options.get("wpad_file"):
        logger.error(
            f"You must provide either an URL to get the WPAD or a path to a WPAD file. "
            f"Use config file {Config.CONFIG_FILE} or provide it with -f or -u params."
        )
        sys.exit(ERR_NO_DATA_PROVIDED)

    # Log the selected options for debug level
    for key, value in options.items():
        if value is not None and value != "":
            logger.debug(f"Selected '{key}: {value}'.")

    # Clear cache directory if specified
    purge_cache_dir(cache.dir) if options["purge_cache"] else None

    try: 
        wpad_file_formatted = (
            format_wpad_file(options["wpad_file"], cache, options["use_cache"]) if options["wpad_file"] != ""
            else get_wpad_from_http(options["wpad_url"], cache, options["use_cache"])
        )

        pacparser.init()
        pacparser.parse_pac_file(wpad_file_formatted)

        for hostname in options["hostnames"]:
            formatted_hostname = hostname if is_url(hostname) else format_hostname(hostname)
            proxy = pacparser.find_proxy(formatted_hostname)

            # Check DNS if flag specified
            if options["check_dns"] and not is_resolvable(hostname):
                logger.warning(f"Hostname '{hostname}' could not be resolved via DNS.")

            sys.stdout.write(f"RESULT: {hostname} -> {proxy}\n")
            sys.stdout.flush()
    
    except requests.RequestException as e:
        logger.error(f"Error downloading the WPAD file: '{e}'")
        sys.exit(ERR_UNABLE_TO_DOWNLOAD_PAC)

    except FileNotFoundError as e:
        logger.error(f"The WPAD file '{args.wpad_file}' was not found. Provide it with -f FILE or use -u URL to download.")
        sys.exit(ERR_NO_PAC_FILE)

    except Exception as e:
        logger.error(f"The WPAD file couldn't be parsed: {e}")
        sys.exit(ERR_COULD_NOT_PARSE_PAC_FILE)
    
    finally:
        pacparser.cleanup()

    sys.exit(SUCCESS)

if __name__ == "__main__":
    main()
