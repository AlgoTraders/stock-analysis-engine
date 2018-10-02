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

Publish Pricing Data Task
=========================

Publish new stock data to redis and s3 (if either of them are running and enabled)

.. autotask:: analysis_engine.work_tasks.publish_pricing_update.publish_pricing_update

Publish from S3 to Redis Task
=============================

Publish S3 key with stock data to redis and s3 (if either of them are running and enabled)

.. autotask:: analysis_engine.work_tasks.publish_from_s3_to_redis.publish_from_s3_to_redis

Prepare Pricing Dataset
=======================

Prepare dataset for analysis. This task collapses nested json dictionaries into a csv file with a header row and stores the output file in s3 and redis automatically.

.. autotask:: analysis_engine.work_tasks.prepare_pricing_dataset.prepare_pricing_dataset
