"""
Get defaults fields for supported teyps of data
"""

import analysis_engine.iex.consts as iex_consts
import spylunking.log.setup_logging as log_utils

log = log_utils.build_colorized_logger(name=__name__)


def get_default_fields(
            field):
    """get_default_fields

    :param field: types of data to get
    """
    use_field = str(field).lower()
    if use_field == 'daily' or field == iex_consts.DATAFEED_DAILY:
        return ['KEY', 'date']
    elif use_field == 'quote' or field == iex_consts.DATAFEED_QUOTE:
        return ['KEY', 'date', 'minute']
    elif use_field == 'stats' or field == iex_consts.DATAFEED_STATS:
        return ['KEY']
    elif use_field == 'peers' or field == iex_consts.DATAFEED_PEERS:
        return ['KEY', 'peer']
    elif use_field == 'news' or field == iex_consts.DATAFEED_NEWS:
        return ['KEY', 'datetime']
    elif use_field == 'financials' or field == iex_consts.DATAFEED_FINANCIALS:
        return ['KEY', 'reportDate']
    elif use_field == 'earnings' or field == iex_consts.DATAFEED_EARNINGS:
        return ['KEY', 'EPSReportDate']
    elif use_field == 'dividends' or field == iex_consts.DATAFEED_DIVIDENDS:
        return ['KEY', 'exDate']
    elif use_field == 'company' or field == iex_consts.DATAFEED_COMPANY:
        return ['KEY']
    else:
        log.error(
            f'get_default_fields({field}) is not a supported '
            'field')
        raise NotImplementedError
# end of get_default_fields
