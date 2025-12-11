"""Domain services and helpers."""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal, ROUND_HALF_UP

import requests
from flask import current_app


@dataclass(frozen=True)
class RateSnapshot:
    """Structure capturing Bitcoin price information."""

    usd_per_btc: Decimal

    @property
    def usd_to_btc(self) -> Decimal:
        if not self.usd_per_btc:
            return Decimal('0')
        return (Decimal('1') / self.usd_per_btc).quantize(
            Decimal('0.00000001'),
            rounding=ROUND_HALF_UP,
        )


def fetch_rate_snapshot() -> RateSnapshot:
    """Return the latest BTC price, defaulting to 0 on network failure."""
    url = current_app.config['BTC_RATE_URL']
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
        usd_value = Decimal(str(data['bpi']['USD']['rate_float']))
        return RateSnapshot(usd_per_btc=usd_value)
    except Exception as exc:  # pragma: no cover - defensive fallback
        current_app.logger.warning('BTC rate fetch failed: %s', exc)
        return RateSnapshot(usd_per_btc=Decimal('0'))
