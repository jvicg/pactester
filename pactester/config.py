#!/usr/bin/env python3

import logging
import tempfile
from argparse import Namespace
from dataclasses import dataclass, fields
from pathlib import Path

import toml
from platformdirs import user_config_dir

from pactester import __progname__

logger = logging.getLogger(__name__)

class CacheDirCreationFailed(Exception):
    """Raised when cache directory creation fails."""
    def __init__(self, path: Path, msg: str):
        super().__init__(f"'{path}': {msg}")
        self.path = path
        self.msg = msg

@dataclass
class Config:
    """
    Class responsible to read from the config file and contain all the readen options as params.
    If there're invalid params detected or the configuration file can't be read, it will show a warning, but
    the program won't stop since options can be also obtained from CLI.
    """
    CONFIG_DIR = Path(user_config_dir(__progname__))
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    CONFIG_FILE = CONFIG_DIR / "config.toml"

    _DEFAULT_CACHE_DIR = Path(tempfile.gettempdir()) / f".{__progname__}_cache"
    _DEFAULT_CACHE_EXPIRES = 24 * 3600

    # Options that should not be used together
    _MUTUALLY_EXCLUSIVE = (
        ("pac_url", "pac_file"),
    )

    pac_url: str | None = None
    pac_file: str | None = None
    check_dns: bool = False
    use_cache: bool = True
    cache_dir: str | Path = _DEFAULT_CACHE_DIR
    cache_expires: int = _DEFAULT_CACHE_EXPIRES

    @classmethod
    def load(cls) -> "Config":
        """
        Load the configuration from a TOML file.

        Returns:
            Config: Configuration found on config file or default values if option not in file.
        """
        if not cls.CONFIG_FILE.exists():
            logger.warning(f"Configuration file '{cls.CONFIG_FILE}' was not found.")
            return cls()

        try:
            data = toml.load(cls.CONFIG_FILE)
            invalid_options = cls._detect_invalid_options(data)
            logger.info(f"Loaded configuration file '{cls.CONFIG_FILE}'. This config may be overrided by CLI.")

            for opt in invalid_options:
                logger.warning(f"Invalid option found in config file: '{opt}'.")

            cls._detect_mutually_exclusive(data)

            # Return instance. If the option is not found in the config file, default values will be used
            init_kwargs = {
                f.name: data.get(f.name, getattr(cls, f.name))
                for f in fields(cls)
            }

            return cls(**init_kwargs)

        except toml.decoder.TomlDecodeError as e:
            logger.warning(f"Config file couldn't be loaded. Check file syntax: {e}")
            return cls()

    @classmethod
    def get_default_cache_dir(cls) -> Path:
        """Return default cache dir."""
        return cls._DEFAULT_CACHE_DIR

    @classmethod
    def _detect_invalid_options(cls, data: dict) -> list[str]:
        """
        Function to detect invalid options in the config file.

        Args:
            data (dict): Dict with the configuration.

        Returns:
            list[str]: List of invalid options.
        """
        valid_options = {f.name for f in fields(cls)}
        return [opt for opt in data if opt not in valid_options]

    @classmethod
    def _detect_mutually_exclusive(cls, data: dict) -> None:
        """
        Detect if mutually exclusive params has been passed together.

        Args:
            data (dict): Dict with the configuration.
        """
        for exclusive_group in cls._MUTUALLY_EXCLUSIVE:
            present_keys = [key for key in data if key in exclusive_group]
            if len(present_keys) > 1:
                logger.warning(
                    f"Mutually exclusive options found together in config file: '{present_keys}'. "
                    f"This may cause unexpected behaviour. Please, choose only one of them."
                )

@dataclass
class Options:
    """
    This objects contains all the options that will be used by the program.
    The init method build the object from CLI args and config file.
    Priority: CLI > config file > default.
    """
    def __init__(self, args: Namespace, config: Config):
        self.hostnames: list = args.hostnames
        self.pac_url: str | None = args.pac_url or config.pac_url
        self.pac_file:str | None = args.pac_file or config.pac_file
        self.check_dns: bool = args.check_dns or config.check_dns
        self.purge_cache: bool = args.purge_cache
        self.use_cache: bool = not args.no_cache if args.no_cache is not None else config.use_cache
        self.cache_dir: str | Path = args.cache_dir or config.cache_dir
        self.cache_expires: int = args.cache_expires or config.cache_expires

        # Create cache dir
        self._create_cache_dir()

    def __iter__(self):
        for key in self.__dict__:
            yield key, getattr(self, key)

    def _create_cache_dir(self) -> None:
        """
        Ensure the cache directory exists. Try fallback if needed.
        Raise exception if all attempts fail.
        """
        def try_mkdir(path: Path) -> bool:
            try:
                path.mkdir(parents=True, exist_ok=True)
                return True
            except Exception as e:
                logger.warning(f"Could not create directory '{path}': {e}")
                return False

        if not isinstance(self.cache_dir, Path):
            self.cache_dir = Path(self.cache_dir)

        # First try user-specified or config-defined cache dir
        if try_mkdir(self.cache_dir):
            return

        # Fallback to default
        fallback_dir = Config.get_default_cache_dir()
        if try_mkdir(fallback_dir):
            self.cache_dir = fallback_dir
            return

        # Raise exception if all attemps failed
        raise CacheDirCreationFailed(fallback_dir, "All attempts to create cache directory failed.")
