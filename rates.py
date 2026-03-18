"""
Курсы USDT/RUB с Rapira (rapira.net).
Покупка: курс Rapira + 0.5%, продажа: курс Rapira - 0.5%.
"""

import logging
import time
from typing import Optional

import httpx

logger = logging.getLogger(__name__)

RAPIRA_RATES_URL = "https://api.rapira.net/open/market/rates"
CACHE_SECONDS = 60  # лимит API: 100 запросов/мин

_cached: Optional[tuple[float, float, float]] = None  # (buy, sell, timestamp)


def fetch_usdt_rub_rates() -> Optional[tuple[float, float]]:
    """
    Возвращает (курс покупки USDT, курс продажи USDT) в рублях.
    Покупка = Rapira + 0.5%, продажа = Rapira - 0.5%.
    При ошибке возвращает None.
    """
    global _cached
    now = time.time()
    if _cached is not None and (now - _cached[2]) < CACHE_SECONDS:
        return _cached[0], _cached[1]

    try:
        with httpx.Client(timeout=10.0) as client:
            r = client.get(
                RAPIRA_RATES_URL,
                headers={"Accept": "application/json"},
            )
            r.raise_for_status()
            data = r.json()
    except Exception as e:
        logger.warning("Rapira rates fetch failed: %s", e)
        if _cached is not None:
            return _cached[0], _cached[1]
        return None

    items = data.get("data") or []
    for item in items:
        if item.get("symbol") == "USDT/RUB":
            close = float(item.get("close") or 0)
            if close <= 0:
                return None
            buy = round(close * 1.005, 2)
            sell = round(close * 0.995, 2)
            _cached = (buy, sell, now)
            return buy, sell

    logger.warning("USDT/RUB not found in Rapira response")
    return None
