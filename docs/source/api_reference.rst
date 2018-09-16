Source Code
===========

These are documents for developing and understanding how the Stock Analysis Engine works. Please refer to the repository for the latest source code examples:

https://github.com/AlgoTraders/stock-analysis-engine/

Example API Requests
====================

.. automodule:: analysis_engine.api_requests
   :members: build_get_new_pricing_request,build_publish_pricing_request,build_cache_ready_pricing_dataset,build_publish_from_s3_to_redis_request

Constants
=========

.. automodule:: analysis_engine.consts
   :members:

Celery Worker Tasks
===================

Celery tasks are automatically processed by the workers. You can turn off celery task publishing by setting the environment variable ``CELERY_DISABLED`` is set to ``1`` (by default celery is enabled for task publishing).

Handle Pricing Update Task
==========================

Get the latest stock news, quotes and options chains for a ticker and publish the values to redis and S3 for downstream analysis.

.. autotask:: analysis_engine.work_tasks.handle_pricing_update_task.handle_pricing_update_task

Get New Pricing Data Task
=========================

.. autotask:: analysis_engine.work_tasks.get_new_pricing_data.get_new_pricing_data
.. automodule:: analysis_engine.work_tasks.get_new_pricing_data
   :members: run_get_new_pricing_data

Publish Pricing Data Task
=========================

Publish new stock data to redis and s3 (if either of them are running and enabled)

.. autotask:: analysis_engine.work_tasks.publish_pricing_update.publish_pricing_update
.. automodule:: analysis_engine.work_tasks.publish_pricing_update
   :members: run_publish_pricing_update

Publish from S3 to Redis Task
=============================

Publish S3 key with stock data to redis and s3 (if either of them are running and enabled)

.. autotask:: analysis_engine.work_tasks.publish_from_s3_to_redis.publish_from_s3_to_redis
.. automodule:: analysis_engine.work_tasks.publish_from_s3_to_redis
   :members: run_publish_from_s3_to_redis

Read from S3 as a String
========================

.. automodule:: analysis_engine.s3_read_contents_from_key
   :members: s3_read_contents_from_key
