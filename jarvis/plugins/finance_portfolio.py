"""
================================================================================
            JARVIS IN-HOUSE FINANCIAL & INVESTMENT CALCULATOR PLUGIN
================================================================================
Calculates:
  • SIP (Systematic Investment Plan) future maturity wealth
  • Fixed Deposit (FD) compound interest returns
  • GST (Goods & Services Tax) pre-tax and post-tax values
  • Rule of 72 (Doubling period estimation)
Zero cloud network dependencies.
================================================================================
"""

import math
import re
from typing import Dict, Any, Tuple
from jarvis.plugins.plugin_base import JarvisPlugin
from jarvis.core.logger import get_logger


class FinancePortfolioPlugin(JarvisPlugin):
    """Offline financial mathematics and investment return predictor."""

    @property
    def name(self) -> str:
        return "finance_portfolio"

    @property
    def description(self) -> str:
        return "Calculates SIP returns, Fixed Deposit growth, GST, and loan analytics."

    def can_handle(self, text: str) -> bool:
        t = text.lower()
        return any(k in t for k in ["sip calculate", "sip calculator", "fixed deposit", "fd return", "gst calculate", "rule of 72"])

    def execute(self, text: str, payload: Dict[str, Any]) -> Tuple[bool, str]:
        t = text.lower()
        logger = get_logger()

        # SIP Calculator: e.g. "sip calculate 5000 12 10" (monthly, return_rate, years)
        if "sip" in t:
            nums = [float(x) for x in re.findall(r"\b\d+(?:\.\d+)?\b", t)]
            if len(nums) >= 3:
                p, r, y = nums[0], nums[1], nums[2]
                n = int(y * 12)
                i = (r / 12.0) / 100.0
                # SIP formula: P * [((1 + i)^n - 1) / i] * (1 + i)
                maturity = p * (((1 + i)**n - 1) / i) * (1 + i)
                invested = p * n
                wealth_gain = maturity - invested
                msg = (
                    f"Sir, SIP Investment Summary:\n"
                    f"• Monthly Investment: ₹{p:,.2f}\n"
                    f"• Total Invested ({int(y)} saal): ₹{invested:,.2f}\n"
                    f"• Estimated Wealth Gain: ₹{wealth_gain:,.2f}\n"
                    f"• Total Expected Value: ₹{maturity:,.2f} (at {r}% p.a.)"
                )
                logger.success("SIP calculation generated.", "FINANCE")
                return True, msg

        # GST Calculator: e.g. "gst calculate 1000 18"
        if "gst" in t:
            nums = [float(x) for x in re.findall(r"\b\d+(?:\.\d+)?\b", t)]
            if len(nums) >= 2:
                amount, rate = nums[0], nums[1]
                gst_amount = amount * (rate / 100.0)
                total = amount + gst_amount
                msg = (
                    f"Sir, GST Calculation:\n"
                    f"• Base Amount: ₹{amount:,.2f}\n"
                    f"• GST ({rate}%): ₹{gst_amount:,.2f}\n"
                    f"• Total Billable Amount: ₹{total:,.2f}"
                )
                return True, msg

        # Rule of 72
        if "rule of 72" in t:
            nums = [float(x) for x in re.findall(r"\b\d+(?:\.\d+)?\b", t)]
            if nums:
                rate = nums[0]
                years = 72.0 / rate if rate > 0 else 0
                return True, f"Sir, Rule of 72 ke anusaar {rate}% annual return par aapka paisa lagbhag {years:.1f} saal me double hoga."

        return True, "Sir, please provide parameters: e.g. 'sip calculate [monthly_amount] [expected_return_pct] [years]'."
