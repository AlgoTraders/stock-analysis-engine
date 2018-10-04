"""
Mocking pyEX data fetch api calls
"""

import pandas as pd


def chartDF(
        symbol,
        timeframe,
        date):
    """chartDF

    mock pyEX chartDF

    :param symbol: ticker symbol
    :param timeframe: timeframe argument
    :param date: date value
    """

    val = {
        'symbol': [symbol],
        'timeframe': [timeframe],
        'date': [date]
    }
    df = pd.DataFrame(
        val)
    return df
# end of chartDF


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
        symbol):
    """newsDF

    mock pyEX newsDF

    :param symbol: ticker symbol
    """

    val = {
        'symbol': [symbol],
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
