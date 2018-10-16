"""
Get defaults fields for supported teyps of data
"""
from analysis_engine.iex.consts import DATAFEED_DAILY
from analysis_engine.iex.consts import DATAFEED_QUOTE
from analysis_engine.iex.consts import DATAFEED_STATS
from analysis_engine.iex.consts import DATAFEED_PEERS
from analysis_engine.iex.consts import DATAFEED_NEWS
from analysis_engine.iex.consts import DATAFEED_FINANCIALS
from analysis_engine.iex.consts import DATAFEED_EARNINGS
from analysis_engine.iex.consts import DATAFEED_DIVIDENDS
from analysis_engine.iex.consts import DATAFEED_COMPANY
from spylunking.log.setup_logging import build_colorized_logger

log = build_colorized_logger(
    name=__name__)


def get_default_fields(
            field):
    """get_default_fields

    :param field: types of data to get
    """
    use_field = str(field).lower()
    if use_field == 'daily' or field == DATAFEED_DAILY:
        return ['KEY', 'date']
    elif use_field == 'quote' or field == DATAFEED_QUOTE:
        return ['KEY', 'date', 'minute']
    elif use_field == 'stats' or field == DATAFEED_STATS:
        return ['KEY']
    elif use_field == 'peers' or field == DATAFEED_PEERS:
        return ['KEY', 'peer']
    elif use_field == 'news' or field == DATAFEED_NEWS:
        return ['KEY', 'datetime']
    elif use_field == 'financials' or field == DATAFEED_FINANCIALS:
        return ['KEY', 'reportDate']
    elif use_field == 'earnings' or field == DATAFEED_EARNINGS:
        return ['KEY', 'EPSReportDate']
    elif use_field == 'dividends' or field == DATAFEED_DIVIDENDS:
        return ['KEY', 'exDate']
    elif use_field == 'company' or field == DATAFEED_COMPANY:
        return ['KEY']
    else:
        log.error(
            'get_default_fields({}) is not a supported '
            'field'.format(
                field))
        raise NotImplemented
# end of get_default_fields
