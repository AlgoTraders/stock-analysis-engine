Scripts
=======

Fetch Pricing Datasets from IEX Cloud and Tradier
=================================================

.. automodule:: analysis_engine.scripts.fetch_new_stock_datasets
   :members: fetch_new_stock_datasets

Backtest an Algorithm and Plot the Trading History
==================================================

.. automodule:: analysis_engine.scripts.run_backtest_and_plot_history
   :members: build_example_algo_config,ExampleCustomAlgo,run_backtest_and_plot_history

Plot the Trading History from a File on Disk
============================================

.. automodule:: analysis_engine.scripts.plot_history_from_local_file
   :members: plot_local_history_file

Publish Stock Data from S3 to Redis
===================================

Publish Stock Data from S3 to Redis
===================================

Publish stock data in an s3 key to redis

.. automodule:: analysis_engine.scripts.publish_from_s3_to_redis
   :members: publish_from_s3_to_redis

Run Aggregate and then Publish data for a Ticker from S3 to Redis
=================================================================

Publish stock data in an s3 key to redis

.. automodule:: analysis_engine.scripts.publish_ticker_aggregate_from_s3
   :members: publish_ticker_aggregate_from_s3

Stock Analysis Command Line Tool
================================

This tool is for preparing, analyzing and using datasets to run predictions using the tensorflow and keras.

.. automodule:: analysis_engine.scripts.sa
   :members: restore_missing_dataset_values_from_algo_ready_file,examine_dataset_in_file,run_sa_tool

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
    export S3_COMPILED_BUCKET=<compiled bucket name - compileddatasets default>
    export S3_KEY=<key name - SPY_demo default>
    export S3_SECURE=<use ssl '1', disable with '0' which is the default>
    export PREPARE_S3_BUCKET_NAME=<prepared dataset bucket name>
    export ANALYZE_S3_BUCKET_NAME=<analyzed dataset bucket name>

Set Redis Environment Variables
===============================

Set these as needed for your Redis deployment

::

    export ENABLED_REDIS_PUBLISH=<'0' disabled which is the default, '1' enabled>
    export REDIS_ADDRESS=<redis endpoint address host:port like: localhost:6379>
    export REDIS_KEY=<key to cache values in redis>
    export REDIS_PASSWORD=<optional - redis password>
    export REDIS_DB=<optional - redis database - 0 by default>
    export REDIS_EXPIRE=<optional - redis expiration for data in seconds>
