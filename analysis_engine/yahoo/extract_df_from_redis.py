"""
Extract an Yahoo dataset from Redis (S3 support coming soon) and
load it into a ``pandas.DataFrame``

Supported environment variables:

::

    # verbose logging in this module
    export DEBUG_EXTRACT=1

    # verbose logging for just Redis operations in this module
    export DEBUG_REDIS_EXTRACT=1

    # verbose logging for just S3 operations in this module
    export DEBUG_S3_EXTRACT=1

"""

import copy
import analysis_engine.extract_utils as extract_utils
from spylunking.log.setup_logging import build_colorized_logger
from analysis_engine.yahoo.consts import DATAFEED_PRICING_YAHOO
from analysis_engine.yahoo.consts import DATAFEED_OPTIONS_YAHOO
from analysis_engine.yahoo.consts import DATAFEED_NEWS_YAHOO
from analysis_engine.yahoo.consts import get_datafeed_str_yahoo

log = build_colorized_logger(
    name=__name__)


def extract_pricing_dataset(
        work_dict,
        scrub_mode='sort-by-date'):
    """extract_pricing_dataset

    Fetch the Yahoo pricing data for a ticker and
    return it as a pandas Dataframe

    :param work_dict: dictionary of args
    :param scrub_mode: type of scrubbing handler to run
    """
    label = work_dict.get('label', 'extract')
    df_type = DATAFEED_PRICING_YAHOO
    df_str = get_datafeed_str_yahoo(df_type=df_type)
    req = copy.deepcopy(work_dict)

    if 'redis_key' not in work_dict:
        # see if it's get dataset dictionary
        if 'daily' in req:
            req['redis_key'] = req['daily']
            req['s3_key'] = req['daily']
    # end of support for the get dataset dictionary

    log.info(
        '{} - {} - start'.format(
            label,
            df_str))

    return extract_utils.perform_extract(
        df_type=df_type,
        df_str=df_str,
        work_dict=req,
        scrub_mode=scrub_mode)
# end of extract_pricing_dataset


def extract_options_dataset(
        work_dict,
        scrub_mode='sort-by-date'):
    """extract_options_dataset

    Fetch the Yahoo options data for a ticker and
    return it as a pandas Dataframe

    :param work_dict: dictionary of args
    :param scrub_mode: type of scrubbing handler to run
    """
    label = work_dict.get('label', 'extract')
    df_type = DATAFEED_OPTIONS_YAHOO
    df_str = get_datafeed_str_yahoo(df_type=df_type)
    req = copy.deepcopy(work_dict)

    if 'redis_key' not in work_dict:
        # see if it's get dataset dictionary
        if 'minute' in work_dict:
            req['redis_key'] = req['minute']
            req['s3_key'] = req['minute']
    # end of support for the get dataset dictionary

    log.info(
        '{} - {} - start'.format(
            label,
            df_str))

    return extract_utils.perform_extract(
        df_type=df_type,
        df_str=df_str,
        work_dict=req,
        scrub_mode=scrub_mode)
# end of extract_options_dataset


def extract_yahoo_news_dataset(
        work_dict,
        scrub_mode='sort-by-date'):
    """extract_yahoo_news_dataset

    Fetch the Yahoo news data for a ticker and
    return it as a pandas Dataframe

    :param work_dict: dictionary of args
    :param scrub_mode: type of scrubbing handler to run
    """
    label = work_dict.get('label', 'extract')
    df_type = DATAFEED_NEWS_YAHOO
    df_str = get_datafeed_str_yahoo(df_type=df_type)
    req = copy.deepcopy(work_dict)

    if 'redis_key' not in work_dict:
        # see if it's get dataset dictionary
        if 'stats' in work_dict:
            req['redis_key'] = req['stats']
            req['s3_key'] = req['stats']
    # end of support for the get dataset dictionary

    log.info(
        '{} - {} - start'.format(
            label,
            df_str))

    return extract_utils.perform_extract(
        df_type=df_type,
        df_str=df_str,
        work_dict=req,
        scrub_mode=scrub_mode)
# end of extract_yahoo_news_dataset
