"""Sunset time for a date, so the app's plans get the sunset-based "Best" lines without a network call (D105, D107).

NOAA's solar position equations (the "General Solar Position Calculations" sheet), with the usual 90.833° zenith
for sunset (refraction plus the sun's radius). Checked against sunrise-sunset.org for central London, Saturdays in
Oct-Nov 2026, to the minute (tests/test_sun.py; research/sources.csv, 28 Sep).
"""

from __future__ import annotations

import math
from datetime import date, datetime, timedelta, timezone
from zoneinfo import ZoneInfo

LONDON = (51.5074, -0.1278)


def sunset(day: date, lat: float = LONDON[0], lon: float = LONDON[1], tz: str = "Europe/London") -> str | None:
    """Local sunset as "hh:mm", or None where the sun doesn't set that day."""
    doy = day.timetuple().tm_yday
    days_in_year = 366 if (day.year % 4 == 0 and (day.year % 100 != 0 or day.year % 400 == 0)) else 365
    g = 2 * math.pi / days_in_year * (doy - 1 + (18 - 12) / 24)   # fractional year, at 18:00 UTC
    eqtime = 229.18 * (0.000075 + 0.001868 * math.cos(g) - 0.032077 * math.sin(g)
                       - 0.014615 * math.cos(2 * g) - 0.040849 * math.sin(2 * g))
    decl = (0.006918 - 0.399912 * math.cos(g) + 0.070257 * math.sin(g) - 0.006758 * math.cos(2 * g)
            + 0.000907 * math.sin(2 * g) - 0.002697 * math.cos(3 * g) + 0.00148 * math.sin(3 * g))
    phi = math.radians(lat)
    cos_ha = math.cos(math.radians(90.833)) / (math.cos(phi) * math.cos(decl)) - math.tan(phi) * math.tan(decl)
    if not -1 <= cos_ha <= 1:
        return None
    ha = math.degrees(math.acos(cos_ha))
    utc_min = 720 - 4 * (lon - ha) - eqtime        # sunset uses the negative hour angle
    utc = datetime(day.year, day.month, day.day, tzinfo=timezone.utc) + timedelta(minutes=utc_min)
    local = (utc + timedelta(seconds=30)).astimezone(ZoneInfo(tz))   # round to the nearest minute
    return local.strftime("%H:%M")
