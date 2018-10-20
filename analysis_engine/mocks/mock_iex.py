"""
Mocking pyEX data fetch api calls
"""

import pandas as pd


def chartDF(
        symbol,
        timeframe,
        date):
    """chartDF

    Code for: `mock pyEX chartDF <https://github.com/timkpaine/pyEX/b
    lob/7cc6d56f7cfb950ed3098ac1191fb204fbf22790/pyEX/stocks.py#L171>`__

    :param symbol: ticker symbol
    :param timeframe: timeframe argument
    :param date: date value
    """

    val = {
        'symbol': [symbol],
        'timeframe': [timeframe],
        'date': [date],
        'testcase': ['mock-chartDF']
    }
    df = pd.DataFrame(
        val)
    return df
# end of chartDF


def quoteDF(
        symbol):
    """quoteDF

    Code for: `mock pyEX quoteDF <https://github.com/timkpaine/pyEX/blob/7
    cc6d56f7cfb950ed3098ac1191fb204fbf22790/pyEX/stocks.py#L681>`__

    :param symbol: ticker symbol
    """

    val = {
        'symbol': [symbol],
        'testcase': ['mock-quoteDF']
    }
    df = pd.DataFrame(
        val)
    return df
# end of quoteDF


def stockStatsDF(
        symbol):
    """stockStatsDF

    mock pyEX stockStatsDF

    :param symbol: ticker symbol
    """

    val = {
        'symbol': [symbol],
        'testcase': ['mock-stockStatsDF']
    }
    df = pd.DataFrame(
        val)
    return df
# end of stockStatsDF


def peersDF(
        symbol):
    """peersDF

    mock pyEX peersDF

    :param symbol: ticker symbol
    """

    val = {
        'symbol': [symbol],
        'testcase': ['mock-peersDF']
    }
    df = pd.DataFrame(
        val)
    return df
# end of peersDF


def newsDF(
        symbol,
        count):
    """newsDF

    mock pyEX newsDF

    :param symbol: ticker symbol
    :param count: number of new items
    """

    val = {
        'symbol': [symbol],
        'count': [count],
        'testcase': ['mock-newsDF']
    }
    df = pd.DataFrame(
        val)
    return df
# end of newsDF


def financialsDF(
        symbol):
    """financialsDF

    mock pyEX financialsDF

    :param symbol: ticker symbol
    """

    val = {
        'symbol': [symbol],
        'testcase': ['mock-financialsDF']
    }
    df = pd.DataFrame(
        val)
    return df
# end of financialsDF


def earningsDF(
        symbol):
    """earningsDF

    mock pyEX earningsDF

    :param symbol: ticker symbol
    """

    val = {
        'symbol': [symbol],
        'testcase': ['mock-earningsDF']
    }
    df = pd.DataFrame(
        val)
    return df
# end of earningsDF


def dividendsDF(
        symbol,
        **kwargs):
    """dividendsDF

    mock pyEX dividendsDF

    :param symbol: ticker symbol
    :param kwargs: keyword arguments dictionary
    """

    val = {
        'symbol': [symbol],
        'testcase': ['mock-dividendsDF']
    }
    df = pd.DataFrame(
        val)
    return df
# end of dividendsDF


def companyDF(
        symbol):
    """companyDF

    mock pyEX companyDF

    :param symbol: ticker symbol
    """

    val = {
        'symbol': [symbol],
        'testcase': ['mock-companyDF']
    }
    df = pd.DataFrame(
        val)
    return df
# end of companyDF
