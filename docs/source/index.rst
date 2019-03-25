.. Stock Analysis Engine documentation master file, created by
   sphinx-quickstart on Fri Sep 14 19:53:05 2018.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Stock Analysis Engine
=====================

Build and tune investment algorithms for use with `artificial intelligence (deep neural networks) <https://github.com/AlgoTraders/stock-analysis-engine/blob/master/compose/docker/notebooks/Comparing-3-Deep-Neural-Networks-Trained-to-Predict-a-Stocks-Closing-Price-Using-The-Analysis-Engine.ipynb>`__ with a distributed stack for running backtests using live pricing data on publicly traded companies with automated datafeeds from: `IEX Cloud <https://iexcloud.io/>`__, `Tradier <https://tradier.com/>`__ and `FinViz <https://finviz.com>`__ (includes: pricing, options, news, dividends, daily, intraday, screeners, statistics, financials, earnings, and more).

Kubernetes users please refer to `the Helm guide to get started <https://stock-analysis-engine.readthedocs.io/en/latest/deploy_on_kubernetes_using_helm.html>`__

.. image:: https://i.imgur.com/tw2wJ6t.png

Fetch the Latest Pricing Data
=============================

Supported fetch methods for getting pricing data:

- Command line using ``fetch`` command
- `IEX Cloud Fetch API <https://stock-analysis-engine.readthedocs.io/en/latest/iex_api.html#iex-fetch-api-reference>`__
- `Tradier Fetch API <https://stock-analysis-engine.readthedocs.io/en/latest/tradier.html#tradier-fetch-api-reference>`__
- Docker-compose using ``./compose/start.sh -c``
- Kubernetes jobs: `Fetch Intraday <https://github.com/AlgoTraders/stock-analysis-engine/blob/master/k8/datasets/pull_intraday_per_minute.yml>`__, `Fetch Daily <https://github.com/AlgoTraders/stock-analysis-engine/blob/master/k8/datasets/pull_daily.yml>`__, `Fetch Weekly <https://github.com/AlgoTraders/stock-analysis-engine/blob/master/k8/datasets/pull_weekly.yml>`__, or `Fetch from only Tradier <https://github.com/AlgoTraders/stock-analysis-engine/blob/master/k8/datasets/pull_tradier_per_minute.yml>`__

Fetch using the Command Line
----------------------------

Here is a video showing how to fetch the latest pricing data for a ticker using the command line:

.. image:: https://asciinema.org/a/220460.png
    :target: https://asciinema.org/a/220460?autoplay=1
    :alt: Fetch Pricing Data using the Command Line

#.  Clone to ``/opt/sa``

    ::

        git clone https://github.com/AlgoTraders/stock-analysis-engine.git /opt/sa
        cd /opt/sa

#.  Create Docker Mounts and Start Redis and Minio

    This will pull `Redis <https://hub.docker.com/_/redis>`__ and `Minio <https://hub.docker.com/r/minio/minio>`__ docker images.

    ::

        ./compose/start.sh -a

#.  Fetch All Pricing Data

    #.  `Run through the Getting Started section <https://github.com/AlgoTraders/stock-analysis-engine#getting-started>`__

    #.  Fetch pricing data from `IEX Cloud (requires an account and uses on-demand usage pricing) <https://iexcloud.io/cloud-login#/register/>`__ and `Tradier (requires an account) <https://developer.tradier.com/getting_started>`__:

        - Set the **IEX_TOKEN** environment variable to fetch from the IEX Cloud datafeeds:

        ::

            export IEX_TOKEN=YOUR_IEX_TOKEN

        - Set the **TD_TOKEN** environment variable to fetch from the Tradier datafeeds:

        ::

            export TD_TOKEN=YOUR_TRADIER_TOKEN

        - Fetch with:

        ::

            fetch -t SPY

        - Fetch only from **IEX** with **-g iex**:

        ::

            fetch -t SPY -g iex
            # and fetch from just Tradier with:
            # fetch -t SPY -g td

        - Fetch previous 30 calendar days of intraday minute pricing data from IEX Cloud

        ::

            backfill-minute-data.sh TICKER
            # backfill-minute-data.sh SPY

    #.  Please refer to `the documentation for more examples on controlling your pricing request usage (including how to run fetches for intraday, daily and weekly use cases) <https://stock-analysis-engine.readthedocs.io/en/latest/scripts.html#module-analysis_engine.scripts.fetch_new_stock_datasets>`__

    .. note:: Yahoo `disabled the YQL finance API so fetching pricing data from yahoo is disabled by default <https://developer.yahoo.com/yql/>`__

#.  View the Compressed Pricing Data in Redis

    ::

        redis-cli keys "SPY_*"
        redis-cli get "<key like SPY_2019-01-08_minute>"

Run Backtests with the Algorithm Runner API
===========================================

Run a backtest with the latest pricing data:

.. code-block:: python

    import analysis_engine.algo_runner as algo_runner
    import analysis_engine.plot_trading_history as plot
    runner = algo_runner.AlgoRunner('SPY')
    # run the algorithm with the latest 200 minutes:
    df = runner.latest()
    print(df[['minute', 'close']].tail(5))
    plot.plot_trading_history(
        title=(
            f'SPY - ${df["close"].iloc[-1]} at: '
            f'{df["minute"].iloc[-1]}'),
        df=df)
    # start a full backtest with:
    # runner.start()

Check out the `backtest_with_runner.py script <https://github.com/AlgoTraders/stock-analysis-engine/blob/master/analysis_engine/scripts/backtest_with_runner.py>`__ for a command line example of using the `Algorithm Runner API <https://stock-analysis-engine.readthedocs.io/en/latest/algo_runner.html>`__ to run and plot from an `Algorithm backtest config file <https://github.com/AlgoTraders/stock-analysis-engine/blob/master/cfg/default_algo.json>`__.

Extract from Redis API
======================

Once fetched, you can extract datasets from the redis cache with:

.. code-block:: python

    import analysis_engine.extract as ae_extract
    print(ae_extract.extract('SPY'))

Extract Latest Minute Pricing for Stocks and Options
====================================================

.. code-block:: python

    import analysis_engine.extract as ae_extract
    print(ae_extract.extract(
        'SPY',
        datasets=['minute', 'tdcalls', 'tdputs']))

Extract Historical Data
-----------------------

Extract historical data with the ``date`` argument formatted ``YYYY-MM-DD``:

.. code-block:: python

    import analysis_engine.extract as ae_extract
    print(ae_extract.extract(
        'AAPL',
        datasets=['minute', 'daily', 'financials', 'earnings', 'dividends'],
        date='2019-02-15'))

Additional Extraction APIs
==========================

- `Extraction API Reference <https://stock-analysis-engine.readthedocs.io/en/latest/extract.html>`__
- `IEX Cloud Extraction API Reference <https://stock-analysis-engine.readthedocs.io/en/latest/iex_api.html#iex-extraction-api-reference>`__
- `Tradier Extraction API Reference <https://stock-analysis-engine.readthedocs.io/en/latest/tradier.html#tradier-extraction-api-reference>`__
- `Inspect Cached Datasets in Redis for Errors <https://stock-analysis-engine.readthedocs.io/en/latest/inspect_datasets.html#module-analysis_engine.scripts.inspect_datasets>`__

Backups
=======

Pricing data is automatically compressed in redis and there is an `example Kubernetes job for backing up all stored pricing data to AWS S3 <https://github.com/AlgoTraders/stock-analysis-engine/blob/master/k8/backups/backup-to-aws-job.yml>`__.

Running the Full Stack Locally for Backtesting and Live Trading Analysis
========================================================================

While not required for backtesting, running the full stack is required for running algorithms during a live trading session. Here is a video on how to deploy the full stack locally using docker compose and the commands from the video.

.. image:: https://asciinema.org/a/220487.png
    :target: https://asciinema.org/a/220487?autoplay=1
    :alt: Running the Full Stack Locally for Backtesting and Live Trading Analysis

#.  Start Workers, Backtester, Pricing Data Collection, Jupyter, Redis and Minio

    Now start the rest of the stack with the command below. This will pull the `~3.0 GB stock-analysis-engine docker image <https://hub.docker.com/r/jayjohnson/stock-analysis-engine>`__ and start the workers, backtester, dataset collection and `Jupyter image <https://hub.docker.com/r/jayjohnson/stock-analysis-jupyter>`__. It will start `Redis <https://hub.docker.com/_/redis>`__ and `Minio <https://hub.docker.com/r/minio/minio>`__ if they are not running already.

    ::

        ./compose/start.sh

    .. tip:: Mac OS X users just a note that `there is a known docker compose issue with network_mode: "host" <https://github.com/docker/for-mac/issues/1031>`__ so you may have issues trying to connect to your services.

#.  Check the Docker Containers

    ::

        docker ps -a

#.  View for dataset collection logs

    ::

        logs-dataset-collection.sh

#.  Wait for pricing engine logs to stop with ``ctrl+c``

    ::

        logs-workers.sh

#.  Verify Pricing Data is in Redis

    ::

        redis-cli keys "*"

#.  Optional - Automating `pricing data collection with the automation-dataset-collection.yml docker compose file <https://github.com/AlgoTraders/stock-analysis-engine/blob/master/compose/automation-dataset-collection.yml>`__:

    .. note:: Depending on how fast you want to run intraday algorithms, you can use this docker compose job or the `Kubernetes job <https://github.com/AlgoTraders/stock-analysis-engine/blob/master/k8/datasets/job.yml>`__ or the `Fetch from Only Tradier Kubernetes job <https://github.com/AlgoTraders/stock-analysis-engine/blob/master/k8/datasets/pull_tradier_per_minute.yml>`__ to collect the most recent pricing information

    ::

        ./compose/start.sh -c

Run a Custom Minute-by-Minute Intraday Algorithm Backtest and Plot the Trading History
======================================================================================

With pricing data in redis, you can start running backtests a few ways:

- `Comparing 3 Deep Neural Networks Trained to Predict a Stocks Closing Price in a Jupyter Notebook <https://github.com/AlgoTraders/stock-analysis-engine/blob/master/compose/docker/notebooks/Comparing-3-Deep-Neural-Networks-Trained-to-Predict-a-Stocks-Closing-Price-Using-The-Analysis-Engine.ipynb>`__
- `Build, run and tune within a Jupyter Notebook and plot the balance vs the stock's closing price while running <https://github.com/AlgoTraders/stock-analysis-engine/blob/master/compose/docker/notebooks/Run-a-Custom-Trading-Algorithm-Backtest-with-Minute-Timeseries-Pricing-Data.ipynb>`__
- `Analyze and replay algorithm trading histories stored in s3 with this Jupyter Notebook <https://github.com/AlgoTraders/stock-analysis-engine/blob/master/compose/docker/notebooks/Analyze%20Compressed%20Algorithm%20Trading%20Histories%20Stored%20in%20S3.ipynb>`__
- `Run with the command line backtest tool <https://github.com/AlgoTraders/stock-analysis-engine/blob/master/analysis_engine/scripts/run_backtest_and_plot_history.py>`__
- `Advanced - building a standalone algorithm as a class for running trading analysis <https://github.com/AlgoTraders/stock-analysis-engine/blob/master/analysis_engine/mocks/example_algo_minute.py>`__

Running an Algorithm with Live Intraday Pricing Data
====================================================

Here is a video showing how to run it:

.. image:: https://asciinema.org/a/220498.png
    :target: https://asciinema.org/a/220498?autoplay=1
    :alt: Running an Algorithm with Live Intraday Pricing Data

The `backtest command line tool <https://github.com/AlgoTraders/stock-analysis-engine/blob/master/analysis_engine/scripts/run_backtest_and_plot_history.py>`__ uses an `algorithm config dictionary <https://github.com/AlgoTraders/stock-analysis-engine/blob/master/tests/algo_configs/test_5_days_ahead.json>`__ to build multiple `Williams %R indicators <https://github.com/AlgoTraders/stock-analysis-engine/blob/master/analysis_engine/scripts/run_backtest_and_plot_history.py#L49>`__ into an algorithm with a **10,000.00 USD** starting balance. Once configured, the backtest iterates through each trading dataset and evaluates if it should buy or sell based off the pricing data. After it finishes, the tool will display a chart showing the algorithm's **balance** and the stock's **close price** per minute using matplotlib and seaborn.

::

    # this can take a few minutes to evaluate
    # as more data is collected
    # because each day has 390 rows to process
    bt -t SPY -f /tmp/history.json

.. note:: The algorithm's **trading history** dataset provides many additional columns to review for tuning indicators and custom buy/sell rules. To reduce the time spent waiting on an algorithm to finish processing, you can save the entire trading history to disk with the ``-f <save_to_file>`` argument.

View the Minute Algorithm's Trading History from a File
=======================================================

Once the **trading history** is saved to disk, you can open it back up and plot other columns within the dataset with:

.. image:: https://i.imgur.com/pH368gy.png

::

    # by default the plot shows
    # balance vs close per minute
    plot-history -f /tmp/history.json

Run a Custom Algorithm and Save the Trading History with just Today's Pricing Data
==================================================================================

Here's how to run an algorithm during a live trading session. This approach assumes another process or cron is ``fetch-ing`` the pricing data using the engine so the algorithm(s) have access to the latest pricing data:

::

    bt -t SPY -f /tmp/SPY-history-$(date +"%Y-%m-%d").json -j $(date +"%Y-%m-%d")

.. note:: Using ``-j <DATE>`` will make the algorithm **jump-to-this-date** before starting any trading. This is helpful for debugging indicators, algorithms, datasets issues, and buy/sell rules as well.

Run a Backtest using an External Algorithm Module and Config File
=================================================================

Run an algorithm backtest with a standalone algorithm class contained in a single python module file that can even be outside the repository using a config file on disk:

::

    ticker=SPY
    config=<CUSTOM_ALGO_CONFIG_DIR>/minute_algo.json
    algo_mod=<CUSTOM_ALGO_MODULE_DIR>/minute_algo.py
    bt -t ${ticker} -c ${algo_config} -g ${algo_mod}

Or the config can use ``"algo_path": "<PATH_TO_FILE>"`` to set the path to an external algorithm module file.

::

    bt -t ${ticker} -c ${algo_config}

.. note:: Using a standalone algorithm class must derive from the ``analysis_engine.algo.BaseAlgo`` class

Building Your Own Trading Algorithms
====================================

Beyond running backtests, the included engine supports running many algorithms and fetching data for both live trading or backtesting all at the same time. As you start to use this approach, you will be generating lots of algorithm pricing datasets, history datasets and coming soon performance datasets for AI training. Because algorithm's utilize the same dataset structure, you can share **ready-to-go** datasets with a team and publish them to S3 for kicking off backtests using lambda functions or just archival for disaster recovery.

.. note:: Backtests can use **ready-to-go** datasets out of S3, redis or a file

The next section looks at how to build an `algorithm-ready datasets from cached pricing data in redis <https://github.com/AlgoTraders/stock-analysis-engine#extract-algorithm-ready-datasets>`__.

Run a Local Backtest and Publish Algorithm Trading History to S3
================================================================

::

    ae -t SPY -p s3://algohistory/algo_training_SPY.json

Run distributed across the engine workers with ``-w``

::

    ae -w -t SPY -p s3://algohistory/algo_training_SPY.json

Run a Local Backtest using an Algorithm Config and Extract an Algorithm-Ready Dataset
=====================================================================================

Use this command to start a local backtest with the included `algorithm config <https://github.com/AlgoTraders/stock-analysis-engine/blob/master/tests/algo_configs/test_5_days_ahead.json>`__. This backtest will also generate a local algorithm-ready dataset saved to a file once it finishes.

#.  Define common values

    ::

        ticker=SPY
        algo_config=tests/algo_configs/test_5_days_ahead.json
        extract_loc=file:/tmp/algoready-SPY-latest.json
        history_loc=file:/tmp/history-SPY-latest.json
        load_loc=${extract_loc}

Run Algo with Extraction and History Publishing
-----------------------------------------------

::

    run-algo-history-to-file.sh -t ${ticker} -c ${algo_config} -e ${extract_loc} -p ${history_loc}

Profile Your Algorithm's Code Performance with vprof
====================================================

.. image:: https://i.imgur.com/1cwDUBC.png

The pip includes `vprof for profiling an algorithm's performance (cpu, memory, profiler and heat map - not money-related) <https://github.com/nvdv/vprof>`__ which was used to generate the cpu flame graph seen above.

Profile your algorithm's code performance with the following steps:

#.  Start vprof in remote mode in a first terminal

    .. note:: This command will start a webapp on port ``3434``

    ::

        vprof -r -p 3434

#.  Start Profiler in a second terminal

    .. note:: This command pushes data to the webapp in the other terminal listening on port ``3434``

    ::

        vprof -c cm ./analysis_engine/perf/profile_algo_runner.py

Run a Local Backtest using an Algorithm Config and an Algorithm-Ready Dataset
=============================================================================

After generating the local algorithm-ready dataset (which can take some time), use this command to run another backtest using the file on disk:

::

    dev_history_loc=file:/tmp/dev-history-${ticker}-latest.json
    run-algo-history-to-file.sh -t ${ticker} -c ${algo_config} -l ${load_loc} -p ${dev_history_loc}

View Buy and Sell Transactions
------------------------------

::

    run-algo-history-to-file.sh -t ${ticker} -c ${algo_config} -l ${load_loc} -p ${dev_history_loc} | grep "TRADE"

Plot Trading History Tools
==========================

Plot Timeseries Trading History with High + Low + Open + Close
--------------------------------------------------------------

::

    sa -t SPY -H ${dev_history_loc}

Run and Publish Trading Performance Report for a Custom Algorithm
=================================================================

This will run a backtest over the past 60 days in order and run the `standalone algorithm as a class example <https://github.com/AlgoTraders/stock-analysis-engine/blob/master/analysis_engine/mocks/example_algo_minute.py>`__. Once done it will publish the trading performance report to a file or minio (s3).

Write the Trading Performance Report to a Local File
----------------------------------------------------

::

    run-algo-report-to-file.sh -t SPY -b 60 -a /opt/sa/analysis_engine/mocks/example_algo_minute.py
    # run-algo-report-to-file.sh -t <TICKER> -b <NUM_DAYS_BACK> -a <CUSTOM_ALGO_MODULE>
    # run on specific date ranges with:
    # -s <start date YYYY-MM-DD> -n <end date YYYY-MM-DD>

Write the Trading Performance Report to Minio (s3)
--------------------------------------------------

::

    run-algo-report-to-s3.sh -t SPY -b 60 -a /opt/sa/analysis_engine/mocks/example_algo_minute.py

Run and Publish Trading History for a Custom Algorithm
======================================================

This will run a full backtest across the past 60 days in order and run the `example algorithm <https://github.com/AlgoTraders/stock-analysis-engine/blob/master/analysis_engine/mocks/example_algo_minute.py>`__. Once done it will publish the trading history to a file or minio (s3).

Write the Trading History to a Local File
-----------------------------------------

::

    run-algo-history-to-file.sh -t SPY -b 60 -a /opt/sa/analysis_engine/mocks/example_algo_minute.py

Write the Trading History to Minio (s3)
---------------------------------------

::

    run-algo-history-to-s3.sh -t SPY -b 60 -a /opt/sa/analysis_engine/mocks/example_algo_minute.py

Developing on AWS
=================

If you are comfortable with AWS S3 usage charges, then you can run just with a redis server to develop and tune algorithms. This works for teams and for archiving datasets for disaster recovery.

Environment Variables
---------------------

Export these based off your AWS IAM credentials and S3 endpoint.

::

    export AWS_ACCESS_KEY_ID="ACCESS"
    export AWS_SECRET_ACCESS_KEY="SECRET"
    export S3_ADDRESS=s3.us-east-1.amazonaws.com

Extract and Publish to AWS S3
=============================

::

    ./tools/backup-datasets-on-s3.sh -t TICKER -q YOUR_BUCKET -k ${S3_ADDRESS} -r localhost:6379

Publish to Custom AWS S3 Bucket and Key
=======================================

::

    extract_loc=s3://YOUR_BUCKET/TICKER-latest.json
    ./tools/backup-datasets-on-s3.sh -t TICKER -e ${extract_loc} -r localhost:6379

Backtest a Custom Algorithm with a Dataset on AWS S3
====================================================

::

    backtest_loc=s3://YOUR_BUCKET/TICKER-latest.json
    custom_algo_module=/opt/sa/analysis_engine/mocks/example_algo_minute.py
    sa -t TICKER -a ${S3_ADDRESS} -r localhost:6379 -b ${backtest_loc} -g ${custom_algo_module}

Fetching New Pricing Tradier Every Minute with Kubernetes
=========================================================

If you want to fetch and append new option pricing data from `Tradier <https://developer.tradier.com/getting_started>`__, you can use the included kubernetes job with a cron to pull new data every minute:

::

    kubectl -f apply /opt/sa/k8/datasets/pull_tradier_per_minute.yml

Run a Distributed 60-day Backtest on SPY and Publish the Trading Report, Trading History and Algorithm-Ready Dataset to S3
==========================================================================================================================

Publish backtests and live trading algorithms to the engine's workers for running many algorithms at the same time. Once done, the algorithm will publish results to s3, redis or a local file. By default, the included example below publishes all datasets into minio (s3) where they can be downloaded for offline backtests or restored back into redis.

.. note:: Running distributed algorithmic workloads requires redis, minio, and the engine running

::

    num_days_back=60
    ./tools/run-algo-with-publishing.sh -t SPY -b ${num_days_back} -w

Run a Local 60-day Backtest on SPY and Publish Trading Report, Trading History and Algorithm-Ready Dataset to S3
================================================================================================================

::

    num_days_back=60
    ./tools/run-algo-with-publishing.sh -t SPY -b ${num_days_back}

Or manually with:

::

    ticker=SPY
    num_days_back=60
    use_date=$(date +"%Y-%m-%d")
    ds_id=$(uuidgen | sed -e 's/-//g')
    ticker_dataset="${ticker}-${use_date}_${ds_id}.json"
    echo "creating ${ticker} dataset: ${ticker_dataset}"
    extract_loc="s3://algoready/${ticker_dataset}"
    history_loc="s3://algohistory/${ticker_dataset}"
    report_loc="s3://algoreport/${ticker_dataset}"
    backtest_loc="s3://algoready/${ticker_dataset}"  # same as the extract_loc
    processed_loc="s3://algoprocessed/${ticker_dataset}"  # archive it when done
    start_date=$(date --date="${num_days_back} day ago" +"%Y-%m-%d")
    echo ""
    echo "extracting algorithm-ready dataset: ${extract_loc}"
    echo "sa -t SPY -e ${extract_loc} -s ${start_date} -n ${use_date}"
    sa -t SPY -e ${extract_loc} -s ${start_date} -n ${use_date}
    echo ""
    echo "running algo with: ${backtest_loc}"
    echo "sa -t SPY -p ${history_loc} -o ${report_loc} -b ${backtest_loc} -e ${processed_loc} -s ${start_date} -n ${use_date}"
    sa -t SPY -p ${history_loc} -o ${report_loc} -b ${backtest_loc} -e ${processed_loc} -s ${start_date} -n ${use_date}

Jupyter on Kubernetes
=====================

This command runs Jupyter on an `AntiNex Kubernetes cluster <https://deploy-to-kubernetes.readthedocs.io/en/latest/>`__

::

    ./k8/jupyter/run.sh ceph dev

Kubernetes - Analyze and Tune Algorithms from a Trading History
===============================================================

With the Analysis Engine's Jupyter instance deployed you can `tune algorithms from a trading history using this notebook <https://aejupyter.example.com/notebooks/Analyze%20Compressed%20Algorithm%20Trading%20Histories%20Stored%20in%20S3.ipynb>`__.

Kubernetes Job - Export SPY Datasets and Publish to Minio
=========================================================

Manually run with an ``ssh-eng`` alias:

::

    function ssheng() {
        pod_name=$(kubectl get po | grep ae-engine | grep Running |tail -1 | awk '{print $1}')
        echo "logging into ${pod_name}"
        kubectl exec -it ${pod_name} bash
    }
    ssheng
    # once inside the container on kubernetes
    source /opt/venv/bin/activate
    sa -a minio-service:9000 -r redis-master:6379 -e s3://backups/SPY-$(date +"%Y-%m-%d") -t SPY

View Algorithm-Ready Datasets
-----------------------------

With the AWS cli configured you can view available algorithm-ready datasets in your minio (s3) bucket with the command:

::

    aws --endpoint-url http://localhost:9000 s3 ls s3://algoready

View Trading History Datasets
-----------------------------

With the AWS cli configured you can view available trading history datasets in your minio (s3) bucket with the command:

::

    aws --endpoint-url http://localhost:9000 s3 ls s3://algohistory

View Trading History Datasets
-----------------------------

With the AWS cli configured you can view available trading performance report datasets in your minio (s3) bucket with the command:

::

    aws --endpoint-url http://localhost:9000 s3 ls s3://algoreport

Advanced - Running Algorithm Backtests Offline
==============================================

With `extracted Algorithm-Ready datasets in minio (s3), redis or a file <https://github.com/AlgoTraders/stock-analysis-engine#extract-algorithm-ready-datasets>`__ you can develop and tune your own algorithms offline without having redis, minio, the analysis engine, or jupyter running locally.

Run a Offline Custom Algorithm Backtest with an Algorithm-Ready File
--------------------------------------------------------------------

::

    # extract with:
    sa -t SPY -e file:/tmp/SPY-latest.json
    sa -t SPY -b file:/tmp/SPY-latest.json -g /opt/sa/analysis_engine/mocks/example_algo_minute.py

Run the Intraday Minute-by-Minute Algorithm and Publish the Algorithm-Ready Dataset to S3
-----------------------------------------------------------------------------------------

Run the `included standalone algorithm <https://github.com/AlgoTraders/stock-analysis-engine/blob/master/analysis_engine/mocks/example_algo_minute.py>`__ with the latest pricing datasets use:

::

    sa -t SPY -g /opt/sa/analysis_engine/mocks/example_algo_minute.py -e s3://algoready/SPY-$(date +"%Y-%m-%d").json

And to debug an algorithm's historical trading performance add the ``-d`` debug flag:

::

    sa -d -t SPY -g /opt/sa/analysis_engine/mocks/example_algo_minute.py -e s3://algoready/SPY-$(date +"%Y-%m-%d").json

Extract Algorithm-Ready Datasets
================================

With pricing data cached in redis, you can extract algorithm-ready datasets and save them to a local file for offline historical backtesting analysis. This also serves as a local backup where all cached data for a single ticker is in a single local file.

Extract an Algorithm-Ready Dataset from Redis and Save it to a File
-------------------------------------------------------------------

::

    sa -t SPY -e ~/SPY-latest.json

Create a Daily Backup
---------------------

::

    sa -t SPY -e ~/SPY-$(date +"%Y-%m-%d").json

Validate the Daily Backup by Examining the Dataset File
-------------------------------------------------------

::

    sa -t SPY -l ~/SPY-$(date +"%Y-%m-%d").json

Validate the Daily Backup by Examining the Dataset File
-------------------------------------------------------

::

    sa -t SPY -l ~/SPY-$(date +"%Y-%m-%d").json

Restore Backup to Redis
-----------------------

Use this command to cache missing pricing datasets so algorithms have the correct data ready-to-go before making buy and sell predictions.

.. note:: By default, this command will not overwrite existing datasets in redis. It was built as a tool for merging redis pricing datasets after a VM restarted and pricing data was missing from the past few days (gaps in pricing data is bad for algorithms).

::

    sa -t SPY -L ~/SPY-$(date +"%Y-%m-%d").json

Fetch
-----

With redis and minio running (``./compose/start.sh``), you can fetch, cache, archive and return all of the newest datasets for tickers:

.. code-block:: python

    from analysis_engine.fetch import fetch
    d = fetch(ticker='SPY')
    for k in d['SPY']:
        print(f'dataset key: {k}\nvalue {d["SPY"][k]}\n')

Backfill Historical Minute Data from IEX Cloud
==============================================

.. note:: `IEX Cloud supports pulling from 30 days before today <https://iexcloud.io/docs/api/#historical-prices>`__

::

    fetch -t TICKER -F PAST_DATE -g iex_min
    # example:
    # fetch -t SPY -F 2019-02-07 -g iex_min

Please refer to the `Stock Analysis Intro Extracting Datasets Jupyter Notebook <https://github.com/AlgoTraders/stock-analysis-engine/blob/master/compose/docker/notebooks/Stock-Analysis-Intro-Extracting-Datasets.ipynb>`__ for the latest usage examples.

.. list-table::
   :header-rows: 1

   * - `Build <https://travis-ci.org/AlgoTraders/stock-analysis-engine>`__
   * - .. image:: https://api.travis-ci.org/AlgoTraders/stock-analysis-engine.svg
           :alt: Travis Tests
           :target: https://travis-ci.org/AlgoTraders/stock-analysis-engine

Table of Contents
=================

.. toctree::
   :maxdepth: 2
   :caption: Contents:

   README
   algo_runner
   get_pricing_on_date
   inspect_datasets
   scripts
   deploy_on_kubernetes_using_helm
   example_algo_minute
   plot_trading_history
   task_run_algo
   run_custom_algo
   run_algo
   perf_testing
   tradier
   example_algos
   indicators_examples
   indicators_load_from_module
   indicators_base
   indicators_build_node
   talib
   build_algo_request
   build_sell_order
   build_buy_order
   build_trade_history_entry
   build_entry_call_spread_details
   build_exit_call_spread_details
   build_entry_put_spread_details
   build_exit_put_spread_details
   build_option_spread_details
   build_dnn_from_trading_history
   algorithm_api
   show_dataset
   load_dataset
   restore_dataset
   publish
   extract
   fetch
   compress_data
   build_publish_request
   api_reference
   iex_api
   yahoo_api
   finviz_api
   scrub_utils
   options_utils
   holidays
   charts
   tasks
   mock_api
   extract_utils
   slack_utils
   utils

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
