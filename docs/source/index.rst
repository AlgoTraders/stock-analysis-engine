.. Stock Analysis Engine documentation master file, created by
   sphinx-quickstart on Fri Sep 14 19:53:05 2018.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Stock Analysis Engine
=====================

Analyze information about publicly traded companies from `Yahoo <https://finance.yahoo.com/>`__ and `IEX Real-Time Price <https://iextrading.com/developer/docs/>`__ (supported data includes: news, quotes, dividends, daily, intraday, statistics, financials, earnings, options, and more). Once collected the data is archived in s3 (using `minio <https://minio.io>`__) and automatically cached in redis. Deploys with `Kubernetes <https://github.com/AlgoTraders/stock-analysis-engine#running-on-kubernetes>`__ or docker compose.

.. image:: https://i.imgur.com/pH368gy.png

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

Table of Contents
=================

.. toctree::
   :maxdepth: 2
   :caption: Contents:

   README
   scripts
   api_reference
   iex_api
   yahoo_api
   scrub_utils
   extract_utils
   options_utils
   charts
   tasks
   mock_api

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
