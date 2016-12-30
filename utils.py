def default_if_none(value, default):
    if value is not None:
        return value
    return default


def s_to_hms(seconds):
    """ Get tuple (hours, minutes, seconds) from total seconds """
    h, r = divmod(seconds, 3600)
    m, s = divmod(r, 60)
    return h, m, s


def hms_to_s(h=0, m=0, s=0):
    """ Get total seconds from tuple (hours, minutes, seconds) """
    return h * 3600 + m * 60 + s
