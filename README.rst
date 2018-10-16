Stock Analysis Engine
=====================

Analyze information about publicly traded companies from `Yahoo <https://finance.yahoo.com/>`__ and `IEX Real-Time Price <https://iextrading.com/developer/docs/>`__ (supported data includes: news, quotes, dividends, daily, intraday, statistics, financials, earnings, options, and more). Once collected the data is archived in s3 (using `minio <https://minio.io>`__) and automatically cached in redis. Deploys with `Kubernetes <https://github.com/AlgoTraders/stock-analysis-engine#running-on-kubernetes>`__ or docker compose.

.. image:: https://i.imgur.com/pH368gy.png

The engine provides an automated, horizontally scalable stock data collection and archive pipeline with a simple extraction interface above a redis datastore.

Once collected and cached, you can quickly extract datasets with:

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

Getting Started
===============

The engine uses `Celery workers to process all tasks <http://www.celeryproject.org/>`__ and is a horizontally scalable worker pool that `natively plugs into many transports and backends <https://github.com/celery/celery#transports-and-backends>`__

If your stack is already running, please refer to the `Intro Stock Analysis using Jupyter Notebook <https://github.com/AlgoTraders/stock-analysis-engine/blob/master/compose/docker/notebooks/Stock-Analysis-Intro.ipynb>`__ for getting started.

#.  Clone

    ::

        git clone https://github.com/AlgoTraders/stock-analysis-engine.git /opt/sa
        cd /opt/sa

#.  Start Redis and Minio

    .. note:: The Minio container is set up to save data to ``/data`` so S3 files can survive a restart/reboot. On Mac OS X, please make sure to add ``/data`` (and ``/data/sa/notebooks`` for Jupyter notebooks) on the Docker Preferences -> File Sharing tab and let the docker daemon restart before trying to start the containers. If not, you will likely see errors like:

       ::

            ERROR: for minio  Cannot start service minio:
            b'Mounts denied: \r\nThe path /data/minio/data\r\nis not shared from OS X

    ::

        ./compose/start.sh

#.  Verify Redis and Minio are Running

    ::

        docker ps
        CONTAINER ID        IMAGE                COMMAND                  CREATED             STATUS                   PORTS                    NAMES
        c2d46e73c355        minio/minio          "/usr/bin/docker-ent…"   4 hours ago         Up 4 hours (healthy)                              minio
        b32838e43edb        redis:4.0.9-alpine   "docker-entrypoint.s…"   4 days ago          Up 4 hours               0.0.0.0:6379->6379/tcp   redis

Running on Ubuntu and CentOS
============================

#.  Install Packages

    Ubuntu

    ::

        sudo apt-get install make cmake gcc python3-distutils python3-tk python3 python3-apport python3-certifi python3-dev python3-pip python3-venv python3.6 redis-tools

    CentOS

    ::

        sudo yum install build-essential tkinter curl-devel make cmake python-devel python-setuptools python-pip python-virtualenv redis

#.  Create and Load Python 3 Virtual Environment

    ::

        virtualenv -p python3 /opt/venv
        source /opt/venv/bin/activate
        pip install --upgrade pip setuptools

#.  Install Analysis Pip

    ::

        pip install -e .


#.  Verify Pip installed

    ::

        pip list | grep stock-analysis-engine

Running on Mac OS X
===================

#.  Download Python 3.6

    .. note:: Python 3.7 is not supported by celery so please ensure it is python 3.6

    https://www.python.org/downloads/mac-osx/

#.  Install Packages

    ::

        brew install openssl
        brew install pyenv-virtualenv
        brew install redis

#.  Create and Load Python 3 Virtual Environment

    ::

        python3 -m venv /opt/venv
        source /opt/venv/bin/activate
        pip install --upgrade pip setuptools

#.  Install Certs

    After hitting ssl verify errors, I found `this stack overflow <https://stackoverflow.com/questions/42098126/mac-osx-python-ssl-sslerror-ssl-certificate-verify-failed-certificate-verify>`__ which shows there's an additional step for setting up python 3.6:

    ::

        /Applications/Python\ 3.6/Install\ Certificates.command

#.  Install PyCurl with OpenSSL

    ::

        PYCURL_SSL_LIBRARY=openssl LDFLAGS="-L/usr/local/opt/openssl/lib" CPPFLAGS="-I/usr/local/opt/openssl/include" pip install --no-cache-dir pycurl

#.  Install Analysis Pip

    ::

        pip install --upgrade pip setuptools
        pip install -e .

#.  Verify Pip installed

    ::

        pip list | grep stock-analysis-engine

Start Workers
=============

::

    ./start-workers.sh

Get and Publish Pricing data
============================

Please refer to the lastest API docs in the repo:

https://github.com/AlgoTraders/stock-analysis-engine/blob/master/analysis_engine/api_requests.py

Run Ticker Analysis
===================

Run the ticker analysis using the `./analysis_engine/scripts/run_ticker_analysis.py <https://github.com/AlgoTraders/stock-analysis-engine/blob/master/analysis_engine/scripts/run_ticker_analysis.py>`__:

Collect all datasets for a Ticker or Symbol
-------------------------------------------

Collect all datasets for the ticker **SPY**:

::

    run_ticker_analysis.py -t SPY

.. note:: This requires the following services are listening on:

    - redis ``localhost:6379``
    - minio ``localhost:9000``

View the Engine Worker Logs
---------------------------

::

    docker logs sa-workers-${USER}

Running Inside Docker Containers
--------------------------------

If you are using an engine that is running inside a docker container, then ``localhost`` is probably not the correct network hostname for finding ``redis`` and ``minio``.

Please set these values as needed to publish and archive the dataset artifacts if you are using the `integration <https://github.com/AlgoTraders/stock-analysis-engine/blob/master/compose/integration.yml>`__ or `notebook integration <https://github.com/AlgoTraders/stock-analysis-engine/blob/master/compose/notebook-integration.yml>`__ docker compose files for deploying the analysis engine stack:

::

    run_ticker_analysis.py -t SPY -a minio-${USER}:9000 -r redis-${USER}:6379

.. warning:: It is not recommended sharing the same Redis server with multiple engine workers from inside docker containers and outside docker. This is because the ``REDIS_ADDRESS`` and ``S3_ADDRESS`` can only be one string value at the moment. So if a job is picked up by the wrong engine (which cannot connect to the correct Redis and Minio), then it can lead to data not being cached or archived correctly and show up as connectivity failures.

Detailed Usage Example
----------------------

The `run_ticker_analysis.py script <https://github.com/AlgoTraders/stock-analysis-engine/blob/master/analysis_engine/scripts/run_ticker_analysis.py#L65>`__ supports many parameters. Here is how to set it up if you have custom ``redis`` and ``minio`` deployments like on kubernetes as `minio-service:9000 <https://github.com/AlgoTraders/stock-analysis-engine/blob/7323ad4007b44eaa511d448c8eb500cec9fe3848/k8/engine/deployment.yml#L80-L81>`__ and `redis-master:6379 <https://github.com/AlgoTraders/stock-analysis-engine/blob/7323ad4007b44eaa511d448c8eb500cec9fe3848/k8/engine/deployment.yml#L88-L89>`__:

- S3 authentication (``-k`` and ``-s``)
- S3 endpoint (``-a``)
- Redis endoint (``-r``)
- Custom S3 Key and Redis Key Name (``-n``)

::

    run_ticker_analysis.py -t SPY -g all -u pricing -k trexaccesskey -s trex123321 -a localhost:9000 -r localhost:6379 -m 4 -n SPY_demo -P 1 -N 1 -O 1 -U 1 -R 1

Usage
-----

Please refer to the `run_ticker_analysis.py script <https://github.com/AlgoTraders/stock-analysis-engine/blob/master/analysis_engine/scripts/run_ticker_analysis.py#L65>`__ for the latest supported usage if some of these are out of date:

::

    usage: run_ticker_analysis.py [-h] -t TICKER [-g FETCH_MODE] [-i TICKER_ID]
                              [-e EXP_DATE_STR] [-l LOG_CONFIG_PATH]
                              [-b BROKER_URL] [-B BACKEND_URL]
                              [-k S3_ACCESS_KEY] [-s S3_SECRET_KEY]
                              [-a S3_ADDRESS] [-S S3_SECURE]
                              [-u S3_BUCKET_NAME] [-G S3_REGION_NAME]
                              [-p REDIS_PASSWORD] [-r REDIS_ADDRESS]
                              [-n KEYNAME] [-m REDIS_DB] [-x REDIS_EXPIRE]
                              [-z STRIKE] [-c CONTRACT_TYPE] [-P GET_PRICING]
                              [-N GET_NEWS] [-O GET_OPTIONS] [-U S3_ENABLED]
                              [-R REDIS_ENABLED] [-d]

    Download and store the latest stock pricing, news, and options chain data and
    store it in S3 and Redis. Once stored, this will also start the buy and sell
    trading analysis.

    optional arguments:
    -h, --help          show this help message and exit
    -t TICKER           ticker
    -g FETCH_MODE       optional - fetch mode: all = fetch from all data sources
                        (default), yahoo = fetch from just Yahoo sources, iex =
                        fetch from just IEX sources
    -i TICKER_ID        optional - ticker id not used without a database
    -e EXP_DATE_STR     optional - options expiration date
    -l LOG_CONFIG_PATH  optional - path to the log config file
    -b BROKER_URL       optional - broker url for Celery
    -B BACKEND_URL      optional - backend url for Celery
    -k S3_ACCESS_KEY    optional - s3 access key
    -s S3_SECRET_KEY    optional - s3 secret key
    -a S3_ADDRESS       optional - s3 address format: <host:port>
    -S S3_SECURE        optional - s3 ssl or not
    -u S3_BUCKET_NAME   optional - s3 bucket name
    -G S3_REGION_NAME   optional - s3 region name
    -p REDIS_PASSWORD   optional - redis_password
    -r REDIS_ADDRESS    optional - redis_address format: <host:port>
    -n KEYNAME          optional - redis and s3 key name
    -m REDIS_DB         optional - redis database number (4 by default)
    -x REDIS_EXPIRE     optional - redis expiration in seconds
    -z STRIKE           optional - strike price
    -c CONTRACT_TYPE    optional - contract type "C" for calls "P" for puts
    -P GET_PRICING      optional - get pricing data if "1" or "0" disabled
    -N GET_NEWS         optional - get news data if "1" or "0" disabled
    -O GET_OPTIONS      optional - get options data if "1" or "0" disabled
    -U S3_ENABLED       optional - s3 enabled for publishing if "1" or "0" is
                        disabled
    -R REDIS_ENABLED    optional - redis enabled for publishing if "1" or "0" is
                        disabled
    -d                  debug

Run Publish from an Existing S3 Key to Redis
============================================

#.  Upload Integration Test Key to S3

    ::

        export INT_TESTS=1
        python -m unittest tests.test_publish_pricing_update.TestPublishPricingData.test_integration_s3_upload

#.  Confirm the Integration Test Key is in S3

    http://localhost:9000/minio/integration-tests/

#.  Run an analysis with an existing S3 key using `./analysis_engine/scripts/publish_from_s3_to_redis.py <https://github.com/AlgoTraders/stock-analysis-engine/blob/master/analysis_engine/scripts/publish_from_s3_to_redis.py>`__

    ::

        publish_from_s3_to_redis.py -t SPY -u integration-tests -k trexaccesskey -s trex123321 -a localhost:9000 -r localhost:6379 -m 4 -n integration-test-v1

#.  Confirm the Key is now in Redis

    ::

        redis-cli
        127.0.0.1:6379> select 4
        OK
        127.0.0.1:6379[4]> keys *
        keys *
        1) "SPY_demo_daily"
        2) "SPY_demo_minute"
        3) "SPY_demo_company"
        4) "integration-test-v1"
        5) "SPY_demo_stats"
        6) "SPY_demo"
        7) "SPY_demo_quote"
        8) "SPY_demo_peers"
        9) "SPY_demo_dividends"
        10) "SPY_demo_news1"
        11) "SPY_demo_news"
        12) "SPY_demo_options"
        13) "SPY_demo_pricing"
        127.0.0.1:6379[4]>

View Archives in S3 - Minio
===========================

Here's a screenshot showing the stock market dataset archives created while running on the `3-node Kubernetes cluster for distributed AI predictions <https://github.com/jay-johnson/deploy-to-kubernetes#deploying-a-distributed-ai-stack-to-kubernetes-on-centos>`__

.. image:: https://i.imgur.com/wDyPKAp.png

http://localhost:9000/minio/pricing/

Login

- username: ``trexaccesskey``
- password: ``trex123321``

Using the AWS CLI to List the Pricing Bucket

Please refer to the official steps for using the ``awscli`` pip with minio:

https://docs.minio.io/docs/aws-cli-with-minio.html

#.  Export Credentials

    ::

        export AWS_SECRET_ACCESS_KEY=trex123321
        export AWS_ACCESS_KEY_ID=trexaccesskey

#.  List Buckets

    ::

        aws --endpoint-url http://localhost:9000 s3 ls
        2018-10-02 22:24:06 company
        2018-10-02 22:24:02 daily
        2018-10-02 22:24:06 dividends
        2018-10-02 22:33:15 integration-tests
        2018-10-02 22:24:03 minute
        2018-10-02 22:24:05 news
        2018-10-02 22:24:04 peers
        2018-10-02 22:24:06 pricing
        2018-10-02 22:24:04 stats
        2018-10-02 22:24:04 quote

#.  List Pricing Bucket Contents

    ::

        aws --endpoint-url http://localhost:9000 s3 ls s3://pricing

#.  Get the Latest SPY Pricing Key

    ::

        aws --endpoint-url http://localhost:9000 s3 ls s3://pricing | grep -i spy_demo
        SPY_demo

View Caches in Redis
====================

::

    redis-cli
    127.0.0.1:6379> select 4
    OK
    127.0.0.1:6379[4]> keys *
    1) "SPY_demo"

Jupyter
=======

You can run the Jupyter notebooks by starting the `notebook-integration.yml stack <https://github.com/AlgoTraders/stock-analysis-engine/blob/master/compose/notebook-integration.yml>`__ with the command:

::

    ./compose/start.sh -j

.. warning:: On Mac OS X, please make sure ``/data/sa/notebooks`` is a shared directory on the Docker Preferences -> File Sharing tab and restart the docker daemon.

With the included Jupyter container running, you can access the `Stock Analysis Intro notebook <https://github.com/AlgoTraders/stock-analysis-engine/blob/master/compose/docker/notebooks/Stock-Analysis-Intro.ipynb>`__ at the url (default login password is ``admin``):

http://localhost:8888/notebooks/Stock-Analysis-Intro.ipynb

Distributed Automation with Docker
==================================

.. note:: Automation requires the integration stack running (redis + minio + engine) and docker-compose.

Dataset Collection
==================

Start automated dataset collection with docker compose:

::

    ./compose/start.sh -c

Datasets in Redis
=================

After running the dataset collection container, the datasets should be auto-cached in Minio (http://localhost:9000/minio/pricing/) and Redis:

::

    redis-cli
    127.0.0.1:6379> select 4
    OK
    127.0.0.1:6379[4]> keys *
    1) "SPY_2018-10-06"
    2) "AMZN_2018-10-06_peers"
    3) "AMZN_2018-10-06_pricing"
    4) "TSLA_2018-10-06_options"
    5) "SPY_2018-10-06_dividends"
    6) "NFLX_2018-10-06_minute"
    7) "TSLA_2018-10-06_news"
    8) "SPY_2018-10-06_quote"
    9) "AMZN_2018-10-06_company"
    10) "TSLA_2018-10-06"
    11) "TSLA_2018-10-06_pricing"
    12) "SPY_2018-10-06_company"
    13) "SPY_2018-10-06_stats"
    14) "NFLX_2018-10-06_peers"
    15) "NFLX_2018-10-06_quote"
    16) "SPY_2018-10-06_news1"
    17) "AMZN_2018-10-06_stats"
    18) "TSLA_2018-10-06_news1"
    19) "AMZN_2018-10-06_news"
    20) "TSLA_2018-10-06_company"
    21) "AMZN_2018-10-06_minute"
    22) "AMZN_2018-10-06_quote"
    23) "NFLX_2018-10-06_dividends"
    24) "NFLX_2018-10-06_options"
    25) "TSLA_2018-10-06_daily"
    26) "SPY_2018-10-06_news"
    27) "SPY_2018-10-06_options"
    28) "NFLX_2018-10-06"
    29) "NFLX_2018-10-06_daily"
    30) "AMZN_2018-10-06"
    31) "AMZN_2018-10-06_options"
    32) "NFLX_2018-10-06_pricing"
    33) "TSLA_2018-10-06_stats"
    34) "TSLA_2018-10-06_minute"
    35) "SPY_2018-10-06_peers"
    36) "AMZN_2018-10-06_dividends"
    37) "TSLA_2018-10-06_dividends"
    38) "NFLX_2018-10-06_company"
    39) "NFLX_2018-10-06_news"
    40) "SPY_2018-10-06_pricing"
    41) "SPY_2018-10-06_daily"
    42) "TSLA_2018-10-06_quote"
    43) "AMZN_2018-10-06_news1"
    44) "AMZN_2018-10-06_daily"
    45) "TSLA_2018-10-06_peers"
    46) "SPY_2018-10-06_minute"
    47) "NFLX_2018-10-06_stats"
    48) "NFLX_2018-10-06_news1"

Running on Kubernetes
=====================

Kubernetes Deployments - Engine
-------------------------------

Deploy the engine with:

::

    kubectl apply -f ./k8/engine/deployment.yml

Kubernetes Job - Dataset Collection
-----------------------------------

Start the dataset collection job with:

::

    kubectl apply -f ./k8/datasets/job.yml

Testing
=======

.. note:: There is a known `pandas issue that logs a warning about _timelex <https://github.com/pandas-dev/pandas/issues/18141>`__, and it will show as a warning until it is fixed in pandas. Please ignore this warning for now.

   ::

        DeprecationWarning: _timelex is a private class and may break without warning, it will be moved and or renamed in future versions.

Run all

::

    py.test --maxfail=1

Run a test case

::

    python -m unittest tests.test_publish_pricing_update.TestPublishPricingData.test_success_publish_pricing_data

Test Publishing
---------------

S3 Upload
---------

::

    python -m unittest tests.test_publish_pricing_update.TestPublishPricingData.test_success_s3_upload

Publish from S3 to Redis
------------------------

::

    python -m unittest tests.test_publish_from_s3_to_redis.TestPublishFromS3ToRedis.test_success_publish_from_s3_to_redis

Redis Cache Set
---------------

::

    python -m unittest tests.test_publish_pricing_update.TestPublishPricingData.test_success_redis_set

Prepare Dataset
---------------

::

    python -m unittest tests.test_prepare_pricing_dataset.TestPreparePricingDataset.test_prepare_pricing_data_success

End-to-End Integration Testing
==============================

Start all the containers for full end-to-end integration testing with real docker containers with the script:

::

    ./compose/start.sh -a
    -------------
    starting end-to-end integration stack: redis, minio, workers and jupyter
    Creating network "compose_default" with the default driver
    Creating redis ... done
    Creating minio ... done
    Creating sa-jupyter ... done
    Creating sa-workers ... done
    started end-to-end integration stack: redis, minio, workers and jupyter

Verify Containers are running:

::

    docker ps
    CONTAINER ID        IMAGE                                     COMMAND                  CREATED             STATUS                    PORTS                    NAMES
    f1b81a91c215        jayjohnson/stock-analysis-engine:latest   "/opt/antinex/core/d…"   35 seconds ago      Up 34 seconds                                      sa-jupyter
    183b01928d1f        jayjohnson/stock-analysis-engine:latest   "/bin/sh -c 'cd /opt…"   35 seconds ago      Up 34 seconds                                      sa-workers
    11d46bf1f0f7        minio/minio:latest                        "/usr/bin/docker-ent…"   36 seconds ago      Up 35 seconds (healthy)                            minio
    9669494b49a2        redis:4.0.9-alpine                        "docker-entrypoint.s…"   36 seconds ago      Up 35 seconds             0.0.0.0:6379->6379/tcp   redis

Stop End-to-End Stack:

::

    ./compose/stop.sh -a
    -------------
    stopping integration stack: redis, minio, workers and jupyter
    Stopping sa-jupyter ... done
    Stopping sa-workers ... done
    Stopping minio      ... done
    Stopping redis      ... done
    Removing sa-jupyter ... done
    Removing sa-workers ... done
    Removing minio      ... done
    Removing redis      ... done
    Removing network compose_default
    stopped end-to-end integration stack: redis, minio, workers and jupyter

Integration UnitTests
=====================

.. note:: please start redis and minio before running these tests.

Please enable integration tests

::

    export INT_TESTS=1

Redis
-----

::

    python -m unittest tests.test_publish_pricing_update.TestPublishPricingData.test_integration_redis_set

S3 Upload
---------

::

    python -m unittest tests.test_publish_pricing_update.TestPublishPricingData.test_integration_s3_upload


Publish from S3 to Redis
------------------------

::

    python -m unittest tests.test_publish_from_s3_to_redis.TestPublishFromS3ToRedis.test_integration_publish_from_s3_to_redis

Prepare Dataset
---------------

::

    python -m unittest tests.test_prepare_pricing_dataset.TestPreparePricingDataset.test_integration_prepare_pricing_dataset

IEX Test - Fetching All Datasets
--------------------------------

::

    python -m unittest tests.test_iex_fetch_data

IEX Test - Fetch Daily
----------------------

::

    python -m unittest tests.test_iex_fetch_data.TestIEXFetchData.test_integration_fetch_daily

IEX Test - Fetch Minute
-----------------------

::

    python -m unittest tests.test_iex_fetch_data.TestIEXFetchData.test_integration_fetch_minute

IEX Test - Fetch Stats
----------------------

::

    python -m unittest tests.test_iex_fetch_data.TestIEXFetchData.test_integration_fetch_stats

IEX Test - Fetch Peers
----------------------

::

    python -m unittest tests.test_iex_fetch_data.TestIEXFetchData.test_integration_fetch_peers

IEX Test - Fetch News
---------------------

::

    python -m unittest tests.test_iex_fetch_data.TestIEXFetchData.test_integration_fetch_news

IEX Test - Fetch Financials
---------------------------

::

    python -m unittest tests.test_iex_fetch_data.TestIEXFetchData.test_integration_fetch_financials

IEX Test - Fetch Earnings
-------------------------

::

    python -m unittest tests.test_iex_fetch_data.TestIEXFetchData.test_integration_fetch_earnings

IEX Test - Fetch Dividends
--------------------------

::

    python -m unittest tests.test_iex_fetch_data.TestIEXFetchData.test_integration_fetch_dividends

IEX Test - Fetch Company
------------------------

::

    python -m unittest tests.test_iex_fetch_data.TestIEXFetchData.test_integration_fetch_company

IEX Test - Fetch Financials Helper
----------------------------------

::

    python -m unittest tests.test_iex_fetch_data.TestIEXFetchData.test_integration_get_financials_helper

IEX Test - Extract Daily Dataset
--------------------------------

::

    python -m unittest tests.test_iex_dataset_extraction.TestIEXDatasetExtraction.test_integration_extract_daily_dataset

IEX Test - Extract Minute Dataset
---------------------------------

::

    python -m unittest tests.test_iex_dataset_extraction.TestIEXDatasetExtraction.test_integration_extract_minute_dataset

IEX Test - Extract Quote Dataset
--------------------------------

::

    python -m unittest tests.test_iex_dataset_extraction.TestIEXDatasetExtraction.test_integration_extract_quote_dataset

IEX Test - Extract Stats Dataset
--------------------------------

::

    python -m unittest tests.test_iex_dataset_extraction.TestIEXDatasetExtraction.test_integration_extract_stats_dataset

IEX Test - Extract Peers Dataset
--------------------------------

::

    python -m unittest tests.test_iex_dataset_extraction.TestIEXDatasetExtraction.test_integration_extract_peers_dataset

IEX Test - Extract News Dataset
-------------------------------

::

    python -m unittest tests.test_iex_dataset_extraction.TestIEXDatasetExtraction.test_integration_extract_news_dataset

IEX Test - Extract Financials Dataset
-------------------------------------

::

    python -m unittest tests.test_iex_dataset_extraction.TestIEXDatasetExtraction.test_integration_extract_financials_dataset

IEX Test - Extract Earnings Dataset
-----------------------------------

::

    python -m unittest tests.test_iex_dataset_extraction.TestIEXDatasetExtraction.test_integration_extract_earnings_dataset

IEX Test - Extract Dividends Dataset
------------------------------------

::

    python -m unittest tests.test_iex_dataset_extraction.TestIEXDatasetExtraction.test_integration_extract_dividends_dataset

IEX Test - Extract Company Dataset
----------------------------------

::

    python -m unittest tests.test_iex_dataset_extraction.TestIEXDatasetExtraction.test_integration_extract_company_dataset

Yahoo Test - Extract Pricing
----------------------------

::

    python -m unittest tests.test_yahoo_dataset_extraction.TestYahooDatasetExtraction.test_integration_extract_pricing

Yahoo Test - Extract News
-------------------------

::

    python -m unittest tests.test_yahoo_dataset_extraction.TestYahooDatasetExtraction.test_integration_extract_yahoo_news

Yahoo Test - Extract Option Calls
---------------------------------

::

    python -m unittest tests.test_yahoo_dataset_extraction.TestYahooDatasetExtraction.test_integration_extract_option_calls

Yahoo Test - Extract Option Puts
--------------------------------

::

    python -m unittest tests.test_yahoo_dataset_extraction.TestYahooDatasetExtraction.test_integration_extract_option_puts

Prepare a Dataset
=================

::

    ticker=SPY
    sa.py -t ${ticker} -f -o ${ticker}_latest_v1 -j prepared -u pricing -k trexaccesskey -s trex123321 -a localhost:9000 -r localhost:6379 -m 4 -n ${ticker}_demo

Debugging
=========

Most of the scripts support running without Celery workers. To run without workers in a synchronous mode use the command:

::

    export CELERY_DISABLED=1

::

    ticker=SPY
    publish_from_s3_to_redis.py -t ${ticker} -u integration-tests -k trexaccesskey -s trex123321 -a localhost:9000 -r localhost:6379 -m 4 -n integration-test-v1
    sa.py -t ${ticker} -f -o ${ticker}_latest_v1 -j prepared -u pricing -k trexaccesskey -s trex123321 -a localhost:9000 -r localhost:6379 -m 4 -n ${ticker}_demo
    run_ticker_analysis.py -t ${ticker} -g all -e 2018-10-19 -u pricing -k trexaccesskey -s trex123321 -a localhost:9000 -r localhost:6379 -m 4 -n ${ticker}_demo -P 1 -N 1 -O 1 -U 1 -R 1

Linting and Other Tools
-----------------------

#.  Linting

    ::

        flake8 .
        pycodestyle .

#.  Sphinx Docs

    ::

        cd docs
        make html

#.  Docker Admin - Pull Latest

    ::

        docker pull jayjohnson/stock-analysis-jupyter && docker pull jayjohnson/stock-analysis-engine

Deploy Fork Feature Branch to Running Containers
================================================

When developing features that impact multiple containers, you can deploy your own feature branch without redownloading or manually building docker images. With the containers running., you can deploy your own fork's branch as a new image (which are automatically saved as new docker container images).

Deploy a public or private fork into running containers
-------------------------------------------------------

::

    ./tools/update-stack.sh <git fork https uri> <optional - branch name (master by default)> <optional - fork repo name>

Example:

::

    ./tools/update-stack.sh https://github.com/jay-johnson/stock-analysis-engine.git timeseries-charts jay

Restore the containers back to the Master
-----------------------------------------

Restore the container builds back to the ``master`` branch from https://github.com/AlgoTraders/stock-analysis-engine with:

::

    ./tools/update-stack.sh https://github.com/AlgoTraders/stock-analysis-engine.git master upstream

Deploy Fork Alias
-----------------

Here's a bashrc alias for quickly building containers from a fork's feature branch:

::

    alias bd='pushd /opt/sa >> /dev/null && source /opt/venv/bin/activate && /opt/sa/tools/update-stack.sh https://github.com/jay-johnson/stock-analysis-engine.git timeseries-charts jay && popd >> /dev/null'

License
=======

Apache 2.0 - Please refer to the LICENSE_ for more details

.. _License: https://github.com/AlgoTraders/stock-analysis-engine/blob/master/LICENSE

Terms of Service
================

Data Attribution
================

This repository currently uses yahoo and `IEX <https://iextrading.com/developer/docs/>`__ for pricing data. Usage of these feeds require the following agreements in the terms of service.

IEX Real-Time Price
===================

If you redistribute our API data:

- Cite IEX using the following text and link: "Data provided for free by IEX."
- Provide a link to https://iextrading.com/api-exhibit-a in your terms of service.
- Additionally, if you display our TOPS price data, cite "IEX Real-Time Price" near the price.
