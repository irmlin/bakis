from datetime import datetime, timedelta
import pytz


def get_adjusted_timezone(datetime_obj: datetime, tz_str: str = 'Europe/Vilnius') -> datetime:
    datetime_naive = datetime_obj.replace(tzinfo=None)
    target_timezone = pytz.timezone(tz_str)
    utc_offset = target_timezone.utcoffset(datetime_naive).total_seconds()
    return datetime_naive + timedelta(seconds=utc_offset)
