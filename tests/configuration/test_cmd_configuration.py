import sys
import pytest

from gemstone.config.configurator import CommandLineConfigurator
from gemstone.config.configurable import Configurable


def test_configurator_command_line_no_configurable(monkeypatch):
    configurables = [
        Configurable("a"),
        Configurable("b"),
        Configurable("c")
    ]

    monkeypatch.setattr(sys, "argv", [sys.argv[0]])

    configurator = CommandLineConfigurator()
    for c in configurables:
        configurator.register_configurable(c)

    configurator.load()
    assert configurator.get("a") is None
    assert configurator.get("b") is None
    assert configurator.get("c") is None
    assert configurator.get("d") is None


def test_configurator_command_line_one_configurable(monkeypatch):
    configurables = [
        Configurable("a"),
        Configurable("b"),
        Configurable("c")
    ]

    monkeypatch.setattr(sys, "argv", [sys.argv[0], "--a=1"])

    configurator = CommandLineConfigurator()

    for c in configurables:
        configurator.register_configurable(c)
    configurator.load()

    assert configurator.get("a") == "1"
    assert configurator.get("b") is None
    assert configurator.get("c") is None
    assert configurator.get("d") is None


def test_configurator_command_line_two_configurables(monkeypatch):
    configurables = [
        Configurable("a"),
        Configurable("b"),
        Configurable("c")
    ]

    monkeypatch.setattr(sys, "argv", [sys.argv[0], "--a=1", "--b", "3"])

    configurator = CommandLineConfigurator()

    for c in configurables:
        configurator.register_configurable(c)
    configurator.load()

    assert configurator.get("a") == "1"
    assert configurator.get("b") == "3"
    assert configurator.get("c") is None
    assert configurator.get("d") is None


def test_configurator_command_line_three_configurables(monkeypatch):
    configurables = [
        Configurable("a"),
        Configurable("b"),
        Configurable("c")
    ]

    monkeypatch.setattr(sys, "argv", [sys.argv[0], "--a=1", "--b", "3", "--c=2"])

    configurator = CommandLineConfigurator()

    for c in configurables:
        configurator.register_configurable(c)
    configurator.load()

    assert configurator.get("a") == "1"
    assert configurator.get("b") == "3"
    assert configurator.get("c") == "2"
    assert configurator.get("d") is None


def test_configurator_command_line_three_configurables_one_extra_param(monkeypatch):
    configurables = [
        Configurable("a"),
        Configurable("b"),
        Configurable("c")
    ]

    monkeypatch.setattr(sys, "argv", [sys.argv[0], "--a=1", "--b", "3", "--c=2", "--d=4"])

    configurator = CommandLineConfigurator()

    for c in configurables:
        configurator.register_configurable(c)

    with pytest.raises(SystemExit):
        # unrecognized parameter: --d
        configurator.load()
