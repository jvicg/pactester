#!/usr/bin/env python

"""
Suite of tests functions for Config class
"""

import pytest
import toml

from pactester.config import Config

# ----------------------
# Fixtures
# ----------------------

@pytest.fixture
def config_dir(tmp_path):
    return tmp_path

@pytest.fixture
def config_file(tmp_path):
    return tmp_path / "fake_config.toml"

@pytest.fixture
def config_valid_data():
    return {
        "pac_url": "http://fake-url/wpad.dat",
        "check_dns": False,
        "use_cache": True,
        "cache_dir": "/tmp/fake_cache_dir",
        "cache_expires": 86400
    }

@pytest.fixture
def config_invalid_data():
    return {
        "pac_url": "http://fake-url/wpad.dat",
        "check_dns": False,
        "invalid_opt1": "invalid_value1",
        "invalid_opt2": "invalid_value2"
    }

@pytest.fixture
def config_mutually_exclusive_data():
    return {
        "pac_url": "http://fake-url/wpad.dat",
        "pac_file": "fake_wpad.dat",
    }

@pytest.fixture
def patch_config_paths(monkeypatch, config_file, config_dir):
    """
    Patch Config object to replace paths with fake ones.
    """
    monkeypatch.setattr(Config, "CONFIG_DIR", config_dir)
    monkeypatch.setattr(Config, "CONFIG_FILE", config_file)

# ----------------------
# Tests
# ----------------------

def test_config_load_with_valid_config(patch_config_paths, config_file, config_valid_data):
    """
    Ensure that the Config object is properly instanciated when valid config is passed.
    """
    config_file.write_text(toml.dumps(config_valid_data))

    config = Config.load()

    assert config.pac_url == "http://fake-url/wpad.dat"
    assert config.pac_file is None
    assert not config.check_dns
    assert config.cache_dir == "/tmp/fake_cache_dir"
    assert config.cache_expires == 86400

@pytest.mark.parametrize("data", [
    {"pac_url": "http://example.com/wpad.dat"},
    {"pac_file": "/path/to/local.wpad"}
])
def test_config_load_no_warning_on_valid_config(patch_config_paths, config_file, data, caplog):
    """
    Ensure no warnings are logged when a valid config is loaded.
    """
    config_file.write_text(toml.dumps(data))

    with caplog.at_level("WARNING"):
        Config.load()

    assert "Invalid option found in config file" not in caplog.text
    assert "Mutually exclusive options found together" not in caplog.text

def test_config_load_default_values_when_no_config_file(patch_config_paths, config_file, caplog):
    """
    Make sure that Config object has the default values when the config file don't exist
    Also check that it prints the expected warning.
    """
    with caplog.at_level("WARNING"):
        config = Config.load()

    assert f"Configuration file '{config_file}' was not found." in caplog.text

    assert not config.check_dns
    assert config.pac_url is None
    assert config.pac_file is None
    assert config.cache_dir == Config._DEFAULT_CACHE_DIR
    assert config.cache_expires == Config._DEFAULT_CACHE_EXPIRES

def test_config_load_log_warning_invalid_options(patch_config_paths, config_file, config_invalid_data, caplog):
    """
    Ensure that the warnings are logged when passed invalid options to Config.
    """
    config_file.write_text(toml.dumps(config_invalid_data))

    with caplog.at_level("WARNING"):
        Config.load()

    assert "invalid_opt1" in caplog.text
    assert "invalid_opt2" in caplog.text

def test_config_load_mutually_exclusive(patch_config_paths, config_file, config_mutually_exclusive_data, caplog):
    """
    Check that warning of mutually exclusive is logged.
    """
    config_file.write_text(toml.dumps(config_mutually_exclusive_data))

    with caplog.at_level("WARNING"):
        Config.load()

    assert "pac_url" in caplog.text
    assert "pac_file" in caplog.text

def test_config_load_invalid_toml_syntax(patch_config_paths, config_file, caplog):
    """
    Ensure that a malformed TOML config logs a warning and falls back to defaults.
    """
    config_file.write_text("invalid = ???")  # Sintaxis TOML no válida

    with caplog.at_level("WARNING"):
        Config.load()

    assert "Config file couldn't be loaded" in caplog.text

def test_detect_invalid_options(config_invalid_data):
    """
    Test `detect_invalid_options` only returns invalid options.
    """
    invalid_options = Config._detect_invalid_options(config_invalid_data)

    assert "invalid_opt1" in invalid_options
    assert "invalid_opt2" in invalid_options

    assert "pac_url" not in invalid_options
    assert "check_dns" not in invalid_options

def test_get_default_cache_dir_returns_expected_path():
    """
    Ensure `get_default_cache_dir` returns the expected default path.
    """
    assert Config.get_default_cache_dir() == Config._DEFAULT_CACHE_DIR
