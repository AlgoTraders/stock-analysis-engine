Source Code
===========

These are documents for developing and understanding how the Stock Analysis Engine works. Please refer to the repository for the latest source code examples:

https://github.com/AlgoTraders/stock-analysis-engine/

Example API Requests
====================

.. automodule:: analysis_engine.api_requests
   :members: build_get_new_pricing_request,build_publish_pricing_request,build_cache_ready_pricing_dataset,build_publish_from_s3_to_redis_request,build_prepare_dataset_request,build_analyze_dataset_request

Constants
=========

.. automodule:: analysis_engine.consts
   :members: is_celery_disabled,ev,get_status

Read from S3 as a String
========================

.. automodule:: analysis_engine.s3_read_contents_from_key
   :members: s3_read_contents_from_key

Get Task Results
================

.. automodule:: analysis_engine.get_task_results
   :members: get_task_results
