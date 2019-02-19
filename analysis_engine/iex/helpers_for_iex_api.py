"""
Functions for getting data from IEX using HTTP

**Debugging**

Please set the ``verbose`` argument to ``True``
to enable debug logging with these calls
"""

try:
    import urllib.parse as urlparse
except ImportError:
    import urlparse as urlparse
import requests
import pandas as pd
import analysis_engine.consts as ae_consts
import analysis_engine.iex.consts as iex_consts
import analysis_engine.iex.build_auth_url as iex_auth
import spylunking.log.setup_logging as log_utils

log = log_utils.build_colorized_logger(name=__name__)


def convert_datetime_columns(
        df,
        date_cols=None,
        second_cols=None,
        tcols=None,
        ecols=None):
    """convert_datetime_columns

    Convert the IEX date columns in the ``df`` to ``datetime`` objects

    :param df: ``pandas.DataFrame`` to set columns to
        datetime objects
    :param date_cols: list of columns to convert with a date string format
        formatted: ``YYYY-MM-DD``
    :param second_cols: list of columns to convert with a date string format
        formatted: ``YYYY-MM-DD HH:MM:SS``
    :param tcols: list of columns to convert with a time format
        (this is for millisecond epoch integers)
    :param ecols: list of columns to convert with a time format
        (this is for nanosecond epoch integers)
    """
    date_cols = date_cols or iex_consts.IEX_DATE_FIELDS
    second_cols = second_cols or iex_consts.IEX_SECOND_FIELDS
    tcols = tcols or iex_consts.IEX_TIME_FIELDS
    ecols = ecols or iex_consts.IEX_EPOCH_FIELDS

    for col in date_cols:
        if col in df:
            df[col] = pd.to_datetime(
                df[col],
                format=iex_consts.IEX_DATE_FORMAT,
                errors='coerce')

    for col in second_cols:
        if col in df:
            df[col] = pd.to_datetime(
                df[col],
                format=iex_consts.IEX_TICK_FORMAT,
                errors='coerce')

    for tcol in tcols:
        if tcol in df:
            df[tcol] = pd.to_datetime(
                df[tcol],
                unit='ms',
                errors='coerce')

    for ecol in ecols:
        if ecol in df:
            df[ecol] = pd.to_datetime(
                df[ecol],
                unit='ns',
                errors='coerce')
# end of convert_datetime_columns


def get_from_iex_v1(
        url,
        verbose=False):
    """get_from_iex_v1

    Get data from the IEX Trading API (v1)
    https//api.iextrading.com/1.0/

    :param url: IEX V1 Resource URL
    :param verbose: optional - bool turn on logging
    """
    url = (
        f'{iex_consts.IEX_URL_BASE_V1}{url}')
    resp = requests.get(
        urlparse(url).geturl(),
        proxies=iex_consts.IEX_PROXIES)
    if resp.status_code == 200:
        res_data = resp.json()
        if verbose:
            proxy_str = ''
            if iex_consts.IEX_PROXIES:
                proxy_str = (
                    f'proxies={iex_consts.IEX_PROXIES} ')
            log.info(
                f'IEXAPI_V1 - url={url} '
                f'{proxy_str}'
                f'status_code={resp.status_code} '
                f'data={ae_consts.ppj(res_data)}')
        return res_data
    raise Exception(
        f'Failed to get data from IEX V1 API with '
        f'function=get_from_iex_v1 '
        f'url={url} which sent '
        f'response {resp.status_code} - {resp.text}')
# end of get_from_iex_v1


def get_from_iex_cloud(
        url,
        token=None,
        verbose=False):
    """get_from_iex_cloud

    Get data from IEX Cloud API (v2)
    https://iexcloud.io

    :param url: IEX resource url
    :param token: optional - string token for your user's
        account
    :param verbose: optional - bool turn on logging
    """
    url = (
        f'{iex_consts.IEX_URL_BASE}{url}')
    resp = requests.get(
        url,
        proxies=iex_consts.IEX_PROXIES)
    if resp.status_code == requests.codes.OK:
        res_data = resp.json()
        if verbose:
            proxy_str = ''
            if iex_consts.IEX_PROXIES:
                proxy_str = (
                    f'proxies={iex_consts.IEX_PROXIES} ')
            log.info(
                f'IEXAPI - response data for '
                f'url={url.replace(token, "REDACTED")} '
                f'{proxy_str}'
                f'status_code={resp.status_code} '
                f'data={ae_consts.ppj(res_data)}')
        return res_data
    raise Exception(
        f'Failed to get data from IEX Cloud with '
        f'function=get_from_iex_cloud '
        f'url={url} which sent '
        f'response {resp.status_code} - {resp.text}')
# end of get_from_iex_cloud


def handle_get_from_iex(
        url,
        token=None,
        version=None,
        verbose=False):
    """handle_get_from_iex

    Implementation for getting data from the IEX
    v2 or v1 api depending on if the ``token``
    argument is set:

    - `IEX Cloud (v2) <https://iexcloud.io>`__
    - `IEX Trading API (v1) <https://iextrading.com/developer/docs/>`__

    :param url: IEX resource url
    :param token: optional - string token for your user's
        account
    :version: optional - string version for the IEX Cloud
        (default is ``beta``)
    :param verbose: optional - bool turn on logging
    """
    if token:
        return get_from_iex_cloud(
            url=url,
            token=token,
            verbose=verbose)
    return get_from_iex_v1(
        url=url,
        verbose=verbose)
# handle_get_from_iex


def get_from_iex(
        url,
        token=None,
        version=None,
        verbose=False):
    """get_from_iex

    Helper for getting data from an IEX
    publishable API endpoint using a token
    as a query param on the http url.

    :param url: IEX resource url
    :param token: optional - string token for your user's
        account
    :param version: optional - version string
    :param verbose: optional - bool turn on logging
    """

    full_url = iex_auth.build_auth_url(
        url=url,
        token=token)
    return handle_get_from_iex(
        url=full_url,
        token=token,
        version=version,
        verbose=verbose)
# end of get_from_iex
