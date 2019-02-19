"""
Mocking data fetch api calls
"""

import datetime


def mock_daily(
        url,
        token=None,
        version=None,
        verbose=False):
    """mock_daily

    mock minute history for a chart

    :param url: IEX resource url
    :param token: optional - string token for your user's
        account
    :param version: optional - version string
    :param verbose: optional - boolean debug logging
    """

    val = {
        'url': url,
        'version': version,
        'symbol': url.split('/')[2],
        'timeframe': '3m',
        'date': datetime.datetime.now().strftime('%Y-%m-%d'),
        'testcase': 'mock-daily'
    }
    return [val]
# end of mock_daily


def mock_minute(
        url,
        token=None,
        version=None,
        verbose=False):
    """mock_minute

    mock minute history for a chart

    :param url: IEX resource url
    :param token: optional - string token for your user's
        account
    :param version: optional - version string
    :param verbose: optional - boolean debug logging
    """

    now = datetime.datetime.now()
    val = {
        'url': url,
        'version': version,
        'symbol': url.split('/')[2],
        'timeframe': '1d',
        'date': now.strftime('%Y-%m-%d'),
        'minute': now.strftime('%H:%M'),
        'testcase': 'mock-minute'

    }
    return [val]
# end of mock_minute


def mock_quote(
        url,
        token=None,
        version=None,
        verbose=False):
    """mock_quote

    mock quote

    :param url: IEX resource url
    :param token: optional - string token for your user's
        account
    :param version: optional - version string
    :param verbose: optional - boolean debug logging
    """

    val = {
        'url': url,
        'version': version,
        'symbol': url.split('/')[2],
        'testcase': 'mock-quote'
    }
    return val
# end of mock_quote


def mock_stats(
        url,
        token=None,
        version=None,
        verbose=False):
    """mock_stats

    mock stats

    :param url: IEX resource url
    :param token: optional - string token for your user's
        account
    :param version: optional - version string
    :param verbose: optional - boolean debug logging
    """

    val = {
        'url': url,
        'version': version,
        'symbol': url.split('/')[2],
        'testcase': 'mock-stats'
    }
    return val
# end of mock_stats


def mock_peers(
        url,
        token=None,
        version=None,
        verbose=False):
    """mock_peers

    mock peers

    :param url: IEX resource url
    :param token: optional - string token for your user's
        account
    :param version: optional - version string
    :param verbose: optional - boolean debug logging
    """

    val = {
        'url': url,
        'version': version,
        'symbol': url.split('/')[2],
        'testcase': 'mock-peers'
    }
    return [val]
# end of mock_peers


def mock_news(
        url,
        token=None,
        version=None,
        verbose=False):
    """mock_news

    mock news

    :param url: IEX resource url
    :param token: optional - string token for your user's
        account
    :param version: optional - version string
    :param verbose: optional - boolean debug logging
    """
    now = datetime.datetime.now()
    epoch = datetime.datetime.utcfromtimestamp(0)
    now_ms = (now - epoch).total_seconds() * 1000.0

    val = {
        'url': url,
        'version': version,
        'datetime': now_ms,
        'symbol': url.split('/')[2],
        'count': 5,
        'testcase': 'mock-news'
    }
    return [val]
# end of mock_news


def mock_financials(
        url,
        token=None,
        version=None,
        verbose=False):
    """mock_financials

    mock financials

    :param url: IEX resource url
    :param token: optional - string token for your user's
        account
    :param version: optional - version string
    :param verbose: optional - boolean debug logging
    """

    val = {
        'url': url,
        'version': version,
        'symbol': url.split('/')[2],
        'testcase': 'mock-financials'
    }
    return {
        'financials': [val]
    }
# end of mock_financials


def mock_earnings(
        url,
        token=None,
        version=None,
        verbose=False):
    """mock_earnings

    mock earnings

    :param url: IEX resource url
    :param token: optional - string token for your user's
        account
    :param version: optional - version string
    :param verbose: optional - boolean debug logging
    """

    val = {
        'url': url,
        'version': version,
        'symbol': url.split('/')[2],
        'testcase': 'mock-earnings'
    }
    return {
        'earnings': [val]
    }
# end of mock_earnings


def mock_dividends(
        url,
        token=None,
        version=None,
        verbose=False):
    """mock_dividends

    mock dividends

    :param url: IEX resource url
    :param token: optional - string token for your user's
        account
    :param version: optional - version string
    :param verbose: optional - boolean debug logging
    """

    val = {
        'url': url,
        'version': version,
        'symbol': url.split('/')[2],
        'testcase': 'mock-dividends'
    }
    return [val]
# end of mock_dividends


def mock_company(
        url,
        token=None,
        version=None,
        verbose=False):
    """mock_company

    mock company

    :param url: IEX resource url
    :param token: optional - string token for your user's
        account
    :param version: optional - version string
    :param verbose: optional - boolean debug logging
    """

    val = {
        'url': url,
        'version': version,
        'symbol': url.split('/')[2],
        'testcase': 'mock-company'
    }
    return val
# end of mock_company
