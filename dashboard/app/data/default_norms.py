"""Starting norm table, loaded into the `benchmark_norms` table by migration 0002.

IMPORTANT: these are INDICATIVE reference values for an MVP, not an official dataset.
Each row is   (age_min, age_max, p10, p25, p50, p75, p90)  - the score needed to reach that percentile.
Replace them with official SAI / Khelo India (or your own) tables by editing the
`benchmark_norms` table; no code changes are needed.
"""

SOURCE = "Indicative MVP reference norms (replace with official SAI/Khelo India tables)"

# Vertical jump, centimetres.
VERTICAL_JUMP = {
    "male": [
        (5, 9, 14, 18, 23, 28, 33),
        (10, 12, 20, 25, 30, 36, 42),
        (13, 15, 26, 32, 38, 45, 52),
        (16, 18, 32, 38, 45, 52, 60),
        (19, 25, 33, 40, 47, 55, 63),
        (26, 100, 26, 32, 39, 46, 53),
    ],
    "female": [
        (5, 9, 12, 16, 20, 25, 29),
        (10, 12, 18, 22, 27, 32, 37),
        (13, 15, 21, 26, 31, 37, 43),
        (16, 18, 22, 27, 32, 38, 44),
        (19, 25, 22, 27, 33, 39, 45),
        (26, 100, 18, 23, 28, 34, 39),
    ],
}

# Sit-ups completed in 60 seconds (the duration used by the mobile app).
SIT_UP = {
    "male": [
        (5, 9, 8, 12, 17, 22, 27),
        (10, 12, 15, 20, 25, 30, 35),
        (13, 15, 20, 26, 31, 36, 41),
        (16, 18, 24, 30, 35, 40, 45),
        (19, 25, 25, 31, 36, 41, 46),
        (26, 100, 20, 26, 31, 36, 41),
    ],
    "female": [
        (5, 9, 6, 10, 14, 19, 23),
        (10, 12, 12, 17, 22, 27, 31),
        (13, 15, 16, 21, 26, 31, 36),
        (16, 18, 18, 24, 29, 34, 39),
        (19, 25, 19, 25, 30, 35, 40),
        (26, 100, 15, 21, 26, 31, 36),
    ],
}

TESTS = {"vertical_jump": ("cm", VERTICAL_JUMP), "sit_up": ("reps", SIT_UP)}


def default_rows() -> list[tuple]:
    """Flat list of (test_type, gender, unit, age_min, age_max, p10, p25, p50, p75, p90)."""
    rows = []
    for test_type, (unit, by_gender) in TESTS.items():
        for gender, bands in by_gender.items():
            for band in bands:
                rows.append((test_type, gender, unit, *band))
    return rows
