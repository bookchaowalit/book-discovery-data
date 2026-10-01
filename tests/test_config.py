"""Environment parsing fails fast with a clear message instead of a bare traceback."""

from __future__ import annotations

import importlib
import os
import unittest
from unittest.mock import patch

from discovery_data import config


def reload_with(**env: str):
    with patch.dict(os.environ, env):
        return importlib.reload(config)


class ConfigTests(unittest.TestCase):
    def tearDown(self) -> None:
        importlib.reload(config)

    def test_defaults(self) -> None:
        with patch.dict(os.environ, {}, clear=False):
            for name in ("API_PORT", "STALE_AFTER_HOURS"):
                os.environ.pop(name, None)
            module = importlib.reload(config)
        self.assertEqual(module.API_PORT, 8110)
        self.assertEqual(module.STALE_AFTER_HOURS, 36.0)

    def test_valid_overrides(self) -> None:
        module = reload_with(API_PORT=" 9000 ", STALE_AFTER_HOURS="0.5")
        self.assertEqual(module.API_PORT, 9000)
        self.assertEqual(module.STALE_AFTER_HOURS, 0.5)

    def test_blank_values_fall_back_to_defaults(self) -> None:
        module = reload_with(API_PORT="", STALE_AFTER_HOURS="  ")
        self.assertEqual(module.API_PORT, 8110)
        self.assertEqual(module.STALE_AFTER_HOURS, 36.0)

    def test_invalid_values_raise_config_error_naming_the_variable(self) -> None:
        cases = [
            ({"API_PORT": "80a"}, "API_PORT"),
            ({"API_PORT": "70000"}, "API_PORT"),
            ({"API_PORT": "-1"}, "API_PORT"),
            ({"STALE_AFTER_HOURS": "soon"}, "STALE_AFTER_HOURS"),
            ({"STALE_AFTER_HOURS": "nan"}, "STALE_AFTER_HOURS"),
            ({"STALE_AFTER_HOURS": "inf"}, "STALE_AFTER_HOURS"),
            ({"STALE_AFTER_HOURS": "0"}, "STALE_AFTER_HOURS"),
            ({"STALE_AFTER_HOURS": "-3"}, "STALE_AFTER_HOURS"),
        ]
        for env, name in cases:
            with self.subTest(env=env):
                with self.assertRaises(ValueError) as caught:
                    reload_with(**env)
                self.assertEqual(type(caught.exception).__name__, "ConfigError")
                self.assertIn(name, str(caught.exception))


if __name__ == "__main__":
    unittest.main()
