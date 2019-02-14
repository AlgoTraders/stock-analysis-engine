"""
Extract an IEX dataset from Redis (S3 support coming soon) and
load it into a ``pandas.DataFrame``

Supported environment variables:

::

    # verbose logging in this module
    export DEBUG_EXTRACT=1

    # verbose logging for just Redis operations in this module
    export DEBUG_REDIS_EXTRACT=1

    # verbose logging for just S3 operations in this module
    export DEBUG_S3_EXTRACT=1

    # to show debug, trace logging please export ``SHARED_LOG_CFG``
    # to a debug logger json file. To turn on debugging for this
    # library, you can export this variable to the repo's
    # included file with the command:
    export SHARED_LOG_CFG=/opt/sa/analysis_engine/log/debug-logging.json

"""

import copy
import analysis_engine.consts as ae_consts
import analysis_engine.iex.consts as iex_consts
import analysis_engine.extract_utils as extract_utils
import spylunking.log.setup_logging as log_utils

log = log_utils.build_colorized_logger(name=__name__)
keys = {
    'company': iex_consts.DATAFEED_COMPANY,
    'daily': iex_consts.DATAFEED_DAILY,
    'dividends': iex_consts.DATAFEED_DIVIDENDS,
    'earnings': iex_consts.DATAFEED_EARNINGS,
    'financials': iex_consts.DATAFEED_FINANCIALS,
    'minute': iex_consts.DATAFEED_MINUTE,
    'news1': iex_consts.DATAFEED_NEWS,
    'peers': iex_consts.DATAFEED_PEERS,
    'quote': iex_consts.DATAFEED_QUOTE,
    'stats': iex_consts.DATAFEED_STATS
}


def extract_daily_dataset(
        work_dict,
        scrub_mode='sort-by-date'):
    """extract_daily_dataset

    Fetch the IEX daily data for a ticker and
    return it as a pandas Dataframe

    :param work_dict: dictionary of args
    :param scrub_mode: type of scrubbing handler to run
    """
    return extract_dataset('daily', work_dict, scrub_mode=scrub_mode)
# end of extract_daily_dataset


def extract_minute_dataset(
        work_dict,
        scrub_mode='sort-by-date'):
    """extract_minute_dataset

    Fetch the IEX minute intraday data for a ticker and
    return it as a pandas Dataframe

    :param work_dict: dictionary of args
    :param scrub_mode: type of scrubbing handler to run
    """
    return extract_dataset('minute', work_dict, scrub_mode=scrub_mode)
# end of extract_minute_dataset


def extract_quote_dataset(
        work_dict,
        scrub_mode='sort-by-date'):
    """extract_quote_dataset

    Fetch the IEX quote data for a ticker and
    return it as a pandas Dataframe

    :param work_dict: dictionary of args
    :param scrub_mode: type of scrubbing handler to run
    """
    return extract_dataset('quote', work_dict, scrub_mode=scrub_mode)
# end of extract_quote_dataset


def extract_stats_dataset(
        work_dict,
        scrub_mode='sort-by-date'):
    """extract_stats_dataset

    Fetch the IEX statistics data for a ticker and
    return it as a pandas Dataframe

    :param work_dict: dictionary of args
    :param scrub_mode: type of scrubbing handler to run
    """
    return extract_dataset('stats', work_dict, scrub_mode=scrub_mode)
# end of extract_stats_dataset


def extract_peers_dataset(
        work_dict,
        scrub_mode='sort-by-date'):
    """extract_peers_dataset

    Fetch the IEX peers data for a ticker and
    return it as a pandas Dataframe

    :param work_dict: dictionary of args
    :param scrub_mode: type of scrubbing handler to run
    """
    return extract_dataset('peers', work_dict, scrub_mode=scrub_mode)
# end of extract_peers_dataset


def extract_news_dataset(
        work_dict,
        scrub_mode='sort-by-date'):
    """extract_news_dataset

    Fetch the IEX news data for a ticker and
    return it as a pandas Dataframe

    :param work_dict: dictionary of args
    :param scrub_mode: type of scrubbing handler to run
    """
    return extract_dataset('news1', work_dict, scrub_mode=scrub_mode)
# end of extract_news_dataset


def extract_financials_dataset(
        work_dict,
        scrub_mode='sort-by-date'):
    """extract_financials_dataset

    Fetch the IEX financial data for a ticker and
    return it as a pandas Dataframe

    :param work_dict: dictionary of args
    :param scrub_mode: type of scrubbing handler to run
    """
    return extract_dataset('financials', work_dict, scrub_mode=scrub_mode)
# end of extract_financials_dataset


def extract_earnings_dataset(
        work_dict,
        scrub_mode='sort-by-date'):
    """extract_earnings_dataset

    Fetch the IEX earnings data for a ticker and
    return it as a pandas Dataframe

    :param work_dict: dictionary of args
    :param scrub_mode: type of scrubbing handler to run
    """
    return extract_dataset('earnings', work_dict, scrub_mode=scrub_mode)
# end of extract_earnings_dataset


def extract_dividends_dataset(
        work_dict,
        scrub_mode='sort-by-date'):
    """extract_dividends_dataset

    Fetch the IEX dividends data for a ticker and
    return it as a pandas Dataframe

    :param work_dict: dictionary of args
    :param scrub_mode: type of scrubbing handler to run
    """
    return extract_dataset('dividends', work_dict, scrub_mode=scrub_mode)
# end of extract_dividends_dataset


def extract_company_dataset(
        work_dict,
        scrub_mode='NO_SORT'):
    """extract_company_dataset

    Fetch the IEX company data for a ticker and
    return it as a pandas Dataframe

    :param work_dict: dictionary of args
    :param scrub_mode: type of scrubbing handler to run
    """
    return extract_dataset('company', work_dict, scrub_mode=scrub_mode)
# end of extract_company_dataset


def extract_dataset(
        key,
        work_dict,
        scrub_mode='NO_SORT'):
    """extract_dataset

    Fetch the IEX key data for a ticker and
    return it as a pandas Dataframe

    :param key: IEX dataset key
    :param work_dict: dictionary of args
    :param scrub_mode: type of scrubbing handler to run
    """
    if not key or key not in keys:
        return ae_consts.NOT_RUN, None
    label = work_dict.get('label', 'extract')
    df_type = keys[key]
    df_str = iex_consts.get_datafeed_str(df_type=df_type)
    req = copy.deepcopy(work_dict)

    if 'redis_key' not in work_dict:
        # see if it's get dataset dictionary
        if f'{key}' in work_dict:
            req['redis_key'] = req[f'{key}']
            req['s3_key'] = req[f'{key}']
    # end of support for the get dataset dictionary

    log.debug(f'{label} - {df_str} - start')

    return extract_utils.perform_extract(
        df_type=df_type,
        df_str=df_str,
        work_dict=req,
        scrub_mode=scrub_mode)
# end of extract_dataset
