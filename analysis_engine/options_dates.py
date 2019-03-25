"""
Option Date Utilities
=====================

These are a collection of functions for determining
when the current options cycle expires (3rd Friday of most months)
and for calculating historical option expiration dates.

.. tip:: If you need to automate looking up the current option
    cycle expiration, then please checkout using the script:

    ::

        /opt/sa/analysis_engine/scripts/print_next_expiration_date.py
        2018-10-19

"""

import datetime
import pandas.tseries.offsets as pd_bday
import analysis_engine.holidays as hdays
import spylunking.log.setup_logging as log_utils

log = log_utils.build_colorized_logger(name=__name__)


def get_options_for_years(
        years=[
            '2014',
            '2015',
            '2016',
            '2016',
            '2017',
            '2018',
            '2019',
            '2020',
            '2021',
            '2022',
        ]):
    """get_options_for_years

    :param years: number of years back
    :param months: number of months to build year
    """

    entities = []
    months = [
        '01',
        '02',
        '03',
        '04',
        '05',
        '06',
        '07',
        '08',
        '09',
        '10',
        '11',
        '12'
    ]
    option_expirations = {
    }
    opts = []

    for year in years:
        for month in months:
            target_date_str = str(month + '-01-' + year)
            target_date = datetime.datetime.strptime(
                target_date_str,
                '%m-%d-%Y')
            option_expiration_date = option_expiration(
                target_date)
            option_expiration_str = option_expiration_date.strftime(
                '%m-%d-%Y')
            option_expirations[option_expiration_str] = option_expiration_date
            opts.append(option_expiration_date.strftime(
                '%m-%d-%Y'))
        # end of for all months
    # end of building option expiration dates

    now = datetime.datetime.now() + datetime.timedelta(days=0)
    num_legs = 20
    num_done = 1
    last_exp_date = 0
    date_format = '%m-%d-%Y'
    str_output = now.strftime(date_format)
    log.info(f'current date={str_output}')

    entities.append(str_output)

    for option_exp in opts:
        option_exp_date = datetime.datetime.strptime(
            option_exp,
            date_format)
        if option_exp_date >= now:
            if num_legs > 0:
                if (last_exp_date == 0):
                    delta = (option_exp_date - now).days
                else:
                    delta = (option_exp_date - last_exp_date).days

                entities.append(str(delta))
                entities.append(option_exp_date.strftime('%m-%d-%Y'))
                entities.append('Leg ' + str(num_done))

            else:
                break
            num_legs -= 1
            num_done += 1
            last_exp_date = option_exp_date
    # end of processing

    return entities
# end of get_options_for_years


def historical_options(
        years=[
            '2014',
            '2015',
            '2016',
            '2017',
            '2018',
            '2019',
            '2020',
            '2021',
            '2022',
            '2023',
            '2024',
            '2025',
            '2026',
            '2027',
            '2028'
        ]):
    """historical_options

    :param years: years to build
    """

    entities = []
    months = [
        '01',
        '02',
        '03',
        '04',
        '05',
        '06',
        '07',
        '08',
        '09',
        '10',
        '11',
        '12'
    ]
    option_expirations = {
    }
    opts = []

    for year in years:
        for month in months:
            target_date_str = str(month + '-01-' + year)
            target_date = datetime.datetime.strptime(
                target_date_str,
                '%m-%d-%Y')
            option_expiration_date = option_expiration(
                target_date)
            option_expiration_str = option_expiration_date.strftime(
                '%m-%d-%Y')
            option_expirations[option_expiration_str] = option_expiration_date
            opts.append(option_expiration_date.strftime(
                '%m-%d-%Y'))
        # end of for all months

    # end of building option expiration dates

    now = datetime.datetime.strptime('01-01-2009', '%m-%d-%Y')
    num_legs = 400
    num_done = 1
    date_format = '%m-%d-%Y'

    for option_exp in opts:
        option_exp_date = datetime.datetime.strptime(option_exp, date_format)
        if option_exp_date >= now:
            if num_legs > 0:
                entities.append(option_exp_date.strftime('%m-%d-%Y'))
            else:
                break
            num_legs -= 1
            num_done += 1
    # end of processing

    return entities
# end of historical_options


def get_options_between_dates(
        start_date,
        end_date):
    """get_options_between_dates

    :param start_date: start date
    :param end_date: end date
    """
    valid_options = []

    for rec in historical_options():
        opt_date = datetime.datetime.strptime(
            str(rec),
            '%m-%d-%Y').date()
        if start_date <= opt_date <= end_date:
            valid_options.append(opt_date.strftime('%Y-%m-%d'))

    return valid_options
# end of get_options_between_dates


def option_expiration(
        date=None):
    """option_expiration

    :param date: date to find the current expiration
    """
    cur_date = date
    if not cur_date:
        cur_date = datetime.datetime.now()
    while (not (cur_date.weekday() == 4 and 14 < cur_date.day < 22)):
        cur_date = cur_date + datetime.timedelta(days=1)

    if hdays.is_holiday(
            date=cur_date):
        test_date = cur_date - datetime.timedelta(days=1)
        if cur_date.weekday() == 0:
            test_date = cur_date - datetime.timedelta(days=3)
        if hdays.is_holiday(
                date=test_date):
            test_date = cur_date - datetime.timedelta(days=4)
            if hdays.is_holiday(
                    date=test_date):
                test_date = cur_date - datetime.timedelta(days=5)
        cur_date = test_date
    # end of if this date is a holiday and go back

    return cur_date
# end of option_expiration


def get_options_for_today():
    """get_options_for_today

    Get a list of option expiration nodes where the last cell
    has the current option cycle's expiration date.

    """
    cur_date = datetime.datetime.now()
    cycle_exps = historical_options()
    previous_exp = None
    valid_option_exps = []
    for idx, org_exp_date_str in enumerate(cycle_exps):
        log.debug(f'cycle={idx} expiration={org_exp_date_str}')
        exp_date = datetime.datetime.strptime(
            org_exp_date_str,
            '%m-%d-%Y')
        exp_date_str = exp_date.strftime(
            '%Y-%m-%d')

        cycle_start_date = exp_date - pd_bday.BDay(19)
        if previous_exp:
            cycle_start_date = previous_exp + pd_bday.BDay(1)
        cycle_start_date_str = cycle_start_date.strftime(
            '%m-%d-%Y')
        valid_option_exps.append({
            'exp_date': exp_date,
            'exp_date_str': exp_date_str,
            'cycle_start': cycle_start_date,
            'cycle_start_str': cycle_start_date_str
        })
        if cur_date < exp_date:
            break
        previous_exp = exp_date
    # end of for all historical options

    return valid_option_exps
# end of get_options_for_today
