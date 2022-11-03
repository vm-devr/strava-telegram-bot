from datetime import datetime, timedelta


def last_sunday(today: datetime.date) -> datetime.date:
    return _last_day(today, "sunday")


def _last_day(d: datetime.date, day_name: str) -> datetime.date:
    # See https://stackoverflow.com/a/19835125
    days_of_week = ["sunday", "monday", "tuesday", "wednesday", "thursday", "friday", "saturday"]
    target_day = days_of_week.index(day_name.lower())
    delta_day = target_day - d.isoweekday()
    if delta_day >= 0:
        delta_day -= 7  # go back 7 days
    return d + timedelta(days=delta_day)
