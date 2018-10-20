.. Stock Analysis Engine documentation master file, created by
   sphinx-quickstart on Fri Sep 14 19:53:05 2018.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Stock Analysis Engine
=====================

Analyze information about publicly traded companies from `Yahoo <https://finance.yahoo.com/>`__, `IEX Real-Time Price <https://iextrading.com/developer/docs/>`__ and `FinViz <https://finviz.com>`__ (datafeeds supported: news, screeners, quotes, dividends, daily, intraday, statistics, financials, earnings, options, and more). Once collected the data is archived in s3 (using `minio <https://minio.io>`__) and automatically cached in redis. Deploys with `Kubernetes <https://github.com/AlgoTraders/stock-analysis-engine#running-on-kubernetes>`__ or docker compose with `support for publishing alerts to Slack <https://github.com/AlgoTraders/stock-analysis-engine/blob/master/compose/docker/notebooks/Stock-Analysis-Intro-Publishing-to-Slack.ipynb>`__.

.. image:: https://i.imgur.com/pH368gy.png

The engine provides an automated, horizontally scalable stock data collection and archive pipeline with a simple extraction interface above a redis datastore.

Fetch
-----

With the containers running, you can fetch, cache, archive and return all of the newest datasets for tickers:

.. code-block:: python

    from analysis_engine.fetch import fetch
    d = fetch(ticker='NFLX')
    print(d)
    for k in d['rec']['ticker_dict']['NFLX']:
        print('dataset key: {}'.format(k))

Extract
-------

Once collected and cached, you can quickly extract datasets from redis with:

.. code-block:: python

    from analysis_engine.api_requests import get_ds_dict
    from analysis_engine.yahoo.extract_df_from_redis import extract_option_calls_dataset
    dataset_req = get_ds_dict(ticker='NFLX', label='nflx-test')
    extract_status, netflix_call_options_df = extract_option_calls_dataset(dataset_req)
    print(netflix_call_options_df)

Please refer to the `Stock Analysis Intro Extracting Datasets Jupyter Notebook <https://github.com/AlgoTraders/stock-analysis-engine/blob/master/compose/docker/notebooks/Stock-Analysis-Intro-Extracting-Datasets.ipynb>`__ for the latest usage examples.

.. list-table::
   :header-rows: 1

   * - `Build <https://travis-ci.org/AlgoTraders/stock-analysis-engine>`__
     - `Docs <https://stock-analysis-engine.readthedocs.io/en/latest/README.html>`__
   * - .. image:: https://api.travis-ci.org/AlgoTraders/stock-analysis-engine.svg
           :alt: Travis Tests
           :target: https://travis-ci.org/AlgoTraders/stock-analysis-engine
     - .. image:: https://readthedocs.org/projects/stock-analysis-engine/badge/?version=latest
           :alt: Read the Docs Stock Analysis Engine
           :target: https://stock-analysis-engine.readthedocs.io/en/latest/README.html

Table of Contents
=================

.. toctree::
   :maxdepth: 2
   :caption: Contents:

   README
   scripts
   api_reference
   iex_api
   yahoo_api
   finviz_api
   scrub_utils
   extract_utils
   options_utils
   charts
   tasks
   mock_api
   slack_utils
   utils

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
