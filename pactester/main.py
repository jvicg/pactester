#!/usr/bin/env python3

import argparse
import logging
import os
import re
import socket
import sys
import time
from hashlib import sha1

import pacparser
import requests

from pactester import __progdesc__, __progepilog__, __progname__, __version__
from pactester.config import CacheDirCreationFailed, Config, Options

SUCCESS = 0
ERR_NO_PAC_FILE = 1
ERR_NO_DATA_PROVIDED = 2
ERR_UNABLE_TO_DOWNLOAD_PAC = 3
ERR_COULD_NOT_PARSE_PAC_FILE = 4
ERR_COULD_NOT_CREATE_CACHE_DIR = 5

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

def gen_pac_file_based_on_url(pac_url: str) -> str:
    """
    Generate a PAC file based on the URL hash. This will store an unique name for each PAC url.

    Args:
        pac_url (str): PAC file URL.

    Returns:
        Path: Object with the file.
    """
    return gen_sha_hash(pac_url)

def gen_pac_file_based_on_timestamp(pac_file: str) -> str:
    """
    Generate a cache filename for the formatted PAC file based on the original file path and last modification time.

    Args:
        pac_file (str): Path to the PAC.

    Returns:
        Path: Object with the file.
    """
    stat = os.stat(pac_file)
    unique_str = f"{pac_file}:{stat.st_mtime}"
    return gen_sha_hash(unique_str)

def format_pac_file(opts: Options) -> str:
    """
    Properly format PAC file as utf-8-sig.

    Args:
        opts (Options): Object with all the program options.

    Returns:
        str: Path of the file.
    """
    cache_file = opts.cache_dir / gen_pac_file_based_on_timestamp(opts.pac_file) # type: ignore

    if cache_file.exists() and opts.use_cache:
        logger.info(f"Using cached formatted PAC file: '{cache_file}'")
        return str(cache_file)

    with open(opts.pac_file, encoding="utf-8-sig") as f: # type: ignore
        content = f.read()

    with open(cache_file, "w", encoding="utf-8") as f:
        f.write(content)

    logger.info(f"Formatted PAC file saved at: '{cache_file}'")
    return str(cache_file)

def get_pac_from_http(opts: Options) -> str:
    """
    Download the PAC file and write it into a file.

    Args:
        opts (Options): Object with all the program options.

    Returns:
        str: Path to the downloaded PAC file.
    """
    pac_file = opts.cache_dir / gen_pac_file_based_on_url(opts.pac_url) # type: ignore

    # Get file from cache if exists and didn't expire
    if pac_file.exists() and opts.use_cache:
        cache_age = time.time() - pac_file.stat().st_mtime

        if cache_age < opts.cache_expires:
            logger.info(f"Using cached PAC file: '{pac_file}'")
            return str(pac_file)
        else:
            logger.info(f"Cache expired, removing: '{pac_file}'")
            pac_file.unlink() # Delete file since it expired

    # Download if cache file expires or doesn't exist
    logger.info(f"Downloading PAC from: '{opts.pac_url}'")
    r = requests.get(opts.pac_url) # type: ignore
    r.raise_for_status()

    with open(pac_file, "w", encoding="utf-8") as f:
        f.write(r.text)

    logger.info(f"Saved PAC to cache: '{pac_file}'")
    return str(pac_file)

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

    parser.add_argument(
        "hostnames",
        nargs="+",
        metavar="hostname",
        type=str,
        help="URLs or hostnames to test."
    )

    exclusive_group = parser.add_mutually_exclusive_group(required=False)

    exclusive_group.add_argument(
        "-u", "--pac-url",
        default=None,
        metavar="URL",
        type=str,
        help="Get the PAC file from an HTTP server."
    )

    exclusive_group.add_argument(
        "-f", "--pac-file",
        default=None,
        metavar="FILE",
        type=str,
        help="Path to the PAC file."
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
        help="Cache expiration time in seconds."
    )

    parser.add_argument(
        "-v", "--verbose",
        default=False,
        action="store_true",
        help="Enable verbose logging output."
    )

    parser.add_argument(
        "-vvv", "--debug",
        default=False,
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

    # Load config file and setup logging
    setup_logging(debug=args.debug, verbose=args.verbose)
    config = Config.load()

    try:
        opts = Options(args, config)

        # Raise error if no pac_url or pac_file were provided
        if opts.pac_url is None and opts.pac_file is None:
            logger.error(
                f"You must provide either an URL to get the PAC or a path to a PAC file. "
                f"Use config file '{Config.CONFIG_FILE}' or provide it with -f or -u params."
            )
            sys.exit(ERR_NO_DATA_PROVIDED)

        # Log the selected options for debug level
        for key, value in opts:
            if value is not None:
                logger.debug(f"Selected '{key}: {value}'.")

        # Clear cache directory if specified
        purge_cache_dir(opts.cache_dir) if opts.purge_cache else None

        pac_file_formatted = (
            format_pac_file(opts) if opts.pac_file is not None
            else get_pac_from_http(opts)
        )

        pacparser.init()
        pacparser.parse_pac_file(pac_file_formatted)

        for hostname in opts.hostnames:
            formatted_hostname = hostname if is_url(hostname) else format_hostname(hostname)
            proxy = pacparser.find_proxy(formatted_hostname)

            # Check DNS if flag specified
            if opts.check_dns and not is_resolvable(hostname):
                logger.warning(f"Hostname '{hostname}' could not be resolved via DNS.")

            sys.stdout.write(f"RESULT: {hostname} -> {proxy}\n")
            sys.stdout.flush()

    except CacheDirCreationFailed as e:
        logger.error(f"Error creating cache dir: {e}")
        sys.exit(ERR_COULD_NOT_CREATE_CACHE_DIR)

    except requests.RequestException as e:
        logger.error(f"Error downloading the PAC file: '{e}'")
        sys.exit(ERR_UNABLE_TO_DOWNLOAD_PAC)

    except FileNotFoundError:
        logger.error(
            f"The PAC file '{args.pac_file}' was not found."
            f"Provide it with -f FILE or use -u URL to download."
        )
        sys.exit(ERR_NO_PAC_FILE)

    except Exception as e:
        logger.error(f"The PAC file couldn't be parsed: {e}")
        sys.exit(ERR_COULD_NOT_PARSE_PAC_FILE)

    finally:
        pacparser.cleanup()

    sys.exit(SUCCESS)

if __name__ == "__main__":
    main()
