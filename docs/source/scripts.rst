Scripts
=======

Run Ticker Analysis
===================

Perform ticker analysis using the included script for kicking off data gathering, caching and archival

.. automodule:: analysis_engine.scripts.run_ticker_analysis
   :members: run_ticker_analysis

Publish Stock Data from S3 to Redis
===================================

Publish stock data in an s3 key to redis

.. automodule:: analysis_engine.scripts.publish_from_s3_to_redis
   :members: publish_from_s3_to_redis

Set S3 Environment Variables
============================

Set these as needed for your S3 deployment

::

    export ENABLED_S3_UPLOAD=<'0' disabled which is the default, '1' enabled>
    export S3_ACCESS_KEY=<access key>
    export S3_SECRET_KEY=<secret key>
    export S3_REGION_NAME=<region name: us-east-1>
    export S3_ADDRESS=<S3 endpoint address host:port like: localhost:9000>
    export S3_UPLOAD_FILE=<path to file to upload>
    export S3_BUCKET=<bucket name - pricing default>
    export S3_KEY=<key name - SPY_demo default>
    export S3_SECURE=<use ssl '1', disable with '0' which is the default>

Set Redis Environment Variables
===============================

Set these as needed for your Redis deployment

::

    export ENABLED_REDIS_PUBLISH=<'0' disabled which is the default, '1' enabled>
    export REDIS_ADDRESS=<redis endpoint address host:port like: localhost:6379>
    export REDIS_KEY=<key to cache values in redis>
    export REDIS_PASSWORD=<optional - redis password>
    export REDIS_DB=<optional - redis database - 4 by default>
    export REDIS_EXPIRE=<optional - redis expiration for data in seconds>
