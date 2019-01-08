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

.. automodule:: analysis_engine.td.extract_df_from_redis
   :members: extract_option_calls_dataset,extract_option_puts_dataset

Tradier API - Fetch
===================

.. automodule:: analysis_engine.td.fetch_data
   :members: fetch_data

.. automodule:: analysis_engine.td.fetch_api
   :members: fetch_calls,fetch_puts

Tradier API - Get Data Helper
=============================

.. automodule:: analysis_engine.td.get_data
   :members: get_data_from_td
