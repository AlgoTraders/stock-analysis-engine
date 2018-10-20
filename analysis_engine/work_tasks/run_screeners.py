"""
Work in progress - screener-driven analysis task
"""

import analysis_engine.fetch as fetch_utils
from spylunking.log.setup_logging import build_colorized_logger


log = build_colorized_logger(
    name=__name__)


def run_screener_analysis():
    """run_screener_analysis"""

    label = 'screener'
    log.info(
        '{} - start'.format(
            label))

    """
    Input - Set up dataset sources to collect
    """

    # fetch from: 'all', 'iex' or 'yahoo'
    fetch_mode = 'iex'
    iex_datasets = [
        'daily',
        'minute',
        'quote',
        'stats',
        'peers',
        'news',
        'financials',
        'earnings',
        'dividends',
        'company'
    ]

    """
    Input - Set up required urls for building buckets
    """
    fv_urls = []

    """
    Output - Where is data getting cached and archived?
    """

    """
    Find tickers in screens
    """

    uniq_tickers = {
        'NFLX': True
    }
    tickers = []
    num_urls = len(fv_urls)

    log.info(
        '{} - pulling tickers from urls={}'.format(
            label,
            num_urls))

    log.info(
        '{} - found uniq_tickers={} from urls={}'.format(
            label,
            len(uniq_tickers),
            num_urls))

    for t in uniq_tickers:
        tickers.append(t)

    """
    pull ticker data
    """

    res = fetch_utils.fetch(
        tickers=tickers,
        fetch_mode=fetch_mode,
        iex_datasets=iex_datasets)

    print(res)

    log.info(
        '{} - done'.format(
            label))
# end of run_screener_analysis


if __name__ == '__main__':
    run_screener_analysis()
