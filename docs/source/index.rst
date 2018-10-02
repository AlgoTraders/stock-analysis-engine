.. Stock Analysis Engine documentation master file, created by
   sphinx-quickstart on Fri Sep 14 19:53:05 2018.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

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

.. toctree::
   :maxdepth: 2
   :caption: Contents:

   README
   scripts
   api_reference
   iex_api
   yahoo_api
   charts
   mock_api

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
