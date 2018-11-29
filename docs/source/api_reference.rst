Source Code
===========

These are documents for developing and understanding how the Stock Analysis Engine works. Please refer to the repository for the latest source code examples:

https://github.com/AlgoTraders/stock-analysis-engine/

Example API Requests
====================

.. automodule:: analysis_engine.api_requests
   :members: get_ds_dict,build_get_new_pricing_request,build_publish_pricing_request,build_cache_ready_pricing_dataset,build_publish_from_s3_to_redis_request,build_prepare_dataset_request,build_analyze_dataset_request,build_screener_analysis_request

Read from S3 as a String
========================

.. automodule:: analysis_engine.s3_read_contents_from_key
   :members: s3_read_contents_from_key

Get Task Results
================

.. automodule:: analysis_engine.get_task_results
   :members: get_task_results
   
Constants
=========

Utility methods and constants

.. automodule:: analysis_engine.consts
   :members: get_indicator_type_as_int,get_indicator_category_as_int,get_indicator_uses_data_as_int,get_algo_timeseries_from_int,is_celery_disabled,get_status,ppj,to_float_str,to_f,get_mb,ev,get_percent_done
