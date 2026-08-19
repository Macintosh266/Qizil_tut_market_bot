import shlex


def parse_quoted_args(text: str) -> list[str]:
    """
    '"Chorsu bozori" "Olma" 50 12000' -> ["Chorsu bozori", "Olma", "50", "12000"]
    Ko'p so'zli nomlar uchun qo'shtirnoq ichiga olinishi kerak.
    """
    try:
        return shlex.split(text)
    except ValueError:
        return text.split()
