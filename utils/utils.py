import re
import pytz
from utils.async_utils import Bus
from transliterate import translit
from datetime import datetime, timedelta


# setting time zone tbilisi
tbilisi_tz = pytz.timezone("Asia/Tbilisi")

def emoji(arrival_time: int) -> str:
    """
    Returns an emoji indicating bus arrival urgency.

    :param arrival_time: time until bus arrival (in minutes)
    :return: colored circle emoji
    """

    return "🔴" if arrival_time < 4 else "🟡" if arrival_time < 7 else "🟢"


def parse_tbilisi_schedule(schedule: list[dict]) -> str:
    """
    Returns a formated bus schedule.

    :param schedule: list of bus schedule dicts
    :return: formated bus schedule
    """

    formated_schedule = ""
    now = datetime.now(tbilisi_tz)
    for bus in schedule:
        # time
        will_arrive_in = bus["realtimeArrivalMinutes"]
        arrival_time = (now + timedelta(minutes=will_arrive_in)).strftime("%H:%M")

        # emoji
        sign = emoji(will_arrive_in)

        # number
        number = bus["shortName"]

        # route
        # translation from Georgian to English
        route = translit(bus["headsign"], "ka", reversed=True).title()

        # changing the case of roman numerals
        pattern = r"\b[IVXLCDM][ivxlcdm]+\b"
        route = re.sub(pattern, lambda x: x.group().upper(), route)

        formated_schedule += f"<code>{arrival_time}</code> {sign} <code>{number}</code> через <b>{will_arrive_in}</b> мин. {route}\n"
    return formated_schedule


def parse_batumi_schedule(schedule: list[Bus]) -> str:
    """
    Returns a formated bus schedule.

    :param schedule: list of namedtuples of bus schedule
    :return: formated bus schedule
    """

    # sorted by increasing arriving time
    sorted_schedule = sorted(schedule, key=lambda x: x.will_arrive_in)

    formated_schedule = ""
    now = datetime.now(tbilisi_tz)
    for bus in sorted_schedule:
        # time
        will_arrive_in = int(bus.will_arrive_in)
        arrival_time = (now + timedelta(minutes=will_arrive_in)).strftime("%H:%M")

        # emoji
        sign = emoji(will_arrive_in)

        start_point, end_point = bus.route[0], bus.route[1]
        # route
        # translation from Georgian to English
        start_point, end_point = translit(start_point, "ka", reversed=True).title(), translit(end_point, "ka", reversed=True).title()

        # changing the case of roman numerals
        pattern = r"\b[IVXLCDM][ivxlcdm]+\b"
        start_point, end_point = re.sub(pattern, lambda x: x.group().upper(), start_point), re.sub(pattern, lambda x: x.group().upper(), end_point)

        formated_schedule += f"<code>{arrival_time}</code> {sign} <code>{bus.number}</code> через <b>{will_arrive_in}</b> мин. {start_point} - {end_point}\n"
    return formated_schedule