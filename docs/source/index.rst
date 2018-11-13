.. Stock Analysis Engine documentation master file, created by
   sphinx-quickstart on Fri Sep 14 19:53:05 2018.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Stock Analysis Engine
=====================

Analyze and run algorithms on publicly traded companies from `Yahoo <https://finance.yahoo.com/>`__, `IEX Real-Time Price <https://iextrading.com/developer/docs/>`__ and `FinViz <https://finviz.com>`__ (datafeeds supported: news, screeners, quotes, dividends, daily, intraday, statistics, financials, earnings, options, and more). Once collected the data is archived in s3 (using `minio <https://minio.io>`__) and automatically cached in redis. Deploys with `Kubernetes <https://github.com/AlgoTraders/stock-analysis-engine#running-on-kubernetes>`__ or docker compose with `support for publishing alerts to Slack <https://github.com/AlgoTraders/stock-analysis-engine/blob/master/compose/docker/notebooks/Stock-Analysis-Intro-Publishing-to-Slack.ipynb>`__.

.. image:: https://i.imgur.com/pH368gy.png

The engine provides an automated, horizontally scalable stock data collection and archive pipeline with a simple extraction interface above a redis datastore.

Building Your Own Algorithms
============================

With the stack running locally on your environment, you can fetch data on an intraday basis or have an `Algorithm-ready dataset already in redis <https://github.com/AlgoTraders/stock-analysis-engine#extract-algorithm-ready-datasets>`__, then you can start you run your own algorithms by building a derived class from the `analysis_engine.algo.BaseAlgo base class <https://github.com/AlgoTraders/stock-analysis-engine/blob/master/analysis_engine/algo.py>`__.

Here is a `detailed example of building an algorithm that processes live intraday, minutely datasets <https://github.com/AlgoTraders/stock-analysis-engine/blob/master/analysis_engine/mocks/example_algo_minute.py>`__ with `real-time pricing data from IEX <https://iextrading.com/developer>`__.

#.  Start the stack with the `integration.yml docker compose file (minio, redis, engine worker, jupyter) <https://github.com/AlgoTraders/stock-analysis-engine/blob/master/compose/integration.yml>`__

    ::

        ./compose/start.sh -a

#.  Start the dataset collection job with the `automation-dataset-collection.yml docker compose file <https://github.com/AlgoTraders/stock-analysis-engine/blob/master/compose/automation-dataset-collection.yml>`__:

    ::

        ./compose/start.sh -c

    Wait for pricing engine logs to stop with ``ctrl+c``

    ::

        logs-workers.sh

#.  Run the Intraday Minute Algorithm

    .. note:: Make sure to run through the `Getting Started before continuing <https://github.com/AlgoTraders/stock-analysis-engine#getting-started>`_.

    To run the sample intraday algorithm against your live pricing datasets from the engine use:

    ::

        sa.py -t SPY -g /opt/sa/analysis_engine/mocks/example_algo_minute.py

    And to debug the algorithm's trading performance history add the ``-d`` debug flag:

    ::

        sa.py -t SPY -g /opt/sa/analysis_engine/mocks/example_algo_minute.py -d

Coming Soon
-----------

- Run an algorithm with only a local algorithm-ready file so redis is not required to develop algorithms
- Need to figure out how to use private algorithm modules inside the container without a container rebuild which might end up being a tool like the `deploy from private fork support <https://github.com/AlgoTraders/stock-analysis-engine#deploy-fork-feature-branch-to-running-containers>`__

Extract Algorithm-Ready Datasets
================================

With cached data in redis, you can use the algorithm api to extract algorithm-ready datasets and save them to a local file on disk for offline historical backtest analysis. This also creates a local archive backup with everything in redis (in case something crashes).

Extract an algorithm-ready dataset from Redis with:

::

    sa.py -t SPY -e ~/SPY-latest.json

Create a Daily Backup in a File
-------------------------------

::

    sa.py -t SPY -e ~/SPY-$(date +"%Y-%m-%d").json

Validate the Daily Backup by Examining the Dataset File
-------------------------------------------------------

::

    sa.py -t SPY -l ~/SPY-$(date +"%Y-%m-%d").json

Restore Backup into Redis
-------------------------

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
