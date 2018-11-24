Mocks and Testing
=================

Known Issues
------------


.. note:: There is a known `pandas issue that logs a warning about _timelex <https://github.com/pandas-dev/pandas/issues/18141>`__, and it will show as a warning until it is fixed in pandas. Please ignore this warning for now.

   ::

        DeprecationWarning: _timelex is a private class and may break without warning, it will be moved and or renamed in future versions.


Run All Tests
-------------

::

    py.test --maxfail=1


Mock S3 Boto Utilities
======================

These are testing utilities for mocking S3 functionality without having an s3 endpoint running.

.. automodule:: analysis_engine.mocks.mock_boto3_s3
   :members: MockBotoS3Bucket,MockBotoS3AllBuckets,MockBotoS3,build_boto3_resource,mock_s3_read_contents_from_key_ev,mock_publish_from_s3_to_redis,mock_publish_from_s3_to_redis_err,mock_publish_from_s3_exception

Mock Redis Utilities
====================

These are testing utilities for mocking Redis's functionality without having a Redis server running.

.. automodule:: analysis_engine.mocks.mock_redis
   :members: MockRedis,MockRedisFailToConnect

Mock Yahoo Utilities
====================

These are testing utilities for mocking Yahoo's functionality without having internet connectivity to fetch data from Yahoo.

.. automodule:: analysis_engine.mocks.mock_pinance
   :members: mock_get_options,MockPinance

Mock IEX Utilities
==================

These are testing utilities for mocking IEX functionality without having internet connectivity to fetch data from IEX.

.. automodule:: analysis_engine.mocks.mock_iex
   :members: chartDF,stockStatsDF,peersDF,newsDF,financialsDF,earningsDF,dividendsDF,companyDF

Mock TA Lib
===========

These are mock talib functions to help test indicators using talib.

.. automodule:: analysis_engine.mocks.mock_talib
   :members: WILLR
