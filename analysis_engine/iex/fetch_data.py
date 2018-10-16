"""
Fetch data from
`IEX <https://iextrading.com/developer/docs/>`__
using
`pyEX <https://github.com/timkpaine/pyEX>`__
with the factory method ``fetch_data``
"""

import analysis_engine.iex.fetch_api as fetch_api
from spylunking.log.setup_logging import build_colorized_logger
from analysis_engine.iex.consts import FETCH_DAILY
from analysis_engine.iex.consts import FETCH_MINUTE
from analysis_engine.iex.consts import FETCH_QUOTE
from analysis_engine.iex.consts import FETCH_STATS
from analysis_engine.iex.consts import FETCH_PEERS
from analysis_engine.iex.consts import FETCH_NEWS
from analysis_engine.iex.consts import FETCH_FINANCIALS
from analysis_engine.iex.consts import FETCH_EARNINGS
from analysis_engine.iex.consts import FETCH_DIVIDENDS
from analysis_engine.iex.consts import FETCH_COMPANY


log = build_colorized_logger(
    name=__name__)


def fetch_data(
        work_dict,
        fetch_type=None):
    """fetch_data

    Factory method for fetching data from
    IEX using an enum or string alias. Returns
    a pandas ``DataFrame`` and only supports
    one ticker at a time.

    Supported enums from: ``analysis_engine.iex.consts``

    ::

        fetch_type = FETCH_DAILY
        fetch_type = FETCH_MINUTE
        fetch_type = FETCH_QUOTE
        fetch_type = FETCH_STATS
        fetch_type = FETCH_PEERS
        fetch_type = FETCH_NEWS
        fetch_type = FETCH_FINANCIALS
        fetch_type = FETCH_EARNINGS
        fetch_type = FETCH_DIVIDENDS
        fetch_type = FETCH_COMPANY

    Supported ``work_dict['ft_type']`` string values:

    ::

        work_dict['ft_type'] = 'daily'
        work_dict['ft_type'] = 'minute'
        work_dict['ft_type'] = 'quote'
        work_dict['ft_type'] = 'stats'
        work_dict['ft_type'] = 'peers'
        work_dict['ft_type'] = 'news'
        work_dict['ft_type'] = 'financials'
        work_dict['ft_type'] = 'earnings'
        work_dict['ft_type'] = 'dividends'
        work_dict['ft_type'] = 'company'

    :param work_dict: dictionary of args for the pEX call
    :param fetch_type: optional - name or enum of the fetcher to create
                       can also be a lower case string
                       in work_dict['ft_type']
    """
    use_fetch_name = None
    if not fetch_type:
        fetch_type = work_dict.get(
            'ft_type',
            None)
    if fetch_type:
        use_fetch_name = str(fetch_type).lower()

    log.debug(
        'name={} type={} args={}'.format(
            use_fetch_name,
            fetch_type,
            work_dict))

    if use_fetch_name == 'daily' or fetch_type == FETCH_DAILY:
        return fetch_api.fetch_daily(
            work_dict=work_dict)
    elif use_fetch_name == 'minute' or fetch_type == FETCH_MINUTE:
        return fetch_api.fetch_minute(
            work_dict=work_dict)
    elif use_fetch_name == 'quote' or fetch_type == FETCH_QUOTE:
        return fetch_api.fetch_quote(
            work_dict=work_dict)
    elif use_fetch_name == 'stats' or fetch_type == FETCH_STATS:
        return fetch_api.fetch_stats(
            work_dict=work_dict)
    elif use_fetch_name == 'peers' or fetch_type == FETCH_PEERS:
        return fetch_api.fetch_peers(
            work_dict=work_dict)
    elif use_fetch_name == 'news' or fetch_type == FETCH_NEWS:
        return fetch_api.fetch_news(
            work_dict=work_dict)
    elif use_fetch_name == 'financials' or fetch_type == FETCH_FINANCIALS:
        return fetch_api.fetch_financials(
            work_dict=work_dict)
    elif use_fetch_name == 'earnings' or fetch_type == FETCH_EARNINGS:
        return fetch_api.fetch_earnings(
            work_dict=work_dict)
    elif use_fetch_name == 'dividends' or fetch_type == FETCH_DIVIDENDS:
        return fetch_api.fetch_dividends(
            work_dict=work_dict)
    elif use_fetch_name == 'company' or fetch_type == FETCH_COMPANY:
        return fetch_api.fetch_company(
            work_dict=work_dict)
    else:
        log.error(
            'label={} - unsupported fetch_data('
            'work_dict={}, '
            'fetch_type={}'
            ')'.format(
                work_dict.get('label', None),
                work_dict,
                fetch_type))
        raise NotImplemented
    # end of supported fetchers
# end of fetch_data
