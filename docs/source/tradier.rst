How to Setup Tradier Authentication
===================================

#.  Sign up for a develop account and get a token.

    https://developer.tradier.com/getting_started

#.  Export Environment Variable

    ::

        export TD_TOKEN=<TRADIER_ACCOUNT_TOKEN>

.. automodule:: analysis_engine.td.consts
   :members: get_auth_headers

Tradier API Documentation
=========================

Tradier API - Extraction
========================

Once fetched you can extract the options data with:

.. code-block:: python

    import analysis_engine.td.extract_df_from_redis as td_extract

    # extract by historical date is also supported:
    # date='2019-02-15'
    calls_status, calls_df = td_extract.extract_option_calls_dataset(
        ticker='SPY')
    puts_status, puts_df = td_extract.extract_option_puts_dataset(
        ticker='SPY')

    print(f'SPY Option Calls from Tradier extract status={calls_status}:')
    print(calls_df)

    print(f'SPY Option Puts from Tradier extract status={puts_status}:')
    print(puts_df)

.. automodule:: analysis_engine.td.extract_df_from_redis
   :members: extract_option_calls_dataset,extract_option_puts_dataset

Tradier API - Fetch
===================

Please use the command line tool to store the data in redis correctly for the extraction tools.

::

    fetch -t TICKER -g td
    # fetch -t SPY -g td

Here is how to use the fetch api:

.. code-block:: python

    import analysis_engine.td.fetch_api as td_fetch

    # Please set the TD_TOKEN environment variable to your token
    calls_status, calls_df = td_fetch.fetch_calls(
        ticker='SPY')
    puts_status, puts_df = td_fetch.fetch_puts(
        ticker='SPY')

    print(f'Fetched SPY Option Calls from Tradier status={calls_status}:')
    print(calls_df)

    print(f'Fetched SPY Option Puts from Tradier status={puts_status}:')
    print(puts_df)

.. automodule:: analysis_engine.td.fetch_data
   :members: fetch_data

.. automodule:: analysis_engine.td.fetch_api
   :members: fetch_calls,fetch_puts

Tradier API - Get Data Helper
=============================

.. automodule:: analysis_engine.td.get_data
   :members: get_data_from_td
