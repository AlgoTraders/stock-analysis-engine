.. Stock Analysis Engine documentation master file, created by
   sphinx-quickstart on Fri Sep 14 19:53:05 2018.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Stock Analysis Engine
=====================

Run algorithms on publicly traded companies with data from: `Yahoo <https://finance.yahoo.com/>`__, `IEX Real-Time Price <https://iextrading.com/developer/docs/>`__ and `FinViz <https://finviz.com>`__ (default datafeeds: pricing, options, news, dividends, daily, intraday, screeners, statistics, financials, earnings, and more).

.. image:: https://i.imgur.com/pH368gy.png

Building Your Own Algorithms
============================

The engine supports running algorithms with live trading data or for backtesting. Use backtesting if you want to tune an algorithm's trading performance with `algorithm-ready datasets cached in redis <https://github.com/AlgoTraders/stock-analysis-engine#extract-algorithm-ready-datasets>`__. Algorithms work the same way for live trading and historical backtesting, and building your own algorithms is as simple as deriving the `base class analysis_engine.algo.BaseAlgo as needed <https://github.com/AlgoTraders/stock-analysis-engine/blob/master/analysis_engine/algo.py>`__.

As an example for building your own algorithms, please refer to the `minute-by-minute algorithm for live intraday trading analysis <https://github.com/AlgoTraders/stock-analysis-engine/blob/master/analysis_engine/mocks/example_algo_minute.py>`__ with `real-time pricing data from IEX <https://iextrading.com/developer>`__.

Backtesting and Live Trading Workflow
-------------------------------------

#.  Start the stack with the `integration.yml docker compose file (minio, redis, engine worker, jupyter) <https://github.com/AlgoTraders/stock-analysis-engine/blob/master/compose/integration.yml>`__

    ::

        ./compose/start.sh -a

#.  Start the dataset collection job with the `automation-dataset-collection.yml docker compose file <https://github.com/AlgoTraders/stock-analysis-engine/blob/master/compose/automation-dataset-collection.yml>`__:

    .. note:: Depending on how fast you want to run intraday algorithms, you can use this tool to collect recent pricing information with a cron or `Kubernetes job <https://github.com/AlgoTraders/stock-analysis-engine/blob/master/k8/datasets/job.yml>`__

    ::

        ./compose/start.sh -c

    Wait for pricing engine logs to stop with ``ctrl+c``

    ::

        logs-workers.sh

#.  Run the Intraday Minute-by-Minute Algorithm

    .. note:: Make sure to run through the `Getting Started before trying to run the algorithm <https://github.com/AlgoTraders/stock-analysis-engine#getting-started>`__

    To run the intraday algorithm with the latest pricing datasets use:

    ::

        sa.py -t SPY -g /opt/sa/analysis_engine/mocks/example_algo_minute.py

    And to debug an algorithm's historical trading performance add the ``-d`` debug flag:

    ::

        sa.py -t SPY -g /opt/sa/analysis_engine/mocks/example_algo_minute.py -d

Coming Soon
-----------

- Run an algorithm with a local algorithm-ready data file so redis is not required to develop and tune algorithms
- Need to figure out how to use private algorithm modules inside the container without a container rebuild which might end up being a tool like the `deploy from private fork support <https://github.com/AlgoTraders/stock-analysis-engine#deploy-fork-feature-branch-to-running-containers>`__

Extract Algorithm-Ready Datasets
================================

With pricing data cached in redis, you can extract algorithm-ready datasets and save them to a local file for offline historical backtesting analysis. This also serves as a local backup where all cached data for a single ticker is in a single local file.

Extract an Algorithm-Ready Dataset from Redis and Save it to a File
-------------------------------------------------------------------

::

    sa.py -t SPY -e ~/SPY-latest.json

Create a Daily Backup
---------------------

::

    sa.py -t SPY -e ~/SPY-$(date +"%Y-%m-%d").json

Validate the Daily Backup by Examining the Dataset File
-------------------------------------------------------

::

    sa.py -t SPY -l ~/SPY-$(date +"%Y-%m-%d").json

Restore Backup to Redis
-----------------------

Use this command to cache missing pricing datasets so algorithms have the correct data ready-to-go before making buy and sell predictions.

.. note:: By default, this command will not overwrite existing datasets in redis. It was built as a tool for merging redis pricing datasets after a VM restarted and pricing data was missing from the past few days (gaps in pricing data is bad for algorithms).

::

    sa.py -t SPY -L ~/SPY-$(date +"%Y-%m-%d").json

Fetch
-----

With redis and minio running (``./compose/start.sh``), you can fetch, cache, archive and return all of the newest datasets for tickers:

.. code-block:: python

    from analysis_engine.fetch import fetch
    d = fetch(ticker='SPY')
    for k in d['SPY']:
        print('dataset key: {}\nvalue {}\n'.format(k, d['SPY'][k]))

Extract
-------

Once collected and cached, you can extract datasets:

.. code-block:: python

    from analysis_engine.extract import extract
    d = extract(ticker='SPY')
    for k in d['SPY']:
        print('dataset key: {}\nvalue {}\n'.format(k, d['SPY'][k]))

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
   example_algo_minute
   example_algos
   run_custom_algo
   run_algo
   build_algo_request
   build_sell_order
   build_buy_order
   build_trade_history_entry
   build_entry_call_spread_details
   build_exit_call_spread_details
   build_entry_put_spread_details
   build_exit_put_spread_details
   build_option_spread_details
   algorithm_api
   show_dataset
   load_dataset
   restore_dataset
   publish
   extract
   fetch
   build_publish_request
   api_reference
   iex_api
   yahoo_api
   finviz_api
   scrub_utils
   options_utils
   charts
   tasks
   mock_api
   extract_utils
   slack_utils
   utils

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
