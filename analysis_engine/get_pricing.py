"""

Utilities for getting pricing data from yahoo finance for:

- pricing
- news
- options

Internal version of:
https://github.com/neberej/pinance/master/pinance/engine/yfinance2.py
"""


import datetime
import json
import urllib.request
import urllib.error
import urllib.parse
from random import randrange
from spylunking.log.setup_logging import build_colorized_logger


log = build_colorized_logger(
    name=__name__)


def create_url(
        ticker,
        exp_date_str):
    """create_url

    :param ticker: ticker to look up
    :param exp_date_str: expiration
    """
    srv = randrange(1, 3, 1)
    if exp_date_str:
        return (
            'https://query{}.finance.yahoo.com/v7/'
            'finance/options/{}?&date={}').format(
                srv,
                ticker,
                exp_date_str)
    else:
        return (
            'https://query{}.finance.yahoo.com/v7/'
            'finance/options/{}').format(
                srv,
                ticker)
# end of create_url


# Convert date/time to unix time for options
def totimestamp(
        inputdate,
        epoch=datetime.datetime(1970, 1, 1)):
    """totimestamp

    :param 1970:
    :param 1:
    :param 1:
    """
    dt = datetime.datetime.strptime(inputdate, '%Y-%m-%d')
    td = dt - epoch
    timestamp = (
        td.microseconds + (
            td.seconds + td.days * 24 * 3600
        ) * 10**6) / 1e6  # td.total_seconds()
    return int(timestamp)
# end of totimestamp


# Make request to yahoo finance
def make_request(
        ticker,
        exp_date_str=None):
    """make_request

    :param ticker: ticker to use
    :param exp_date_str: contract expiration date format ``YYYY-MM-DD``
    """
    if exp_date_str:
        use_exp_date = totimestamp(exp_date_str)
        url = create_url(ticker, use_exp_date)
    else:
        url = create_url(ticker, None)

    try:
        response = json.loads(
            urllib.request.urlopen(url).read().decode('utf-8'))
    except urllib.error.URLError as e:
        if hasattr(e, 'reason'):
            return []
        elif hasattr(e, 'code'):
            return []
    return response
# end of make_request


def extract_options_data(
        response,
        contract_type,
        strike=None):
    """extract_options_data

    :param response: previous response data
    :param contract_type: ``C`` for calls or ``P`` for puts
    :param strike: strike price
    """
    if strike:
        log.debug((
            'getting contract={} strike={}').format(
                contract_type,
                strike))
        if contract_type == 'C':
            calls = response['optionChain']['result'][0]['options'][0]['calls']
            for call in calls:
                if call['strike'] == round(strike, 1):
                    return [
                        call
                    ]

        elif contract_type == 'P':
            puts = response['optionChain']['result'][0]['options'][0]['puts']
            for put in puts:
                if put['strike'] == round(strike, 1):
                    return [
                        put
                    ]
    else:
        log.debug((
            'getting all chains'))
    # end of if strike

    return response['optionChain']['result'][0]['options']
# end of extract_options_data


def get_quotes(
        ticker):
    """get_quotes

    :param ticker: ticker to get pricing data
    """
    response = make_request(
        ticker=ticker,
        exp_date_str=None)
    try:
        quotes_data = response['optionChain']['result'][0]['quote']
        return quotes_data
    except Exception as e:
        log.error((
            'failed get_quotes(ticker={}) with ex={}').format(
                ticker,
                e))
        return []
# end of get_quotes


def get_options(
        ticker,
        contract_type,
        exp_date_str,
        strike=None):
    """get_options

    :param ticker: ticker to lookup
    :param exp_date_str: ``YYYY-MM-DD`` expiration date format
    :param strike: optional strike price, ``None`` returns
                   all option chains
    :param contract_type: ``C`` calls or ``P`` for puts, if
                          ``strike=None`` then the ``contract_type``
                          is ignored
    """
    log.info((
        'get_options ticker={} '
        'contract={} exp_date={} strike={}').format(
            ticker,
            contract_type,
            exp_date_str,
            strike))

    response = make_request(
        ticker=ticker,
        exp_date_str=exp_date_str)
    try:
        options_data = extract_options_data(
            response=response,
            contract_type=contract_type,
            strike=strike)
        return options_data
    except Exception as e:
        log.error((
            'failed get_options('
            'ticker={}, '
            'contract_type={}, '
            'exp_date_str={}, '
            'strike={}) with ex={}').format(
                ticker,
                contract_type,
                exp_date_str,
                strike,
                e))
        return []
# end of get_options
