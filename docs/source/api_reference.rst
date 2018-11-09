Source Code
===========

These are documents for developing and understanding how the Stock Analysis Engine works. Please refer to the repository for the latest source code examples:

https://github.com/AlgoTraders/stock-analysis-engine/

Getting Datasets for Stock Tickers
==================================

.. automodule:: analysis_engine.fetch
   :members: fetch

Example API Requests
====================

.. automodule:: analysis_engine.api_requests
   :members: get_ds_dict,build_get_new_pricing_request,build_publish_pricing_request,build_cache_ready_pricing_dataset,build_publish_from_s3_to_redis_request,build_prepare_dataset_request,build_analyze_dataset_request,build_screener_analysis_request,build_algo_request,build_buy_order,build_sell_order,build_trade_history_entry,build_option_spread_details,build_entry_call_spread_details,build_exit_call_spread_details,build_entry_put_spread_details,build_exit_put_spread_details

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
