"""
================================================================================
                    JARVIS CRYPTO & FINANCIAL MARKET PLUGIN
================================================================================
Fetches real-time cryptocurrency valuation (Bitcoin, Ethereum, Solana)
and equity indicators.
================================================================================
"""

import json
import urllib.request
from typing import Dict, Any, Tuple

from jarvis.plugins.plugin_base import JarvisPlugin


class CryptoStocksPlugin(JarvisPlugin):
    """Provides market quotes for major cryptocurrencies."""

    @property
    def name(self) -> str:
        return "crypto_stocks"

    @property
    def description(self) -> str:
        return "Fetches live cryptocurrency prices."

    def can_handle(self, text: str) -> bool:
        t = text.lower()
        return any(k in t for k in ["crypto", "bitcoin", "btc", "ethereum", "eth", "solana"])

    def execute(self, text: str, payload: Dict[str, Any]) -> Tuple[bool, str]:
        url = "https://api.coingecko.com/api/v3/simple/price?ids=bitcoin,ethereum,solana&vs_currencies=usd,inr"
        try:
            req = urllib.request.Request(url, headers={'User-Agent': 'JARVIS/4.0'})
            with urllib.request.urlopen(req, timeout=4) as resp:
                data = json.loads(resp.read().decode('utf-8'))

            btc_usd = data.get("bitcoin", {}).get("usd", 0)
            btc_inr = data.get("bitcoin", {}).get("inr", 0)
            eth_usd = data.get("ethereum", {}).get("usd", 0)

            speech = (
                f"Sir, Bitcoin ka price abhi approximately ${btc_usd:,} USD hai "
                f"(lagbhag ₹{btc_inr:,} INR). Ethereum ${eth_usd:,} par trade kar raha hai."
            )
            return True, speech
        except Exception:
            return False, "Sir, market API se real-time crypto prices fetch nahi ho paye."
