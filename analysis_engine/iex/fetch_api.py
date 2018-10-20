"""
Fetch API calls wrapping pyEX

Supported environment variables:

::

    # verbose logging in this module
    export DEBUG_FETCH=1

"""

import pyEX.stocks as pyex_stocks
import analysis_engine.iex.utils as fetch_utils
import analysis_engine.dataset_scrub_utils as scrub_utils
from spylunking.log.setup_logging import build_colorized_logger
from analysis_engine.iex.consts import DATAFEED_DAILY
from analysis_engine.iex.consts import DATAFEED_MINUTE
from analysis_engine.iex.consts import DATAFEED_QUOTE
from analysis_engine.iex.consts import DATAFEED_STATS
from analysis_engine.iex.consts import DATAFEED_PEERS
from analysis_engine.iex.consts import DATAFEED_NEWS
from analysis_engine.iex.consts import DATAFEED_FINANCIALS
from analysis_engine.iex.consts import DATAFEED_EARNINGS
from analysis_engine.iex.consts import DATAFEED_DIVIDENDS
from analysis_engine.iex.consts import DATAFEED_COMPANY

log = build_colorized_logger(
    name=__name__)


def fetch_daily(
        work_dict,
        scrub_mode='sort-by-date'):
    """fetch_daily

    Fetch the IEX daily data for a ticker and
    return it as a ``pandas.DataFrame``.

    :param work_dict: dictionary of args
    :param scrub_mode: type of scrubbing handler to run
    """
    datafeed_type = DATAFEED_DAILY
    ticker = work_dict.get(
        'ticker',
        None)
    label = work_dict.get(
        'label',
        None)
    use_date = work_dict.get(
        'use_date',
        None)

    log.info(
        '{} - daily - scrub_mode={} args={} '
        'ticker={}'.format(
            label,
            scrub_mode,
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

    scrubbed_df = scrub_utils.ingress_scrub_dataset(
        label=label,
        scrub_mode=scrub_mode,
        datafeed_type=datafeed_type,
        msg_format='df={} date_str={}',
        ds_id=ticker,
        date_str=use_date,
        df=res)

    return scrubbed_df
# end of fetch_daily


def fetch_minute(
        work_dict,
        scrub_mode='sort-by-date'):
    """fetch_minute

    Fetch the IEX minute intraday data for a ticker and
    return it as a ``pandas.DataFrame``.

    :param work_dict: dictionary of args
    :param scrub_mode: type of scrubbing handler to run
    """
    datafeed_type = DATAFEED_MINUTE
    ticker = work_dict.get(
        'ticker',
        None)
    label = work_dict.get(
        'label',
        None)
    use_date = work_dict.get(
        'use_date',
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

    scrubbed_df = scrub_utils.ingress_scrub_dataset(
        label=label,
        scrub_mode=scrub_mode,
        datafeed_type=datafeed_type,
        msg_format='df={} date_str={}',
        ds_id=ticker,
        date_str=use_date,
        df=res)

    return scrubbed_df
# end of fetch_minute


def fetch_quote(
        work_dict,
        scrub_mode='sort-by-date'):
    """fetch_quote

    Fetch the IEX quote data for a ticker and
    return as a ``pandas.DataFrame``.

    :param work_dict: dictionary of args
    :param scrub_mode: type of scrubbing handler to run
    """
    datafeed_type = DATAFEED_QUOTE
    ticker = work_dict.get(
        'ticker',
        None)
    label = work_dict.get(
        'label',
        None)
    use_date = work_dict.get(
        'use_date',
        None)

    log.info(
        '{} - quote - args={} ticker={}'.format(
            label,
            work_dict,
            ticker))

    res = pyex_stocks.quoteDF(
        symbol=ticker)

    scrubbed_df = scrub_utils.ingress_scrub_dataset(
        label=label,
        scrub_mode=scrub_mode,
        datafeed_type=datafeed_type,
        msg_format='df={} date_str={}',
        ds_id=ticker,
        date_str=use_date,
        df=res)

    return scrubbed_df
# end of fetch_quote


def fetch_stats(
        work_dict,
        scrub_mode='sort-by-date'):
    """fetch_stats

    Fetch the IEX statistics data for a ticker and
    return it as a ``pandas.DataFrame``.

    :param work_dict: dictionary of args
    :param scrub_mode: type of scrubbing handler to run
    """
    datafeed_type = DATAFEED_STATS
    ticker = work_dict.get(
        'ticker',
        None)
    label = work_dict.get(
        'label',
        None)
    use_date = work_dict.get(
        'use_date',
        None)

    log.info(
        '{} - stats - args={} ticker={}'.format(
            label,
            work_dict,
            ticker))

    res = pyex_stocks.stockStatsDF(
        symbol=ticker)

    scrubbed_df = scrub_utils.ingress_scrub_dataset(
        label=label,
        scrub_mode=scrub_mode,
        datafeed_type=datafeed_type,
        msg_format='df={} date_str={}',
        ds_id=ticker,
        date_str=use_date,
        df=res)

    return scrubbed_df
# end of fetch_stats


def fetch_peers(
        work_dict,
        scrub_mode='sort-by-date'):
    """fetch_peers

    Fetch the IEX peers data for a ticker and
    return it as a ``pandas.DataFrame``.

    :param work_dict: dictionary of args
    :param scrub_mode: type of scrubbing handler to run
    """
    datafeed_type = DATAFEED_PEERS
    ticker = work_dict.get(
        'ticker',
        None)
    label = work_dict.get(
        'label',
        None)
    use_date = work_dict.get(
        'use_date',
        None)

    log.info(
        '{} - peers - args={} ticker={}'.format(
            label,
            work_dict,
            ticker))

    res = pyex_stocks.peersDF(
        symbol=ticker)

    scrubbed_df = scrub_utils.ingress_scrub_dataset(
        label=label,
        scrub_mode=scrub_mode,
        datafeed_type=datafeed_type,
        msg_format='df={} date_str={}',
        ds_id=ticker,
        date_str=use_date,
        df=res)

    return scrubbed_df
# end of fetch_peers


def fetch_news(
        work_dict,
        scrub_mode='sort-by-date'):
    """fetch_news

    Fetch the IEX news data for a ticker and
    return it as a ``pandas.DataFrame``.

    :param work_dict: dictionary of args
    :param scrub_mode: type of scrubbing handler to run
    """
    datafeed_type = DATAFEED_NEWS
    ticker = work_dict.get(
        'ticker',
        None)
    label = work_dict.get(
        'label',
        None)
    use_date = work_dict.get(
        'use_date',
        None)

    log.info(
        '{} - news - args={} ticker={}'.format(
            label,
            work_dict,
            ticker))

    res = pyex_stocks.newsDF(
        symbol=ticker,
        count=50)

    scrubbed_df = scrub_utils.ingress_scrub_dataset(
        label=label,
        scrub_mode=scrub_mode,
        datafeed_type=datafeed_type,
        msg_format='df={} date_str={}',
        ds_id=ticker,
        date_str=use_date,
        df=res)

    return scrubbed_df
# end of fetch_news


def fetch_financials(
        work_dict,
        scrub_mode='sort-by-date'):
    """fetch_financials

    Fetch the IEX financial data for a ticker and
    return it as a ``pandas.DataFrame``.

    :param work_dict: dictionary of args
    :param scrub_mode: type of scrubbing handler to run
    """
    datafeed_type = DATAFEED_FINANCIALS
    ticker = work_dict.get(
        'ticker',
        None)
    label = work_dict.get(
        'label',
        None)
    use_date = work_dict.get(
        'use_date',
        None)

    log.info(
        '{} - financials - args={} ticker={}'.format(
            label,
            work_dict,
            ticker))

    res = pyex_stocks.financialsDF(
        symbol=ticker)

    scrubbed_df = scrub_utils.ingress_scrub_dataset(
        label=label,
        scrub_mode=scrub_mode,
        datafeed_type=datafeed_type,
        msg_format='df={} date_str={}',
        ds_id=ticker,
        date_str=use_date,
        df=res)

    return scrubbed_df
# end of fetch_financials


def fetch_earnings(
        work_dict,
        scrub_mode='sort-by-date'):
    """fetch_earnings

    Fetch the IEX earnings data for a ticker and
    return it as a ``pandas.DataFrame``.

    :param work_dict: dictionary of args
    :param scrub_mode: type of scrubbing handler to run
    """
    datafeed_type = DATAFEED_EARNINGS
    ticker = work_dict.get(
        'ticker',
        None)
    label = work_dict.get(
        'label',
        None)
    use_date = work_dict.get(
        'use_date',
        None)

    log.info(
        '{} - earnings - args={} ticker={}'.format(
            label,
            work_dict,
            ticker))

    res = pyex_stocks.earningsDF(
        symbol=ticker)

    scrubbed_df = scrub_utils.ingress_scrub_dataset(
        label=label,
        scrub_mode=scrub_mode,
        datafeed_type=datafeed_type,
        msg_format='df={} date_str={}',
        ds_id=ticker,
        date_str=use_date,
        df=res)

    return scrubbed_df
# end of fetch_earnings


def fetch_dividends(
        work_dict,
        scrub_mode='sort-by-date'):
    """fetch_dividends

    Fetch the IEX dividends data for a ticker and
    return it as a ``pandas.DataFrame``.

    :param work_dict: dictionary of args
    :param scrub_mode: type of scrubbing handler to run
    """
    datafeed_type = DATAFEED_DIVIDENDS
    ticker = work_dict.get(
        'ticker',
        None)
    label = work_dict.get(
        'label',
        None)
    timeframe = work_dict.get(
        'timeframe',
        '2y')
    use_date = work_dict.get(
        'use_date',
        None)

    log.info(
        '{} - dividends - args={} ticker={} '
        'timeframe={}'.format(
            label,
            work_dict,
            ticker,
            timeframe))

    res = pyex_stocks.dividendsDF(
        symbol=ticker,
        timeframe=timeframe)

    scrubbed_df = scrub_utils.ingress_scrub_dataset(
        label=label,
        scrub_mode=scrub_mode,
        datafeed_type=datafeed_type,
        msg_format='df={} date_str={}',
        ds_id=ticker,
        date_str=use_date,
        df=res)

    return scrubbed_df
# end of fetch_dividends


def fetch_company(
        work_dict,
        scrub_mode='NO_SORT'):
    """fetch_company

    Fetch the IEX company data for a ticker and
    return it as a ``pandas.DataFrame``.

    :param work_dict: dictionary of args
    :param scrub_mode: type of scrubbing handler to run
    """
    datafeed_type = DATAFEED_COMPANY
    ticker = work_dict.get(
        'ticker',
        None)
    label = work_dict.get(
        'label',
        None)
    use_date = work_dict.get(
        'use_date',
        None)

    log.info(
        '{} - company - args={} ticker={}'.format(
            label,
            label,
            work_dict,
            ticker))

    res = pyex_stocks.companyDF(
        symbol=ticker)

    scrubbed_df = scrub_utils.ingress_scrub_dataset(
        label=label,
        scrub_mode=scrub_mode,
        datafeed_type=datafeed_type,
        msg_format='df={} date_str={}',
        ds_id=ticker,
        date_str=use_date,
        df=res)

    return scrubbed_df
# end of fetch_company
