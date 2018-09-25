Stock Analysis Engine
=====================

Use this to get pricing data for tickers (news, quotes and options right now) and archive it in s3 (using `minio <https://minio.io>`__) and cache it in redis.

It uses `Celery workers to process all tasks <http://www.celeryproject.org/>`__ and is a horizontally scalable worker pool that works with many `transports and backends <https://github.com/celery/celery#transports-and-backends>`__

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

#.  Clone

    ::

        git clone https://github.com/AlgoTraders/stock-analysis-engine.git /opt/sa
        cd /opt/sa

#.  Start Redis and Minio

    .. note:: The Minio container is set up to save data to ``/data`` so S3 files can survive a restart/reboot. On Mac, please make sure to add ``/data`` on the Docker Preferences -> File Sharing tab and let the docker daemon restart before trying to start the containers. If not, you will likely see errors like:

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

Ubuntu and CentOS
-----------------

::

    virtualenv -p python3 /opt/venv && source /opt/venv/bin/activate && pip install -e .

Mac OS X
--------

#.  Download Python 3.6

    .. note:: Python 3.7 is not supported by celery so please ensure it is python 3.6

    https://www.python.org/downloads/mac-osx/

#.  Install Certs

    After hitting ssl verify errors, I found `this stack overflow <https://stackoverflow.com/questions/42098126/mac-osx-python-ssl-sslerror-ssl-certificate-verify-failed-certificate-verify>`__ which shows there's an additional step for setitng up python 3.6:

    ::

        /Applications/Python\ 3.6/Install\ Certificates.command ; exit;

#.  Install Packages

    ::

        brew install openssl
        brew install pyenv-virtualenv

#.  Create and Load Virtual Environment

    ::

        virtualenv -p python3 /opt/venv
        source /opt/venv/bin/activate

#.  Install PyCurl with OpenSSL

    ::

        PYCURL_SSL_LIBRARY=openssl LDFLAGS="-L/usr/local/opt/openssl/lib" CPPFLAGS="-I/usr/local/opt/openssl/include" pip install --no-cache-dir pycurl

#.  Install Analysis Pip

    ::

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
        2018-09-16 07:23:31 integration-tests
        2018-09-16 07:22:31 pricing

#.  List Pricing Bucket Contents

    ::

        aws --endpoint-url http://localhost:9000 s3 ls s3://pricing

#.  Get the Latest SPY Pricing Key

    ::

        aws --endpoint-url http://localhost:9000 s3 ls s3://pricing | tail -1 | awk '{print $NF}' | grep -i spy
        SPY_demo

View Caches in Redis
====================

::

    redis-cli
    127.0.0.1:6379> select 4
    OK
    127.0.0.1:6379[4]> keys *
    1) "SPY_demo"

Testing
=======

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
    run_ticker_analysis.py -t ${ticker} -e 2018-09-21 -u pricing -k trexaccesskey -s trex123321 -a localhost:9000 -r localhost:6379 -m 4 -n ${ticker}_demo -P 1 -N 1 -O 1 -U 1 -R 1

Linting
-------

flake8 .

pycodestyle .

License
=======

Apache 2.0 - Please refer to the LICENSE_ for more details

.. _License: https://github.com/AlgoTraders/stock-analysis-engine/blob/master/LICENSE
