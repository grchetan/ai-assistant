"""
================================================================================
                    JARVIS PLUGIN REGISTRY & MANAGER
================================================================================
Dynamic loader and lifecycle manager for all JARVIS capability plugins.
================================================================================
"""

import threading
from typing import Dict, List, Optional, Tuple, Any

from jarvis.plugins.plugin_base import JarvisPlugin
from jarvis.plugins.weather_plugin import WeatherPlugin
from jarvis.plugins.crypto_stocks_plugin import CryptoStocksPlugin
from jarvis.plugins.news_plugin import NewsPlugin
from jarvis.plugins.calculator_units import CalculatorUnitsPlugin
from jarvis.plugins.trivia_games import TriviaGamesPlugin
from jarvis.plugins.dictionary_thesaurus import DictionaryPlugin
from jarvis.plugins.system_benchmark import SystemBenchmarkPlugin
from jarvis.core.logger import get_logger


class PluginManager:
    """Manages plugin lifecycles and routes intent executions."""

    _instance: Optional["PluginManager"] = None
    _lock = threading.RLock()

    def __new__(cls) -> "PluginManager":
        with cls._lock:
            if cls._instance is None:
                cls._instance = super(PluginManager, cls).__new__(cls)
                cls._instance._init_manager()
            return cls._instance

    def _init_manager(self) -> None:
        self.logger = get_logger()
        self._plugins: Dict[str, JarvisPlugin] = {}
        self._register_default_plugins()

    def _register_default_plugins(self) -> None:
        defaults = [
            WeatherPlugin(),
            CryptoStocksPlugin(),
            NewsPlugin(),
            CalculatorUnitsPlugin(),
            TriviaGamesPlugin(),
            DictionaryPlugin(),
            SystemBenchmarkPlugin(),
        ]
        for p in defaults:
            self.register_plugin(p)

    def register_plugin(self, plugin: JarvisPlugin) -> bool:
        """Register and activate a plugin."""
        with self._lock:
            try:
                if plugin.on_load():
                    self._plugins[plugin.name] = plugin
                    self.logger.info(f"Loaded plugin: [{plugin.name}] - {plugin.description}", "PLUGIN")
                    return True
            except Exception as e:
                self.logger.error(f"Failed to load plugin {plugin.name}: {e}", "PLUGIN")
            return False

    def find_handler(self, text: str) -> Optional[JarvisPlugin]:
        """Find the first plugin willing to handle the text query."""
        with self._lock:
            for plugin in self._plugins.values():
                try:
                    if plugin.can_handle(text):
                        return plugin
                except Exception:
                    continue
        return None

    def execute_plugin(self, plugin_name: str, text: str, payload: Dict[str, Any]) -> Tuple[bool, str]:
        with self._lock:
            plugin = self._plugins.get(plugin_name)
            if not plugin:
                return False, f"Plugin '{plugin_name}' not found."
            try:
                return plugin.execute(text, payload)
            except Exception as e:
                return False, f"Plugin error: {e}"


def get_plugin_manager() -> PluginManager:
    return PluginManager()
