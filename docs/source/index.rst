.. Stock Analysis Engine documentation master file, created by
   sphinx-quickstart on Fri Sep 14 19:53:05 2018.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Stock Analysis Engine
=====================

Build and tune your own investment algorithms using a distributed, fault-resilient approach capable of running many backtests and live-trading algorithms at the same time on publicly traded companies with automated datafeeds from: `Yahoo <https://finance.yahoo.com/>`__, `IEX Real-Time Price <https://iextrading.com/developer/docs/>`__ and `FinViz <https://finviz.com>`__ (includes: pricing, options, news, dividends, daily, intraday, screeners, statistics, financials, earnings, and more). Runs on Kubernetes and docker-compose.

.. image:: https://i.imgur.com/pH368gy.png

Clone and Start Redis and Minio
-------------------------------

::

    git clone https://github.com/AlgoTraders/stock-analysis-engine.git /opt/sa
    cd /opt/sa
    ./compose/start.sh

Fetch Stock Pricing for a Ticker Symbol
=======================================

.. note:: Make sure to run through the `Getting Started before running fetch and algorithms <https://github.com/AlgoTraders/stock-analysis-engine#getting-started>`__

::

    fetch -t SPY

Run and Publish Trading Performance Report for a Custom Algorithm
=================================================================

This will run a full backtest across the past 60 days in order and run the `minute-by-minute algorithm <https://github.com/AlgoTraders/stock-analysis-engine/blob/master/analysis_engine/mocks/example_algo_minute.py>`__. Once done it will publish the trading performance report to a file or minio (s3).

Write the Trading Performance Report to a Local File
----------------------------------------------------

::

    run-algo-report-to-file.sh -t SPY -b 60 -a /opt/sa/analysis_engine/mocks/example_algo_minute.py
    # run-algo-report-to-file.sh -t <TICKER> -b <NUM_DAYS_BACK> -a <CUSTOM_ALGO_MODULE>
    # run on specific date ranges with:
    # -s <start date YYYY-MM-DD> -n <end date YYYY-MM-DD>

Write the Trading Performance Report to Minio (s3)
--------------------------------------------------

::

    run-algo-report-to-s3.sh -t SPY -b 60 -a /opt/sa/analysis_engine/mocks/example_algo_minute.py

Run and Publish Trading History for a Custom Algorithm
======================================================

This will run a full backtest across the past 60 days in order and run the `minute-by-minute algorithm <https://github.com/AlgoTraders/stock-analysis-engine/blob/master/analysis_engine/mocks/example_algo_minute.py>`__. Once done it will publish the trading history to a file or minio (s3).

Write the Trading History to a Local File
-----------------------------------------

::

    run-algo-history-to-file.sh -t SPY -b 60 -a /opt/sa/analysis_engine/mocks/example_algo_minute.py

Write the Trading History to Minio (s3)
---------------------------------------

::

    run-algo-history-to-s3.sh -t SPY -b 60 -a /opt/sa/analysis_engine/mocks/example_algo_minute.py

Building Your Own Trading Algorithms
====================================

The engine supports running algorithms with live trading data or for backtesting. Use backtesting if you want to tune an algorithm's trading performance with `algorithm-ready datasets cached in redis <https://github.com/AlgoTraders/stock-analysis-engine#extract-algorithm-ready-datasets>`__. Algorithms work the same way for live trading and historical backtesting, and building your own algorithms is as simple as deriving the `base class analysis_engine.algo.BaseAlgo as needed <https://github.com/AlgoTraders/stock-analysis-engine/blob/master/analysis_engine/algo.py>`__.

As an example for building your own algorithms, please refer to the `minute-by-minute algorithm for live intraday trading analysis <https://github.com/AlgoTraders/stock-analysis-engine/blob/master/analysis_engine/mocks/example_algo_minute.py>`__ with `real-time pricing data from IEX <https://iextrading.com/developer>`__.

Developing on AWS
=================

If you are comfortable with AWS S3 usage charges, then you can run just with a redis server to develop and tune algorithms. This works for teams and for archiving datasets for disaster recovery.

Environment Variables
---------------------

Export these based off your AWS IAM credentials and S3 endpoint.

::

    export AWS_ACCESS_KEY_ID="ACCESS"
    export AWS_SECRET_ACCESS_KEY="SECRET"
    export S3_ADDRESS=s3.us-east-1.amazonaws.com

Extract and Publish to AWS S3
=============================

::

    ./tools/backup-datasets-on-s3.sh -t TICKER -q YOUR_BUCKET -k ${S3_ADDRESS} -r localhost:6379

Publish to Custom AWS S3 Bucket and Key
=======================================

::

    extract_loc=s3://YOUR_BUCKET/TICKER-latest.json
    ./tools/backup-datasets-on-s3.sh -t TICKER -e ${extract_loc} -r localhost:6379

Backtest a Custom Algorithm with a Dataset on AWS S3
====================================================

::

    backtest_loc=s3://YOUR_BUCKET/TICKER-latest.json
    custom_algo_module=/opt/sa/analysis_engine/mocks/example_algo_minute.py
    sa -t TICKER -a ${S3_ADDRESS} -r localhost:6379 -b ${backtest_loc} -g ${custom_algo_module}

Running the Full Stack Locally
==============================

While not required for backtesting, running the full stack is required for running algorithms during a live trading session. Here is how to deploy the full stack locally using docker compose.

#.  Start the stack with the `integration.yml docker compose file (minio, redis, engine worker, jupyter) <https://github.com/AlgoTraders/stock-analysis-engine/blob/master/compose/integration.yml>`__

    .. note:: The containers are set up to run price point predictions using AI with Tensorflow and Keras. Including these in the container image is easier for deployment, but inflated the docker image size to over ``2.8 GB``. Please wait while the images download as it can take a few minutes depending on your internet speed.
        ::

            (venv) jay@home1:/opt/sa$ docker images
            REPOSITORY                          TAG                 IMAGE ID            CREATED             SIZE
            jayjohnson/stock-analysis-jupyter   latest              071f97d2517e        12 hours ago        2.94GB
            jayjohnson/stock-analysis-engine    latest              1cf690880894        12 hours ago        2.94GB
            minio/minio                         latest              3a3963612183        6 weeks ago         35.8MB
            redis                               4.0.9-alpine        494c839f5bb5        5 months ago        27.8MB

    ::

        ./compose/start.sh -a

#.  Start the dataset collection job with the `automation-dataset-collection.yml docker compose file <https://github.com/AlgoTraders/stock-analysis-engine/blob/master/compose/automation-dataset-collection.yml>`__:

    .. note:: Depending on how fast you want to run intraday algorithms, you can use this tool to collect recent pricing information with a cron or `Kubernetes job <https://github.com/AlgoTraders/stock-analysis-engine/blob/master/k8/datasets/job.yml>`__

    ::

        ./compose/start.sh -c

    Wait for pricing engine logs to stop with ``ctrl+c``

    ::

        logs-workers.sh

Run a Distributed 60-day Backtest on SPY and Publish the Trading Report, Trading History and Algorithm-Ready Dataset to S3
==========================================================================================================================

Publish backtests and live trading algorithms to the engine's workers for running many algorithms at the same time. Once done, the algorithm will publish results to s3, redis or a local file. By default, the included example below publishes all datasets into minio (s3) where they can be downloaded for offline backtests or restored back into redis.

.. note:: Running distributed algorithmic workloads requires redis, minio, and the engine running

::

    num_days_back=60
    ./tools/run-algo-with-publishing.sh -t SPY -b ${num_days_back} -w

Run a Local 60-day Backtest on SPY and Publish Trading Report, Trading History and Algorithm-Ready Dataset to S3
================================================================================================================

::

    num_days_back=60
    ./tools/run-algo-with-publishing.sh -t SPY -b ${num_days_back}

Or manually with:

::

    ticker=SPY
    num_days_back=60
    use_date=$(date +"%Y-%m-%d")
    ds_id=$(uuidgen | sed -e 's/-//g')
    ticker_dataset="${ticker}-${use_date}_${ds_id}.json"
    echo "creating ${ticker} dataset: ${ticker_dataset}"
    extract_loc="s3://algoready/${ticker_dataset}"
    history_loc="s3://algohistory/${ticker_dataset}"
    report_loc="s3://algoreport/${ticker_dataset}"
    backtest_loc="s3://algoready/${ticker_dataset}"  # same as the extract_loc
    processed_loc="s3://algoprocessed/${ticker_dataset}"  # archive it when done
    start_date=$(date --date="${num_days_back} day ago" +"%Y-%m-%d")
    echo ""
    echo "extracting algorithm-ready dataset: ${extract_loc}"
    echo "sa -t SPY -e ${extract_loc} -s ${start_date} -n ${use_date}"
    sa -t SPY -e ${extract_loc} -s ${start_date} -n ${use_date}
    echo ""
    echo "running algo with: ${backtest_loc}"
    echo "sa -t SPY -p ${history_loc} -o ${report_loc} -b ${backtest_loc} -e ${processed_loc} -s ${start_date} -n ${use_date}"
    sa -t SPY -p ${history_loc} -o ${report_loc} -b ${backtest_loc} -e ${processed_loc} -s ${start_date} -n ${use_date}

Kubernetes Job - Export SPY Datasets and Publish to Minio
=========================================================

Manually run with an ``ssh-eng`` alias:

::

    function ssheng() {
        pod_name=$(kubectl get po | grep sa-engine | grep Running |tail -1 | awk '{print $1}')
        echo "logging into ${pod_name}"
        kubectl exec -it ${pod_name} bash
    }
    ssheng
    # once inside the container on kubernetes
    source /opt/venv/bin/activate
    sa -a minio-service:9000 -r redis-master:6379 -e s3://backups/SPY-$(date +"%Y-%m-%d") -t SPY

View Algorithm-Ready Datasets
-----------------------------

With the AWS cli configured you can view available algorithm-ready datasets in your minio (s3) bucket with the command:

::

    aws --endpoint-url http://localhost:9000 s3 ls s3://algoready

View Trading History Datasets
-----------------------------

With the AWS cli configured you can view available trading history datasets in your minio (s3) bucket with the command:

::

    aws --endpoint-url http://localhost:9000 s3 ls s3://algohistory

View Trading History Datasets
-----------------------------

With the AWS cli configured you can view available trading performance report datasets in your minio (s3) bucket with the command:

::

    aws --endpoint-url http://localhost:9000 s3 ls s3://algoreport

Advanced - Running Algorithm Backtests Offline
==============================================

With `extracted Algorithm-Ready datasets in minio (s3), redis or a file <https://github.com/AlgoTraders/stock-analysis-engine#extract-algorithm-ready-datasets>`__ you can develop and tune your own algorithms offline without having redis, minio, the analysis engine, or jupyter running locally.

Run a Offline Custom Algorithm Backtest with an Algorithm-Ready File
--------------------------------------------------------------------

::

    # extract with:
    sa -t SPY -e file:/tmp/SPY-latest.json
    sa -t SPY -b file:/tmp/SPY-latest.json -g /opt/sa/analysis_engine/mocks/example_algo_minute.py

Run the Intraday Minute-by-Minute Algorithm and Publish the Algorithm-Ready Dataset to S3
-----------------------------------------------------------------------------------------

Run the `included intraday algorithm <https://github.com/AlgoTraders/stock-analysis-engine/blob/master/analysis_engine/mocks/example_algo_minute.py>`__ with the latest pricing datasets use:

::

    sa -t SPY -g /opt/sa/analysis_engine/mocks/example_algo_minute.py -e s3://algoready/SPY-$(date +"%Y-%m-%d").json

And to debug an algorithm's historical trading performance add the ``-d`` debug flag:

::

    sa -d -t SPY -g /opt/sa/analysis_engine/mocks/example_algo_minute.py -e s3://algoready/SPY-$(date +"%Y-%m-%d").json

Extract Algorithm-Ready Datasets
================================

With pricing data cached in redis, you can extract algorithm-ready datasets and save them to a local file for offline historical backtesting analysis. This also serves as a local backup where all cached data for a single ticker is in a single local file.

Extract an Algorithm-Ready Dataset from Redis and Save it to a File
-------------------------------------------------------------------

::

    sa -t SPY -e ~/SPY-latest.json

Create a Daily Backup
---------------------

::

    sa -t SPY -e ~/SPY-$(date +"%Y-%m-%d").json

Validate the Daily Backup by Examining the Dataset File
-------------------------------------------------------

::

    sa -t SPY -l ~/SPY-$(date +"%Y-%m-%d").json

Validate the Daily Backup by Examining the Dataset File
-------------------------------------------------------

::

    sa -t SPY -l ~/SPY-$(date +"%Y-%m-%d").json

Restore Backup to Redis
-----------------------

Use this command to cache missing pricing datasets so algorithms have the correct data ready-to-go before making buy and sell predictions.

.. note:: By default, this command will not overwrite existing datasets in redis. It was built as a tool for merging redis pricing datasets after a VM restarted and pricing data was missing from the past few days (gaps in pricing data is bad for algorithms).

::

    sa -t SPY -L ~/SPY-$(date +"%Y-%m-%d").json

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
   run_distributed_algorithms
   run_custom_algo
   run_algo
   example_algos
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
