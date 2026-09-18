"""Booths domain constants."""

from datetime import date, time

FESTIVAL_DATES = [date(2026, 9, 29), date(2026, 9, 30), date(2026, 10, 1)]
DEFAULT_FESTIVAL_DATE = FESTIVAL_DATES[0]

# 이 시각 이전 요청은 DAY, 이후는 NIGHT 기본값
DAY_NIGHT_BOUNDARY = time(16, 30)

# 컬러칩 4종. 'BOOTH' 칩은 협업 부스(COLLAB)와 일반 부스(ETC)를 함께 묶음
CATEGORY_CHIPS = ["BOOTH", "TOILET", "ALCOHOL", "ECO"]
BOOTH_CHIP = "BOOTH"
BOOTH_CHIP_CATEGORIES = ["COLLAB", "ETC"]
