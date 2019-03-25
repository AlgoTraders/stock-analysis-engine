"""
Holiday detection for US Markets

`Stack Overflow for this module <https://stackoverflow.com/questions/33094297/
create-trading-holiday-calendar-with-pandas>`__
"""

import datetime as dt
import pandas.tseries.holiday as pd_holiday


class USTradingCalendar(
        pd_holiday.AbstractHolidayCalendar):
    """USTradingCalendar"""
    rules = [
        pd_holiday.Holiday(
            'NewYearsDay',
            month=1,
            day=1,
            observance=pd_holiday.nearest_workday),
        pd_holiday.USMartinLutherKingJr,
        pd_holiday.USPresidentsDay,
        pd_holiday.GoodFriday,
        pd_holiday.USMemorialDay,
        pd_holiday.Holiday(
            'USIndependenceDay',
            month=7,
            day=4,
            observance=pd_holiday.nearest_workday),
        pd_holiday.USLaborDay,
        pd_holiday.USThanksgivingDay,
        pd_holiday.Holiday(
            'Christmas',
            month=12,
            day=25,
            observance=pd_holiday.nearest_workday)
    ]
# end of USTradingCalendar


def get_trading_close_holidays(
        year=None):
    """get_trading_close_holidays

    Get Trading Holidays for the year

    :param year: optional - year integer
    """
    use_year = year
    if not use_year:
        use_year = int(dt.datetime.utcnow().year)
    inst = USTradingCalendar()
    return inst.holidays(
        dt.datetime(use_year-1, 12, 31),
        dt.datetime(use_year, 12, 31))
# end of get_trading_close_holidays


def is_holiday(
        date=None,
        date_str=None,
        fmt='%Y-%m-%d'):
    """is_holiday

    Determine if the ``date`` is a holiday, if not then determine
    if today is a holiday. Returns ``True`` if it is a holiday and
    ``False`` if it is not a holiday in the US Markets.

    :param date: optional - datetime object object
        for calling ``get_trading_close_holidays(year=date.year)``
    :param date_str: optional - date string formatted with ``fmt``
    :param fmt: optional - datetime.strftime formatter
    """
    cal_df = None
    use_date = dt.datetime.utcnow()
    if date:
        use_date = date
    else:
        if date_str:
            use_date = dt.datetime.strptime(
                date_str,
                fmt)
    cal_df = get_trading_close_holidays(
        year=use_date.year)
    use_date_str = use_date.strftime(fmt)
    for d in cal_df.to_list():
        if d.strftime(fmt) == use_date_str:
            return True
    return False
# end of is_holiday
