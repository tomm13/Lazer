import time


def convert_to_unix_time(datetime):
    # Convert to unix time
    return int(time.mktime(datetime.timetuple()))


def convert_to_format(unix_time):
    return f"<t:{unix_time}:R>"
