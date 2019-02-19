"""
Fetch API calls for pulling IEX Cloud Data from
a valid IEX account

.. warning:: Running these API calls will impact
    your account's monthly quota. Please be
    aware of your usage when calling these.

Please set the environment variable ``IEX_TOKEN`` to
your account token before running these calls.

More steps can be found on the docs in the
`IEX API <https://stock-analysis-engine.readth
edocs.io/en/latest/iex_api.html#iex-api>`__

**Command Line Tool Fetching Examples**

With the Analysis Engine stack running you can use
the pip's included ``fetch`` command line tool with the
following arguments to pull data (and automate it).

**Fetch Minute Data**

::

    fetch -t AAPL -g min

**Fetch Daily Data**

::

    fetch -t AAPL -g day

**Fetch Quote Data**

::

    fetch -t AAPL -g quote

**Fetch Stats Data**

::

    fetch -t AAPL -g stats

**Fetch Peers Data**

::

    fetch -t AAPL -g peers

**Fetch News Data**

::

    fetch -t AAPL -g news

**Fetch Financials Data**

::

    fetch -t AAPL -g fin

**Fetch Earnings Data**

::

    fetch -t AAPL -g earn

**Fetch Dividends Data**

::

    fetch -t AAPL -g div

**Fetch Company Data**

::

    fetch -t AAPL -g comp

**Command Line Fetch Debugging**

Add the ``-d`` flag to the ``fetch`` command to enable
verbose logging. Here is an example:

::

    fetch -t AAPL -g news -d

"""

import pandas as pd
import analysis_engine.consts as ae_consts
import analysis_engine.utils as ae_utils
import analysis_engine.dataset_scrub_utils as dataset_utils
import analysis_engine.iex.consts as iex_consts
import analysis_engine.iex.helpers_for_iex_api as iex_helpers
import spylunking.log.setup_logging as log_utils

log = log_utils.build_colorized_logger(name=__name__)


def fetch_daily(
        ticker=None,
        work_dict=None,
        scrub_mode='sort-by-date',
        verbose=False):
    """fetch_daily

    Fetch the IEX daily data for a ticker and
    return it as a ``pandas.DataFrame``.

    https://iexcloud.io/docs/api/#historical-prices

    .. code-block:: python

        import analysis_engine.iex.fetch_api as iex_fetch

        daily_df = iex_fetch.fetch_daily(ticker='SPY')
        print(daily_df)

    :param ticker: string ticker to fetch
    :param work_dict: dictionary of args
        used by the automation
    :param scrub_mode: optional - string
        type of scrubbing handler to run
    :param verbose: optional - bool to log for debugging
    """
    label = None
    if work_dict:
        if not ticker:
            ticker = work_dict.get('ticker', None)
        label = work_dict.get('label', None)

    use_url = (
        f'/stock/{ticker}/chart/1m')

    if verbose:
        log.info(
            f'{label} - daily - url={use_url} '
            f'req={work_dict} '
            f'ticker={ticker}')

    resp_json = iex_helpers.get_from_iex(
        url=use_url,
        token=iex_consts.IEX_TOKEN,
        verbose=verbose)

    df = pd.DataFrame(resp_json)

    if verbose:
        log.info(
            f'{label} - daily - url={use_url} '
            f'ticker={ticker} response '
            f'df={df.tail(5)}')

    if len(df.index) == 0:
        return df

    iex_helpers.convert_datetime_columns(
        df=df)

    cols_to_drop = [
    ]

    remove_these = None
    for c in df:
        if c in cols_to_drop:
            if not remove_these:
                remove_these = []
            remove_these.append(c)

    if remove_these:
        df = df.drop(columns=remove_these)

    df.set_index(
        [
            'date'
        ]).sort_values(by=['date'], ascending=True)

    return df
# end of fetch_daily


def fetch_minute(
        ticker=None,
        backfill_date=None,
        work_dict=None,
        scrub_mode='sort-by-date',
        verbose=False):
    """fetch_minute

    Fetch the IEX minute intraday data for a ticker and
    return it as a ``pandas.DataFrame``.

    https://iexcloud.io/docs/api/#historical-prices

    .. code-block:: python

        import analysis_engine.iex.fetch_api as iex_fetch

        minute_df = iex_fetch.fetch_minute(ticker='SPY')
        print(minute_df)

    :param ticker: string ticker to fetch
    :param backfill_date: optional - date string formatted
        ``YYYY-MM-DD`` for filling in missing minute data
    :param work_dict: dictionary of args
        used by the automation
    :param scrub_mode: optional - string
        type of scrubbing handler to run
    :param verbose: optional - bool to log for debugging
    """
    label = None
    use_date = backfill_date
    from_historical_date = None
    last_close_to_use = None
    dates = []

    if work_dict:
        label = work_dict.get('label', None)
        use_date = work_dict.get('use_date', None)
        if not ticker:
            ticker = work_dict.get('ticker', None)
        if not backfill_date:
            use_date = work_dict.get('backfill_date', None)
        if 'from_historical_date' in work_dict:
            from_historical_date = work_dict['from_historical_date']
        if 'last_close_to_use' in work_dict:
            last_close_to_use = work_dict['last_close_to_use']
        if from_historical_date and last_close_to_use:
            dates = ae_utils.get_days_between_dates(
                from_historical_date=work_dict['from_historical_date'],
                last_close_to_use=last_close_to_use)

    use_url = (
        f'/stock/{ticker}/chart/1d')

    if use_date:
        # no - chars in the date
        use_url = (
            f'/stock/{ticker}/chart/date/{use_date.replace("-", "")}')

    if verbose:
        log.info(
            f'{label} - minute - url={use_url} '
            f'req={work_dict} ticker={ticker} '
            f'fhdate={from_historical_date} '
            f'last_close={last_close_to_use} '
            f'dates={dates}')

    resp_json = iex_helpers.get_from_iex(
        url=use_url,
        token=iex_consts.IEX_TOKEN,
        verbose=verbose)

    df = pd.DataFrame(resp_json)

    if verbose:
        log.info(
            f'{label} - minute - url={use_url} '
            f'ticker={ticker} response '
            f'df={df.tail(5)}')

    if 'date' not in df:
        log.error(
            f'unable to download IEX Cloud minute '
            f'data for {ticker} on backfill_date={use_date} '
            f'df: {df} from url: {use_url} with response: {resp_json}')
        return df

    if len(df.index) == 0:
        return df

    iex_helpers.convert_datetime_columns(
        df=df)

    if not use_date:
        use_date = df['date'].iloc[-1].strftime('%Y-%m-%d')

    new_minutes = dataset_utils.build_dates_from_df_col(
        src_col='minute',
        use_date_str=use_date,
        df=df)
    df['date'] = pd.to_datetime(
        new_minutes,
        format=ae_consts.COMMON_TICK_DATE_FORMAT)
    # make sure dates are set as strings in the cache
    df['date'] = df['date'].dt.strftime(
        ae_consts.COMMON_TICK_DATE_FORMAT)
    df.set_index(
        [
            'date'
        ])
    return df
# end of fetch_minute


def fetch_quote(
        ticker=None,
        work_dict=None,
        scrub_mode='sort-by-date',
        verbose=False):
    """fetch_quote

    Fetch the IEX quote data for a ticker and
    return as a ``pandas.DataFrame``.

    https://iexcloud.io/docs/api/#quote

    .. code-block:: python

        import analysis_engine.iex.fetch_api as iex_fetch

        quote_df = iex_fetch.fetch_quote(ticker='SPY')
        print(quote_df)

    :param ticker: string ticker to fetch
    :param work_dict: dictionary of args
        used by the automation
    :param scrub_mode: optional - string
        type of scrubbing handler to run
    :param verbose: optional - bool to log for debugging
    """
    label = None
    if work_dict:
        if not ticker:
            ticker = work_dict.get('ticker', None)
        label = work_dict.get('label', None)

    use_url = (
        f'/stock/{ticker}/quote')

    if verbose:
        log.info(
            f'{label} - quote - url={use_url} '
            f'req={work_dict} ticker={ticker}')

    resp_json = iex_helpers.get_from_iex(
        url=use_url,
        token=iex_consts.IEX_TOKEN,
        verbose=verbose)

    df = pd.DataFrame([resp_json])

    if verbose:
        log.info(
            f'{label} - quote - url={use_url} '
            f'ticker={ticker} response '
            f'df={df.tail(5)}')

    if len(df.index) == 0:
        return df

    iex_helpers.convert_datetime_columns(
        df=df)

    cols_to_drop = []
    remove_these = None
    if len(cols_to_drop) > 0:
        for c in df:
            if c in cols_to_drop:
                if not remove_these:
                    remove_these = []
                remove_these.append(c)

    if remove_these:
        df = df.drop(columns=remove_these)

    return df
# end of fetch_quote


def fetch_stats(
        ticker=None,
        work_dict=None,
        scrub_mode='sort-by-date',
        verbose=False):
    """fetch_stats

    Fetch the IEX statistics data for a ticker and
    return it as a ``pandas.DataFrame``.

    https://iexcloud.io/docs/api/#key-stats

    .. code-block:: python

        import analysis_engine.iex.fetch_api as iex_fetch

        stats_df = iex_fetch.fetch_stats(ticker='SPY')
        print(stats_df)

    :param ticker: string ticker to fetch
    :param work_dict: dictionary of args
        used by the automation
    :param scrub_mode: optional - string
        type of scrubbing handler to run
    :param verbose: optional - bool to log for debugging
    """
    label = None
    if work_dict:
        if not ticker:
            ticker = work_dict.get('ticker', None)
        label = work_dict.get('label', None)

    use_url = (
        f'/stock/{ticker}/stats')

    if verbose:
        log.info(
            f'{label} - stats - url={use_url} '
            f'req={work_dict} ticker={ticker}')

    resp_json = iex_helpers.get_from_iex(
        url=use_url,
        token=iex_consts.IEX_TOKEN,
        verbose=verbose)

    df = pd.DataFrame([resp_json])

    if verbose:
        log.info(
            f'{label} - stats - url={use_url} '
            f'ticker={ticker} response '
            f'df={df.tail(5)}')

    if len(df.index) == 0:
        return df

    iex_helpers.convert_datetime_columns(
        df=df)

    cols_to_drop = []
    remove_these = None
    if len(cols_to_drop) > 0:
        for c in df:
            if c in cols_to_drop:
                if not remove_these:
                    remove_these = []
                remove_these.append(c)

    if remove_these:
        df = df.drop(columns=remove_these)

    return df
# end of fetch_stats


def fetch_peers(
        ticker=None,
        work_dict=None,
        scrub_mode='sort-by-date',
        verbose=False):
    """fetch_peers

    Fetch the IEX peers data for a ticker and
    return it as a ``pandas.DataFrame``.

    https://iexcloud.io/docs/api/#peers

    .. code-block:: python

        import analysis_engine.iex.fetch_api as iex_fetch

        peers_df = iex_fetch.fetch_peers(ticker='SPY')
        print(peers_df)

    :param ticker: string ticker to fetch
    :param work_dict: dictionary of args
        used by the automation
    :param scrub_mode: optional - string
        type of scrubbing handler to run
    :param verbose: optional - bool to log for debugging
    """
    label = None
    if work_dict:
        if not ticker:
            ticker = work_dict.get('ticker', None)
        label = work_dict.get('label', None)

    use_url = (
        f'/stock/{ticker}/relevant')

    if verbose:
        log.info(
            f'{label} - peers - url={use_url} '
            f'req={work_dict} ticker={ticker}')

    resp_json = iex_helpers.get_from_iex(
        url=use_url,
        token=iex_consts.IEX_TOKEN,
        verbose=verbose)

    df = pd.DataFrame(resp_json)

    if verbose:
        log.info(
            f'{label} - peers - url={use_url} '
            f'ticker={ticker} response '
            f'df={df.tail(5)}')

    if len(df.index) == 0:
        return df

    iex_helpers.convert_datetime_columns(
        df=df)

    cols_to_drop = []
    remove_these = None
    if len(cols_to_drop) > 0:
        for c in df:
            if c in cols_to_drop:
                if not remove_these:
                    remove_these = []
                remove_these.append(c)

    if remove_these:
        df = df.drop(columns=remove_these)

    return df
# end of fetch_peers


def fetch_news(
        ticker=None,
        num_news=5,
        work_dict=None,
        scrub_mode='sort-by-date',
        verbose=False):
    """fetch_news

    Fetch the IEX news data for a ticker and
    return it as a ``pandas.DataFrame``.

    https://iexcloud.io/docs/api/#news

    .. code-block:: python

        import analysis_engine.iex.fetch_api as iex_fetch

        news_df = iex_fetch.fetch_news(ticker='SPY')
        print(news_df)

    :param ticker: string ticker to fetch
    :param num_news: optional - int number of news
        articles to fetch
        (default is ``5`` articles)
    :param work_dict: dictionary of args
        used by the automation
    :param scrub_mode: optional - string
        type of scrubbing handler to run
    :param verbose: optional - bool to log for debugging
    """
    label = None
    if work_dict:
        if not ticker:
            ticker = work_dict.get('ticker', None)
        label = work_dict.get('label', None)
        if not num_news:
            num_news = int(work_dict.get('num_news', 5))

    use_url = (
        f'/stock/{ticker}/news/last/{num_news}')

    if verbose:
        log.info(
            f'{label} - news - url={use_url} '
            f'req={work_dict} ticker={ticker}')

    resp_json = iex_helpers.get_from_iex(
        url=use_url,
        token=iex_consts.IEX_TOKEN,
        verbose=verbose)

    df = pd.DataFrame(resp_json)

    if verbose:
        log.info(
            f'{label} - news - url={use_url} '
            f'ticker={ticker} response '
            f'df={df.tail(5)}')

    if len(df.index) == 0:
        return df

    if 'datetime' not in df:
        log.error(
            f'unable to download IEX Cloud news '
            f'data for {ticker} '
            f'df: {df} from url: {use_url} with response: {resp_json}')
        return df

    df['datetime'] = pd.to_datetime(
        df['datetime'],
        unit='ms',
        errors='coerce')

    cols_to_drop = []
    remove_these = None
    if len(cols_to_drop) > 0:
        for c in df:
            if c in cols_to_drop:
                if not remove_these:
                    remove_these = []
                remove_these.append(c)

    if remove_these:
        df = df.drop(columns=remove_these)

    return df
# end of fetch_news


def fetch_financials(
        ticker=None,
        work_dict=None,
        scrub_mode='sort-by-date',
        verbose=False):
    """fetch_financials

    Fetch the IEX financial data for a ticker and
    return it as a ``pandas.DataFrame``.

    https://iexcloud.io/docs/api/#financials

    .. code-block:: python

        import analysis_engine.iex.fetch_api as iex_fetch

        fin_df = iex_fetch.fetch_financials(ticker='SPY')
        print(fin_df)

    :param ticker: string ticker to fetch
    :param work_dict: dictionary of args
        used by the automation
    :param scrub_mode: optional - string
        type of scrubbing handler to run
    :param verbose: optional - bool to log for debugging
    """
    label = None
    if work_dict:
        if not ticker:
            ticker = work_dict.get('ticker', None)
        label = work_dict.get('label', None)

    use_url = (
        f'/stock/{ticker}/financials')

    if verbose:
        log.info(
            f'{label} - fins - url={use_url} '
            f'req={work_dict} ticker={ticker}')

    resp_json = iex_helpers.get_from_iex(
        url=use_url,
        token=iex_consts.IEX_TOKEN,
        verbose=verbose)

    df = pd.DataFrame(resp_json.get('financials', []))

    if verbose:
        log.info(
            f'{label} - fins - url={use_url} '
            f'ticker={ticker} response '
            f'df={df.tail(5)}')

    if len(df.index) == 0:
        return df

    iex_helpers.convert_datetime_columns(
        df=df)

    cols_to_drop = []
    remove_these = None
    if len(cols_to_drop) > 0:
        for c in df:
            if c in cols_to_drop:
                if not remove_these:
                    remove_these = []
                remove_these.append(c)

    if remove_these:
        df = df.drop(columns=remove_these)

    return df
# end of fetch_financials


def fetch_earnings(
        ticker=None,
        work_dict=None,
        scrub_mode='sort-by-date',
        verbose=False):
    """fetch_earnings

    Fetch the IEX earnings data for a ticker and
    return it as a ``pandas.DataFrame``.

    https://iexcloud.io/docs/api/#earnings

    .. code-block:: python

        import analysis_engine.iex.fetch_api as iex_fetch

        earn_df = iex_fetch.fetch_earnings(ticker='SPY')
        print(earn_df)

    :param ticker: string ticker to fetch
    :param work_dict: dictionary of args
        used by the automation
    :param scrub_mode: optional - string
        type of scrubbing handler to run
    :param verbose: optional - bool to log for debugging
    """
    label = None
    if work_dict:
        if not ticker:
            ticker = work_dict.get('ticker', None)
        label = work_dict.get('label', None)

    use_url = (
        f'/stock/{ticker}/earnings')

    if verbose:
        log.info(
            f'{label} - earns - url={use_url} '
            f'req={work_dict} ticker={ticker}')

    resp_json = iex_helpers.get_from_iex(
        url=use_url,
        token=iex_consts.IEX_TOKEN,
        verbose=verbose)

    df = pd.DataFrame(resp_json.get('earnings', []))

    if verbose:
        log.info(
            f'{label} - earns - url={use_url} '
            f'ticker={ticker} response '
            f'df={df.tail(5)}')

    if len(df.index) == 0:
        return df

    iex_helpers.convert_datetime_columns(
        df=df)

    cols_to_drop = []
    remove_these = None
    if len(cols_to_drop) > 0:
        for c in df:
            if c in cols_to_drop:
                if not remove_these:
                    remove_these = []
                remove_these.append(c)

    if remove_these:
        df = df.drop(columns=remove_these)

    return df
# end of fetch_earnings


def fetch_dividends(
        ticker=None,
        timeframe='3m',
        work_dict=None,
        scrub_mode='sort-by-date',
        verbose=False):
    """fetch_dividends

    Fetch the IEX dividends data for a ticker and
    return it as a ``pandas.DataFrame``.

    https://iexcloud.io/docs/api/#dividends

    .. code-block:: python

        import analysis_engine.iex.fetch_api as iex_fetch

        div_df = iex_fetch.fetch_dividends(ticker='SPY')
        print(div_df)

    :param ticker: string ticker to fetch
    :param timeframe: optional - string for setting
        dividend lookback period used for
        (default is ``3m`` for three months)
    :param work_dict: dictionary of args
        used by the automation
    :param scrub_mode: optional - string
        type of scrubbing handler to run
    :param verbose: optional - bool to log for debugging
    """
    label = None
    if work_dict:
        if not ticker:
            ticker = work_dict.get('ticker', None)
        label = work_dict.get('label', None)
        if not timeframe:
            timeframe = work_dict.get('timeframe', '3m')

    use_url = (
        f'/stock/{ticker}/dividends/{timeframe}')

    if verbose:
        log.info(
            f'{label} - divs - url={use_url} '
            f'req={work_dict} ticker={ticker}')

    resp_json = iex_helpers.get_from_iex(
        url=use_url,
        token=iex_consts.IEX_TOKEN,
        verbose=verbose)

    df = pd.DataFrame(resp_json)

    if verbose:
        log.info(
            f'{label} - divs - url={use_url} '
            f'ticker={ticker} response '
            f'df={df.tail(5)}')

    if len(df.index) == 0:
        return df

    iex_helpers.convert_datetime_columns(
        df=df)

    cols_to_drop = []
    remove_these = None
    if len(cols_to_drop) > 0:
        for c in df:
            if c in cols_to_drop:
                if not remove_these:
                    remove_these = []
                remove_these.append(c)

    if remove_these:
        df = df.drop(columns=remove_these)

    return df
# end of fetch_dividends


def fetch_company(
        ticker=None,
        work_dict=None,
        scrub_mode='NO_SORT',
        verbose=False):
    """fetch_company

    Fetch the IEX company data for a ticker and
    return it as a ``pandas.DataFrame``.

    https://iexcloud.io/docs/api/#company

    .. code-block:: python

        import analysis_engine.iex.fetch_api as iex_fetch

        comp_df = iex_fetch.fetch_company(ticker='SPY')
        print(comp_df)

    :param ticker: string ticker to fetch
    :param work_dict: dictionary of args
        used by the automation
    :param scrub_mode: optional - string
        type of scrubbing handler to run
    :param verbose: optional - bool to log for debugging
    """
    label = None
    if work_dict:
        if not ticker:
            ticker = work_dict.get('ticker', None)
        label = work_dict.get('label', None)

    use_url = (
        f'/stock/{ticker}/company')

    if verbose:
        log.info(
            f'{label} - comp - url={use_url} '
            f'req={work_dict} ticker={ticker}')

    resp_json = iex_helpers.get_from_iex(
        url=use_url,
        token=iex_consts.IEX_TOKEN,
        verbose=verbose)

    df = pd.DataFrame([resp_json])

    if verbose:
        log.info(
            f'{label} - comp - url={use_url} '
            f'ticker={ticker} response '
            f'df={df}')

    if len(df.index) == 0:
        return df

    iex_helpers.convert_datetime_columns(
        df=df)

    cols_to_drop = []
    remove_these = None
    if len(cols_to_drop) > 0:
        for c in df:
            if c in cols_to_drop:
                if not remove_these:
                    remove_these = []
                remove_these.append(c)

    if remove_these:
        df = df.drop(columns=remove_these)

    return df
# end of fetch_company
