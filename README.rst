Stock Analysis Engine
=====================

Use this to get pricing data for tickers (news, quotes and options right now) and archive it in s3 (using `minio <https://minio.io>`__) and cache it in redis.

It uses `Celery workers to process all tasks <http://www.celeryproject.org/>`__ and is a horizontally scalable worker pool that works with many `transports and backends <https://github.com/celery/celery#transports-and-backends>`__

.. list-table::
   :header-rows: 1

   * - `Build <https://travis-ci.org/AlgoTraders/stock-analysis-engine>`__
     - `Docs <//stock-analysis-engine.readthedocs.io/en/latest/>`__
   * - .. image:: https://travis-ci.org/AlgoTraders/stock-analysis-engine?branch=master
           :alt: Travis Tests
           :target: https://travis-ci.org/AlgoTraders/stock-analysis-engine.svg
     - .. image:: https://readthedocs.org/projects/stock-analysis-engine/badge/?version=latest
           :alt: Read the Docs Stock Analysis Engine
           :target: https://readthedocs.org/projects/stock-analysis-engine/badge/?version=latest

Getting Started
===============

#.  Clone

    ::

        git clone https://github.com/AlgoTraders/stock-analysis-engine.git /opt/sa
        cd /opt/sa

#.  Start Redis and Minio

    ::

        ./compose/start.sh

#.  Verify Redis and Minio are Running

    ::

        docker ps
        CONTAINER ID        IMAGE                COMMAND                  CREATED             STATUS                   PORTS                    NAMES
        c2d46e73c355        minio/minio          "/usr/bin/docker-ent…"   4 hours ago         Up 4 hours (healthy)                              minio
        b32838e43edb        redis:4.0.9-alpine   "docker-entrypoint.s…"   4 days ago          Up 4 hours               0.0.0.0:6379->6379/tcp   redis

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

::

    run_ticker_analysis.py -t SPY -e 2018-09-21 -u pricing -k trexaccesskey -s trex123321 -a localhost:9000 -r localhost:6379 -m 4 -n SPY_demo -P 1 -N 1 -O 1 -U 1 -R 1

::

    run_ticker_analysis.py -h
    usage: run_ticker_analysis.py [-h] -t TICKER [-i TICKER_ID] [-e EXP_DATE_STR]
                                [-l LOG_CONFIG_PATH] [-b BROKER_URL]
                                [-B BACKEND_URL] [-k S3_ACCESS_KEY]
                                [-s S3_SECRET_KEY] [-a S3_ADDRESS]
                                [-S S3_SECURE] [-u S3_BUCKET_NAME]
                                [-g S3_REGION_NAME] [-p REDIS_PASSWORD]
                                [-r REDIS_ADDRESS] [-n KEYNAME] [-m REDIS_DB]
                                [-x REDIS_EXPIRE] [-z STRIKE] [-c CONTRACT_TYPE]
                                [-P GET_PRICING] [-N GET_NEWS] [-O GET_OPTIONS]
                                [-U S3_ENABLED] [-R REDIS_ENABLED] [-d]

    Download and store the latest stock pricing, news, and options chain data and
    store it in S3 and Redis. Once stored, this will also start the buy and sell
    trading analysis.

    optional arguments:
    -h, --help          show this help message and exit
    -t TICKER           ticker
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
    -g S3_REGION_NAME   optional - s3 region name
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
        1) "integration-test-v1"
        127.0.0.1:6379[4]>

View Archives in S3 - Minio
===========================

http://localhost:9000/minio/pricing/

Login

- username: ``trexaccesskey``
- password: ``trex123321``

View Caches in Redis
====================

::

    redis-cli
    127.0.0.1:6379> select 4
    OK
    127.0.0.1:6379[4]> keys *
    1) "SPY_demo"

Development
===========

::

    virtualenv -p python3 /opt/venv && source /opt/venv/bin/activate && pip install -e .

Testing
-------

Run all

::

    py.test --maxfail=1

Run a test case

::

    python -m unittest tests.test_update_prices.TestUpdatePrices.test_success_update_prices

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

Integration Tests
=================

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

Linting
-------

flake8 .

pycodestyle .

License
=======

Apache 2.0 - Please refer to the LICENSE_ for more details

.. _License: https://github.com/AlgoTraders/stock-analysis-engine/blob/master/LICENSE
