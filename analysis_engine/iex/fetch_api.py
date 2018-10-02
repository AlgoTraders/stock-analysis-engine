"""
Fetch API calls wrapping pyEX
"""

import pyEX.stocks as pyex_stocks
import analysis_engine.iex.utils as fetch_utils
from spylunking.log.setup_logging import build_colorized_logger


log = build_colorized_logger(
    name=__name__)


def fetch_daily(
        work_dict):
    """fetch_daily

    Fetch the IEX daily data for a ticker and
    return it as a pandas Dataframe

    :param work_dict: dictionary of args
    """
    ticker = work_dict.get(
        'ticker',
        None)
    label = work_dict.get(
        'label',
        None)

    log.info(
        '{} - daily - args={} ticker={}'.format(
            label,
            work_dict,
            ticker))

    res = pyex_stocks.chartDF(
        symbol=ticker,
        timeframe=work_dict.get(
            'timeframe',
            '1d'),
        date=work_dict.get(
            'date',
            None))
    return res
# end of fetch_daily


def fetch_minute(
        work_dict):
    """fetch_minute

    Fetch the IEX minute intraday data for a ticker and
    return it as a pandas Dataframe

    :param work_dict: dictionary of args
    """
    ticker = work_dict.get(
        'ticker',
        None)
    label = work_dict.get(
        'label',
        None)

    from_historical_date = None
    last_close_to_use = None
    dates = []

    if 'from_historical_date' in work_dict:
        from_historical_date = work_dict['from_historical_date']
        last_close_to_use = work_dict['last_close_to_use']
        dates = fetch_utils.get_days_between_dates(
            from_historical_date=work_dict['from_historical_date'],
            last_close_to_use=last_close_to_use)

    log.info(
        '{} - minute - args={} ticker={} '
        'fhdate={} last_close={} dates={}'.format(
            label,
            work_dict,
            ticker,
            from_historical_date,
            last_close_to_use,
            dates))

    res = pyex_stocks.chartDF(
        symbol=ticker,
        timeframe=work_dict.get(
            'timeframe',
            '1m'),
        date=work_dict.get(
            'date',
            None))
    return res
# end of fetch_minute


def fetch_stats(
        work_dict):
    """fetch_stats

    Fetch the IEX statistics data for a ticker and
    return it as a pandas Dataframe

    :param work_dict: dictionary of args
    """
    ticker = work_dict.get(
        'ticker',
        None)
    label = work_dict.get(
        'label',
        None)

    log.info(
        '{} - stats - args={} ticker={}'.format(
            label,
            work_dict,
            ticker))

    res = pyex_stocks.stockStatsDF(
        symbol=ticker)
    return res
# end of fetch_stats


def fetch_peers(
        work_dict):
    """fetch_peers

    Fetch the IEX peers data for a ticker and
    return it as a pandas Dataframe

    :param work_dict: dictionary of args
    """
    ticker = work_dict.get(
        'ticker',
        None)
    label = work_dict.get(
        'label',
        None)

    log.info(
        '{} - peers - args={} ticker={}'.format(
            label,
            work_dict,
            ticker))

    res = pyex_stocks.peersDF(
        symbol=ticker)
    return res
# end of fetch_peers


def fetch_news(
        work_dict):
    """fetch_news

    Fetch the IEX news data for a ticker and
    return it as a pandas Dataframe

    :param work_dict: dictionary of args
    """
    ticker = work_dict.get(
        'ticker',
        None)
    label = work_dict.get(
        'label',
        None)

    log.info(
        '{} - news - args={} ticker={}'.format(
            label,
            work_dict,
            ticker))

    res = pyex_stocks.newsDF(
        symbol=ticker)
    return res
# end of fetch_news


def fetch_financials(
        work_dict):
    """fetch_financials

    Fetch the IEX financial data for a ticker and
    return it as a pandas Dataframe

    :param work_dict: dictionary of args
    """
    ticker = work_dict.get(
        'ticker',
        None)
    label = work_dict.get(
        'label',
        None)

    log.info(
        '{} - financials - args={} ticker={}'.format(
            label,
            work_dict,
            ticker))

    res = pyex_stocks.financialsDF(
        symbol=ticker)
    return res
# end of fetch_financials


def fetch_earnings(
        work_dict):
    """fetch_earnings

    Fetch the IEX earnings data for a ticker and
    return it as a pandas Dataframe

    :param work_dict: dictionary of args
    """
    ticker = work_dict.get(
        'ticker',
        None)
    label = work_dict.get(
        'label',
        None)

    log.info(
        '{} - earnings - args={} ticker={}'.format(
            label,
            work_dict,
            ticker))

    res = pyex_stocks.earningsDF(
        symbol=ticker)
    return res
# end of fetch_earnings


def fetch_dividends(
        work_dict):
    """fetch_dividends

    Fetch the IEX dividends data for a ticker and
    return it as a pandas Dataframe

    :param work_dict: dictionary of args
    """
    ticker = work_dict.get(
        'ticker',
        None)
    label = work_dict.get(
        'label',
        None)

    log.info(
        '{} - dividends - args={} ticker={}'.format(
            label,
            work_dict,
            ticker))

    res = pyex_stocks.dividendsDF(
        symbol=ticker)
    return res
# end of fetch_dividends


def fetch_company(
        work_dict):
    """fetch_company

    Fetch the IEX company data for a ticker and
    return it as a pandas Dataframe

    :param work_dict: dictionary of args
    """
    ticker = work_dict.get(
        'ticker',
        None)
    label = work_dict.get(
        'label',
        None)

    log.info(
        '{} - company - args={} ticker={}'.format(
            label,
            label,
            work_dict,
            ticker))

    res = pyex_stocks.companyDF(
        symbol=ticker)
    return res
# end of fetch_company
