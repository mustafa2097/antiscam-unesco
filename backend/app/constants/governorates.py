IRAQI_GOVERNORATES: tuple[tuple[str, str, str], ...] = (
    ("baghdad", "Baghdad", "بغداد"),
    ("basra", "Basra", "البصرة"),
    ("nineveh", "Nineveh", "نينوى"),
    ("erbil", "Erbil", "أربيل"),
    ("sulaymaniyah", "Sulaymaniyah", "السليمانية"),
    ("dohuk", "Dohuk", "دهوك"),
    ("kirkuk", "Kirkuk", "كركوك"),
    ("anbar", "Anbar", "الأنبار"),
    ("diyala", "Diyala", "ديالى"),
    ("saladin", "Saladin", "صلاح الدين"),
    ("babil", "Babil", "بابل"),
    ("karbala", "Karbala", "كربلاء"),
    ("najaf", "Najaf", "النجف"),
    ("wasit", "Wasit", "واسط"),
    ("maysan", "Maysan", "ميسان"),
    ("dhi_qar", "Dhi Qar", "ذي قار"),
    ("muthanna", "Muthanna", "المثنى"),
    ("qadisiyyah", "Qadisiyyah", "القادسية"),
)

GOVERNORATE_SLUGS = frozenset(slug for slug, _, _ in IRAQI_GOVERNORATES)
