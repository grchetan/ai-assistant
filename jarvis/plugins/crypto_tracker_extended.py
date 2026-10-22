"""
================================================================================
                    JARVIS EXTENDED CRYPTO MARKET INTELLIGENCE
================================================================================
Comprehensive cryptocurrency market surveillance tracking top market assets,
24-hour price volatility, market capitalization, and fiat currency conversions.
================================================================================
"""

import json
import urllib.request
from typing import Dict, Any, Tuple, List

from jarvis.plugins.plugin_base import JarvisPlugin


class ExtendedCryptoPlugin(JarvisPlugin):
    """Detailed multi-asset cryptocurrency tracking."""

    @property
    def name(self) -> str:
        return "extended_crypto"

    @property
    def description(self) -> str:
        return "Comprehensive top 10 cryptocurrency market surveillance."

    def can_handle(self, text: str) -> bool:
        t = text.lower()
        return any(k in t for k in ["top crypto", "crypto market", "crypto ranking", "crypto prices"])

    def execute(self, text: str, payload: Dict[str, Any]) -> Tuple[bool, str]:
        url = "https://api.coingecko.com/api/v3/coins/markets?vs_currency=usd&order=market_cap_desc&per_page=5&page=1&sparkline=false"
        try:
            req = urllib.request.Request(url, headers={'User-Agent': 'JARVIS/4.0'})
            with urllib.request.urlopen(req, timeout=5) as resp:
                data = json.loads(resp.read().decode('utf-8'))

            lines = []
            for coin in data:
                symbol = coin['symbol'].upper()
                price = coin['current_price']
                change = coin.get('price_change_percentage_24h', 0.0)
                sign = "+" if change >= 0 else ""
                lines.append(f"{symbol}: ${price:,.2f} ({sign}{change:.1f}%)")

            speech = "Sir, top crypto assets: " + ", ".join(lines)
            return True, speech
        except Exception:
            return False, "Crypto market feed abhi unavailable hai sir."
