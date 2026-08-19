from datetime import datetime, timedelta


def parse_period(text: str) -> tuple[datetime, datetime, str] | None:
    """
    /statistic argumentini tahlil qiladi:
      "11.08.2026"  -> bir kun
      "08.2026"     -> bir oy
      "2026"        -> bir yil
    Qaytaradi: (start, end, label) yoki noto'g'ri format bo'lsa None.
    """
    text = text.strip()
    parts = text.split(".")

    try:
        if len(parts) == 3:
            day, month, year = map(int, parts)
            start = datetime(year, month, day)
            end = start + timedelta(days=1)
            return start, end, text

        if len(parts) == 2:
            month, year = map(int, parts)
            start = datetime(year, month, 1)
            end = datetime(year + 1, 1, 1) if month == 12 else datetime(year, month + 1, 1)
            return start, end, text

        if len(parts) == 1:
            year = int(parts[0])
            start = datetime(year, 1, 1)
            end = datetime(year + 1, 1, 1)
            return start, end, text

    except ValueError:
        return None

    return None


def get_preset_period(preset: str) -> tuple[datetime, datetime]:
    """
    "today" | "week" | "month" | "year" uchun (start, end) oralig'ini qaytaradi.
    "week" — joriy dushanbadan boshlab, "month"/"year" — joriy oy/yil boshidan.
    """
    now = datetime.utcnow()
    today_start = datetime(now.year, now.month, now.day)

    if preset == "today":
        return today_start, today_start + timedelta(days=1)

    if preset == "week":
        week_start = today_start - timedelta(days=today_start.weekday())
        return week_start, today_start + timedelta(days=1)

    if preset == "month":
        month_start = datetime(now.year, now.month, 1)
        return month_start, today_start + timedelta(days=1)

    if preset == "year":
        year_start = datetime(now.year, 1, 1)
        return year_start, today_start + timedelta(days=1)

    # noma'lum preset — bugungi kunni qaytaramiz
    return today_start, today_start + timedelta(days=1)
