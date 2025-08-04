#!/usr/bin/env python

"""
Suite of tests functions for Options class
"""

from argparse import Namespace

import pytest

from pactester.config import CacheDirCreationFailed, Config, Options

# ----------------------
# Fixtures
# ----------------------

@pytest.fixture
def args(tmp_path):
    return Namespace(
        hostnames=["fake-host.com", "http://fake-url.int"],
        pac_url="http://fake-url/wpad.dat",
        pac_file=None,
        check_dns=True,
        purge_cache=False,
        no_cache=False,
        cache_dir=str(tmp_path / "fake_cache_dir"),
        cache_expires=12345
    )

@pytest.fixture
def args_with_missing():
    return Namespace(
        hostnames=["fake-host.com", "http://fake-url.int"],
        pac_url=None,
        pac_file=None,
        check_dns=None,
        purge_cache=False,
        cache_dir=None,
        no_cache=None,
        cache_expires=None
    )

@pytest.fixture
def mocked_config_obj(monkeypatch, tmp_path):
    """
    Return a mocked Config object with modified paths
    """
    fake_dir = tmp_path / "config"
    fake_dir.mkdir(exist_ok=True)

    fake_file = fake_dir / "config.toml"

    monkeypatch.setattr(Config, "CONFIG_DIR", fake_dir)
    monkeypatch.setattr(Config, "CONFIG_FILE", fake_file)

    return Config

@pytest.fixture
def config(mocked_config_obj, tmp_path):
    return mocked_config_obj(
        pac_url="http://fake-url-config-file/wpad.dat",
        check_dns=False,
        use_cache=False,
        cache_dir=tmp_path / "fake_cache_dir_2",
        cache_expires=67890
    )

# ----------------------
# Tests
# ----------------------

def test_options_initialization_from_cli_only(args, tmp_path, mocked_config_obj):
    """
    Test that options is initialized with the CLI values. No config file will be passed.
    """
    config = mocked_config_obj()
    opts = Options(args, config)

    assert opts.pac_url == "http://fake-url/wpad.dat"
    assert opts.pac_file is None
    assert opts.check_dns is True
    assert opts.use_cache is True
    assert opts.purge_cache is False
    assert opts.cache_dir == tmp_path / "fake_cache_dir"
    assert opts.cache_expires == 12345
    assert opts.hostnames == ["fake-host.com", "http://fake-url.int"]

def test_options_use_config_when_missing_from_cli(args_with_missing, config, tmp_path):
    """
    Make sure that config options are loaded when they're not passed via CLI.
    """
    opts = Options(args_with_missing, config)

    assert opts.pac_url == "http://fake-url-config-file/wpad.dat"
    assert opts.pac_file is None
    assert opts.check_dns is False
    assert opts.use_cache is False
    assert opts.cache_dir == tmp_path / "fake_cache_dir_2"
    assert opts.cache_expires == 67890

def test_options_cache_dir_is_created(args, config):
    """
    Ensure that the cache directory is created.
    """
    opts = Options(args, config)

    assert opts.cache_dir.exists() # type: ignore

def test_options_cache_dir_creation_failure(args, monkeypatch):
    """
    Check exception is raised when is not posible to create cache directory.
    """
    config = Config()

    # Mock Path.mkdir to always return an error
    def fail_mkdir(*args, **kwargs):
        raise OSError("Permission denied")

    monkeypatch.setattr("pathlib.Path.mkdir", fail_mkdir)

    with pytest.raises(CacheDirCreationFailed) as exc_info:
        Options(args, config)

    assert "All attempts to create cache directory failed" in str(exc_info.value)
    assert str(Config._DEFAULT_CACHE_DIR) in str(exc_info.value)

def test_options_cli_override_config(args, config, tmp_path):
    """
    Test that the CLI options override whats in the config file.
    """
    opts = Options(args, config)

    assert opts.pac_url == "http://fake-url/wpad.dat"
    assert opts.pac_file is None
    assert opts.check_dns is True
    assert opts.use_cache is True
    assert opts.cache_dir == tmp_path / "fake_cache_dir"
    assert opts.cache_expires == 12345

def test_options_iterates_correctly(args, config):
    """
    Test that `__iter__` function works as expected.
    """
    opts = Options(args, config)
    keys = dict(opts).keys()

    assert "hostnames" in keys
    assert "pac_url" in keys
    assert "pac_file" in keys
    assert "check_dns" in keys
    assert "purge_cache" in keys
    assert "use_cache" in keys
    assert "cache_dir" in keys
    assert "cache_expires" in keys
