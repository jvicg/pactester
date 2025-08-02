#!/usr/bin/env python3

import tempfile
import logging
from argparse import Namespace
from pathlib import Path
from dataclasses import dataclass

import toml
from platformdirs import user_config_dir

from pactester import __progname__


logger = logging.getLogger(__name__)

@dataclass
class Cache:
    dir: Path
    expires: int

    DEFAULT_CACHE_DIR = Path(tempfile.gettempdir()) / "pactester-cache"
    DEFAULT_CACHE_EXPIRES = 24 * 3600

    @classmethod
    def from_sources(cls, args: Namespace, config: dict) -> "Cache":
        """
        Factory method that builds a Cache instance from CLI args and config dict.
        Priority: CLI > config > default.

        Args:
            args (Namespace): CLI arguments.
            config (dict): Configuration file
        """
        cache_dir = args.cache_dir or config.get("cache_dir") or cls.DEFAULT_CACHE_DIR
        cache_expires = args.cache_expires or config.get("cache_expires") or cls.DEFAULT_CACHE_EXPIRES

        # Ensure dir is a Path
        if not isinstance(cache_dir, Path):
            cache_dir = Path(cache_dir)
        cache_dir.mkdir(parents=True, exist_ok=True)

        logger.info(f"Cache directory is: '{cache_dir}'")
        logger.info(f"Cache expiration time is: '{cache_expires}'")

        return cls(cache_dir, int(cache_expires))

class Config:
    _CONFIG_DIR = Path(user_config_dir(__progname__))
    _CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    CONFIG_FILE = _CONFIG_DIR / "config.toml"

    _VALID_OPTIONS: set[str] = {
        "wpad_url",
        "wpad_file",
        "check_dns",
        "use_cache",
        "cache_dir",
        "cache_expires"
    }

    _MUTUALLY_EXCLUSIVE: tuple[list] = (
        ["wpad_url", "wpad_file"],
    )

    @classmethod
    def load(cls) -> dict:
        """
        Load the configuration from a TOML file.

        Returns:
            dict: Dictionary with all the user config.
        """
        if not cls.CONFIG_FILE.exists():
            logger.info(f"Configuration file {cls.CONFIG_FILE} was not found.")
            return {}

        try:    
            data = toml.load(cls.CONFIG_FILE)
            invalid_options = cls._detect_invalid_options(data)
            logger.info(f"Loaded configuration file '{cls.CONFIG_FILE}'. This config may be overrided by CLI.")

            for opt in invalid_options:
                logger.warning(f"Invalid option found in config file: '{opt}'.")
            
            cls._detect_mutually_exclusive(data)

            return data
        
        except toml.decoder.TomlDecodeError as e:
            logger.warning(f"Config file couldn't be loaded. Check file syntax: {e}")
            return {}

    @classmethod
    def _detect_invalid_options(cls, data: dict) -> list[str]:
        """
        Function to detect invalid options in the config file.
        
        Args:
            data (dict): Dict with the configuration.

        Returns:
            list[str]: List of invalid options.
        """
        return [opt for opt in data if opt not in cls._VALID_OPTIONS]

    @classmethod
    def _detect_mutually_exclusive(cls, data: dict) -> None:
        """
        Detect if mutually exclusive params has been passed together.

        Args:
            data (dict): Dict with the configuration.
        """
        for exclusive_group in cls._MUTUALLY_EXCLUSIVE:
            present_keys = [key for key in data.keys() if key in exclusive_group]
            if len(present_keys) > 1:
                logger.warning(
                    f"Mutually exclusive options found together in config file: '{present_keys}'. "
                    f"This may cause unexpected behaviour. Please, choose only one of them."
                )
            