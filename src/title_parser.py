"""

"""
import re

__author__ = "LoveIsGrief"

RANGE_REGEX_START = r'(?P<start>((?P<s_hours>\d{2}):)?((?P<s_minutes>\d{2}):)(?P<s_seconds>\d{2}))'
RANGE_REGEX_END = r'(?P<end>((?P<e_hours>\d{2}):)?((?P<e_minutes>\d{2}):)(?P<e_seconds>\d{2}))'

RANGE_REGEX_OPT_START = r'\[%(start)s?-%(end)s\]' % dict(start=RANGE_REGEX_START, end=RANGE_REGEX_END)
RANGE_REGEX_OPT_END = r'\[%(start)s-%(end)s?\]' % dict(start=RANGE_REGEX_START, end=RANGE_REGEX_END)


def str2int(string):
    i = 0
    try:
        i = int(string)
    except:
        pass
    return i


def seconds_from_match(match, prefix):
    hours = str2int(match.group(prefix + "hours")) * 3600
    minutes = str2int(match.group(prefix + "minutes")) * 60
    seconds = str2int(match.group(prefix + "seconds"))
    return hours + minutes + seconds


def get_range_from_string(string):
    """

    WARNING:
    Be sure that `start >= end` otherwise start will be set to None!

    :param string:
    :type string: str
    :return: start and end of the range in seconds, None for any value means infinity
    :rtype: tuple[int|None, int|None]
    """
    start = None
    end = None
    m = re.search(RANGE_REGEX_OPT_START, string)
    if not m:
        m = re.search(RANGE_REGEX_OPT_END, string)
    if m:
        if m.group("start"):
            start = seconds_from_match(m, "s_")
        if m.group("end"):
            end = seconds_from_match(m, "e_")

    if (start and end) and start >= end:
        start = None

    return start, end
