Use Helm to Run the Analysis Engine on Kubernetes
=================================================

.. image:: https://asciinema.org/a/230665.png
    :target: https://asciinema.org/a/230665?autoplay=1
    :alt: Use Helm to Run the Analysis Engine on Kubernetes

This guide outlines how to use helm to deploy and manage the Analysis Engine (AE) on kubernetes (tested on ``1.13.3``).

It requires the following steps are done before getting started:

#.  Access to a running Kubernetes cluster
#.  `Helm is installed <https://helm.sh/docs/using_helm/>`__
#.  A valid account for `IEX Cloud <https://iexcloud.io/cloud-login#/register/>`__
#.  A valid account for `Tradier <https://developer.tradier.com/user/sign_up>`__
#.  Optional - `Install Ceph Cluster for Persistent Storage Support <https://deploy-to-kubernetes.readthedocs.io/en/latest/ceph.html>`__
#.  Optional - `Install the Stock Analysis Engine for Local Development Outside of Kubernetes <https://stock-analysis-engine.readthedocs.io/en/latest/README.html#getting-started>`__

Getting Started
===============

AE builds multiple helm charts that are hosted on a local helm repository, and everything runs within the ``ae`` kubernetes namespace.

Please change to the ``./helm`` directory:

::

    cd helm

Build Charts
------------

This will build all the AE charts, download `stable/redis <https://github.com/helm/charts/tree/master/stable/redis>`__ and `stable/minio <https://github.com/helm/charts/tree/master/stable/minio>`__, and ensure the local helm server is running:

::

    ./build.sh

Configuration
=============

Each AE chart supports attributes for connecting to a:

#.  `Private Docker Registry <https://docs.docker.com/registry/deploying/>`__
#.  `Redis <https://github.com/helm/charts/tree/master/stable/redis>`__
#.  `S3 (Minio or AWS) <https://github.com/helm/charts/tree/master/stable/minio>`__
#.  `IEX Cloud <https://iexcloud.io/docs/api/#stocks>`__
#.  `Tradier <https://developer.tradier.com/documentation>`__
#.  `Jupyter <https://jupyter.org/>`__
#.  `Nginx Ingress <https://github.com/nginxinc/kubernetes-ingress/>`__

Depending on your environment, these services may require you to edit the associated helm chart's `values.yaml <https://github.com/helm/helm/blob/master/docs/chart_template_guide/values_files.md>`__ file(s) before starting everything with the `start.sh <https://github.com/AlgoTraders/stock-analysis-engine/tree/master/helm/start.sh>`__ script to deploy AE.

Below are some of the common integration questions on how to configure each one (hopefully) for your environment:

Configure Redis
---------------

The ``start.sh`` script installs the `stable/redis <//github.com/helm/charts/tree/master/stable/redis>`__ chart with the included `./redis/values.yaml <https://github.com/AlgoTraders/stock-analysis-engine/tree/master/helm/redis/values.yaml>`__ for configuring as needed before the start script boots up the included `Bitnami Redis cluster <https://bitnami.com/stack/redis/helm>`__

Configure Minio
---------------

The ``start.sh`` script installs the `stable/minio <https://github.com/helm/charts/tree/master/stable/minio>`__ chart with the included `./minio/values.yaml <https://github.com/AlgoTraders/stock-analysis-engine/tree/master/helm/minio/values.yaml>`__ for configuring as needed before the start script boots up the included `Minio <https://docs.minio.io/docs/deploy-minio-on-kubernetes.html>`__

Configure AE Stack
------------------

Each of the AE charts can be configured prior to running the stack's core AE chart found in:

`./ae/values.yaml <https://github.com/AlgoTraders/stock-analysis-engine/tree/master/helm/ae/values.yaml>`__

Configure the AE Backup to AWS S3 Job
-------------------------------------

Please set your AWS credentials (which will be installed as kubernetes secrets) in the file:

`./ae-backup/values.yaml <https://github.com/AlgoTraders/stock-analysis-engine/tree/master/helm/ae-backup/values.yaml>`__

Configure Data Collection Jobs
------------------------------

Data collection is broken up into three categories of jobs: intraday, daily and weekly data to collect. Intraday data collection is built to be fast and pull data that changes often vs weekly data that is mostly static and expensive for ``IEX Cloud`` users. These chart jobs are intended to be used with cron jobs that fire work into the AE workers which compress + cache the pricing data for algorithms and backtesting.

#.  Set your ``IEX Cloud`` account up in each chart:
    
    #.  `ae-intraday <https://github.com/AlgoTraders/stock-analysis-engine/blob/f8be749f5cdbc27ee83c66d2d7d4cad39ca949b0/helm/ae-intraday/values.yaml#L79-L88>`__

    #.  `ae-daily <https://github.com/AlgoTraders/stock-analysis-engine/blob/f8be749f5cdbc27ee83c66d2d7d4cad39ca949b0/helm/ae-daily/values.yaml#L79-L88>`__

    #.  `ae-weekly <https://github.com/AlgoTraders/stock-analysis-engine/blob/f8be749f5cdbc27ee83c66d2d7d4cad39ca949b0/helm/ae-weekly/values.yaml#L79-L88>`__

    **Supported IEX Cloud Attributes**

    ::
    
        # IEX Cloud
        # https://iexcloud.io/docs/api/
        iex:
          addToSecrets: true
          secretName: ae.k8.iex.<intraday|daily|weekly>
          # Publishable Token:
          token: ""
          # Secret Token:
          secretToken: ""
          apiVersion: beta

#.  Set your ``Tradier`` account up in each chart:
    
    #.  `ae-intraday <https://github.com/AlgoTraders/stock-analysis-engine/blob/f8be749f5cdbc27ee83c66d2d7d4cad39ca949b0/helm/ae-intraday/values.yaml#L90-L98>`__

    #.  `ae-daily <https://github.com/AlgoTraders/stock-analysis-engine/blob/f8be749f5cdbc27ee83c66d2d7d4cad39ca949b0/helm/ae-daily/values.yaml#L90-L98>`__

    #.  `ae-weekly <https://github.com/AlgoTraders/stock-analysis-engine/blob/f8be749f5cdbc27ee83c66d2d7d4cad39ca949b0/helm/ae-weekly/values.yaml#L90-L98>`__

    **Supported Tradier Attributes**

    ::

        # Tradier
        # https://developer.tradier.com/documentation
        tradier:
          addToSecrets: true
          secretName: ae.k8.tradier.<intraday|daily|weekly>
          token: ""
          apiFQDN: api.tradier.com
          dataFQDN: sandbox.tradier.com
          streamFQDN: sandbox.tradier.com

#.  `ae-intraday <https://github.com/AlgoTraders/stock-analysis-engine/tree/master/helm/ae-intraday/values.yaml>`__

    - Set the `intraday.tickers <https://github.com/AlgoTraders/stock-analysis-engine/blob/f8be749f5cdbc27ee83c66d2d7d4cad39ca949b0/helm/ae-intraday/values.yaml#L125>`__ to a comma-delimited list of tickers to pull per minute.

#.  `ae-daily <https://github.com/AlgoTraders/stock-analysis-engine/tree/master/helm/ae-daily/values.yaml>`__

    - Set the `daily.tickers <https://github.com/AlgoTraders/stock-analysis-engine/blob/f8be749f5cdbc27ee83c66d2d7d4cad39ca949b0/helm/ae-daily/values.yaml#L125>`__ to a comma-delimited list of tickers to pull at the end of each trading day.

#.  `ae-weekly <https://github.com/AlgoTraders/stock-analysis-engine/tree/master/helm/ae-weekly/values.yaml>`__

    - Set the `weekly.tickers <https://github.com/AlgoTraders/stock-analysis-engine/blob/f8be749f5cdbc27ee83c66d2d7d4cad39ca949b0/helm/ae-weekly/values.yaml#L125>`__ to a comma-delimited list of tickers to pull every week. This is used for pulling "quota-expensive" data that does not change often like ``IEX Financials or Earnings`` data every week.

Set Jupyter Login Credentials
-----------------------------

Please set your Jupyter login `password <https://github.com/AlgoTraders/stock-analysis-engine/blob/f8be749f5cdbc27ee83c66d2d7d4cad39ca949b0/helm/ae-jupyter/values.yaml#L99>`__ that works with a browser:

::

    jupyter:
      password: admin

View Jupyter
------------

By default, Jupyter is hosted with `nginx-ingress with TLS encryption <https://github.com/nginxinc/kubernetes-ingress>`__ at:

https://aejupyter.example.com

Default login password is:

- password: ``admin``

View Minio
----------

By default, Minio is hosted with `nginx-ingress with TLS encryption <https://github.com/nginxinc/kubernetes-ingress>`__ at:

https://aeminio.example.com

Default `login credentials <https://github.com/AlgoTraders/stock-analysis-engine/blob/f8be749f5cdbc27ee83c66d2d7d4cad39ca949b0/helm/ae/values.yaml#L50-L51>`__ are:

- Access Key: ``trexaccesskey``
- Secret Key: ``trex123321``

Optional - Set Default Storage Class
------------------------------------

The AE pods are using a `Distributed Ceph Cluster <https://deploy-to-kubernetes.readthedocs.io/en/latest/ceph.html>`__ for persistenting data outside kubernetes with ``~300 GB`` of disk space.

To set your kubernetes cluster StorageClass to use the `ceph-rbd <https://github.com/AlgoTraders/stock-analysis-engine/blob/f8be749f5cdbc27ee83c66d2d7d4cad39ca949b0/helm/set-storage-class.sh#L13-L16>`__ use the script:

`./set-storage-class.sh ceph-rbd <https://github.com/AlgoTraders/stock-analysis-engine/blob/master/helm/set-storage-class.sh>`__

Optional - Set the Charts to Pull from a Private Docker Registry
----------------------------------------------------------------

By default the AE charts use the `Stock Analysis Engine container <https://hub.docker.com/r/jayjohnson/stock-analysis-engine>`__, and here is how to set up each AE component chart to use a private docker image in a private docker registry (for building your own algos in-house).

Each of the AE charts `values.yaml <https://github.com/AlgoTraders/stock-analysis-engine/blob/f8be749f5cdbc27ee83c66d2d7d4cad39ca949b0/helm/ae/values.yaml#L32-L36>`__ files contain **two** required sections for deploying from a private docker registry.

#.  Set the Private Docker Registry Authentication values in each chart

    Please set the registry address, secret name and docker config json for authentication using this format.

    - `ae <https://github.com/AlgoTraders/stock-analysis-engine/blob/f8be749f5cdbc27ee83c66d2d7d4cad39ca949b0/helm/ae/values.yaml#L32-L36>`__
    - `ae-backup <https://github.com/AlgoTraders/stock-analysis-engine/blob/f8be749f5cdbc27ee83c66d2d7d4cad39ca949b0/helm/ae-backup/values.yaml#L32-L36>`__
    - `ae-intraday <https://github.com/AlgoTraders/stock-analysis-engine/blob/f8be749f5cdbc27ee83c66d2d7d4cad39ca949b0/helm/ae-intraday/values.yaml#L32-L36>`__
    - `ae-daily <https://github.com/AlgoTraders/stock-analysis-engine/blob/f8be749f5cdbc27ee83c66d2d7d4cad39ca949b0/helm/ae-daily/values.yaml#L32-L36>`__
    - `ae-weekly <https://github.com/AlgoTraders/stock-analysis-engine/blob/f8be749f5cdbc27ee83c66d2d7d4cad39ca949b0/helm/ae-weekly/values.yaml#L32-L36>`__
    - `ae-jupyter <https://github.com/AlgoTraders/stock-analysis-engine/blob/f8be749f5cdbc27ee83c66d2d7d4cad39ca949b0/helm/ae-jupyter/values.yaml#L32-L36>`__

    .. note:: The ``imagePullSecrets`` attribute uses a naming convention format: ``<base key>.<component name>``. The base is ``ae.docker.creds.`` and the approach allows different docker images for each component (for testing) like intraday data collection vs running a backup job or even hosting jupyter.

    **Supported Private Docker Registry Authentication Attributes**

    ::

        registry:
          addToSecrets: true
          address: <FQDN to docker registry>:<PORT registry uses a default port 5000>
          imagePullSecrets: ae.docker.creds.<core|backtester|backup|intraday|daily|weekly|jupyter>
          dockerConfigJSON: '{"auths":{"<FQDN>:<PORT>":{"Username":"username","Password":"password","Email":""}}}'

#.  Set the AE Component's docker image name, tag, pullPolicy and private flag

    Please set the registry address, secret name and docker config json for authentication using this format.

    - `ae backtester <https://github.com/AlgoTraders/stock-analysis-engine/blob/f8be749f5cdbc27ee83c66d2d7d4cad39ca949b0/helm/ae/values.yaml#L134-L138>`__
    - `ae engine <https://github.com/AlgoTraders/stock-analysis-engine/blob/f8be749f5cdbc27ee83c66d2d7d4cad39ca949b0/helm/ae/values.yaml#L164-L168>`__
    - `ae-backup <https://github.com/AlgoTraders/stock-analysis-engine/blob/f8be749f5cdbc27ee83c66d2d7d4cad39ca949b0/helm/ae-backup/values.yaml#L101-L105>`__
    - `ae-intraday <https://github.com/AlgoTraders/stock-analysis-engine/blob/f8be749f5cdbc27ee83c66d2d7d4cad39ca949b0/helm/ae-intraday/values.yaml#L128-L132>`__
    - `ae-daily <https://github.com/AlgoTraders/stock-analysis-engine/blob/f8be749f5cdbc27ee83c66d2d7d4cad39ca949b0/helm/ae-daily/values.yaml#L128-L132>`__
    - `ae-weekly <https://github.com/AlgoTraders/stock-analysis-engine/blob/f8be749f5cdbc27ee83c66d2d7d4cad39ca949b0/helm/ae-weekly/values.yaml#L32-L36>`__
    - `ae-jupyter <https://github.com/AlgoTraders/stock-analysis-engine/blob/f8be749f5cdbc27ee83c66d2d7d4cad39ca949b0/helm/ae-jupyter/values.yaml#L100-L104>`__

    **Supported Private Docker Image Attributes per AE Component**

    ::

        image:
          private: true
          name: YOUR_IMAGE_NAME_HERE
          tag: latest
          pullPolicy: Always

Start Stack
===========

This command can take a few minutes to download and start all the components:

::

    ./start.sh

Manually Starting Components With Helm
======================================

If you do not want to use ``start.sh`` you can start the charts with helm using:

Start the AE Stack
------------------

::

    helm install \
        --name=ae \
        ./ae \
        --namespace=ae \
        -f ./ae/values.yaml 

Start Redis
-----------

::

    helm install \
        --name=ae-redis \
        stable/redis \
        --namespace=ae \
        -f ./redis/values.yaml

Start Minio
-----------

::

    helm install \
        --name=ae-minio \
        stable/minio \
        --namespace=ae \
        -f ./minio/values.yaml

Start Jupyter
-------------

::

    helm install \
        --name=ae-jupyter \
        ./ae-jupyter \
        --namespace=ae \
        -f ./ae-jupyter/values.yaml

Start Backup Job
----------------

::

    helm install \
        --name=ae-backup \
        ./ae-backup \
        --namespace=ae \
        -f ./ae-backup/values.yaml

Start Intraday Data Collection Job
----------------------------------

::

    helm install \
        --name=ae-intraday \
        ./ae-intraday \
        --namespace=ae \
        -f ./ae-intraday/values.yaml

Start Daily Data Collection Job
-------------------------------

::

    helm install \
        --name=ae-daily \
        ./ae-daily \
        --namespace=ae \
        -f ./ae-daily/values.yaml

Start Weekly Data Collection Job
--------------------------------

::

    helm install \
        --name=ae-weekly \
        ./ae-weekly \
        --namespace=ae \
        -f ./ae-weekly/values.yaml

Verify Pods are Running
=======================

::

    ./show-pods.sh 
    ------------------------------------ 
    getting pods in ae:  
    kubectl get pods -n ae 
    NAME                              READY   STATUS    RESTARTS   AGE
    ae-minio-55d56cf646-87znm         1/1     Running   0          3h30m
    ae-redis-master-0                 1/1     Running   0          3h30m
    ae-redis-slave-68fd99b688-sn875   1/1     Running   0          3h30m
    backtester-5c9687c645-n6mmr       1/1     Running   0          4m22s
    engine-6bc677fc8f-8c65v           1/1     Running   0          4m22s
    engine-6bc677fc8f-mdmcw           1/1     Running   0          4m22s
    jupyter-64cf988d59-7s7hs          1/1     Running   0          4m21s

Run Intraday Pricing Data Collection
====================================

Once your ``ae-intraday/values.yaml`` is ready, you can automate intraday data collection by using the helper script to start the helm release for ``ae-intraday``:

::

    ./run-intraday-job.sh <PATH_TO_VALUES_YAML>

And for a cron job, include the ``-r`` argument to ensure the job is recreated.

::

    ./run-intraday-job.sh -r <PATH_TO_VALUES_YAML>

View Collected Pricing Data in Redis
====================================

After data collection, you can view compressed data for a ticker within the redis cluster with:

::

    ./view-ticker-data-in-redis.sh TICKER

Run Daily Pricing Data Collection
=================================

Once your ``ae-daily/values.yaml`` is ready, you can automate daily data collection by using the helper script to start the helm release for ``ae-daily``:

::

    ./run-daily-job.sh <PATH_TO_VALUES_YAML>

And for a cron job, include the ``-r`` argument to ensure the job is recreated.

::

    ./run-daily-job.sh -r <PATH_TO_VALUES_YAML>

Run Weekly Pricing Data Collection
==================================

Once your ``ae-weekly/values.yaml`` is ready, you can automate weekly data collection by using the helper script to start the helm release for ``ae-weekly``:

::

    ./run-weekly-job.sh <PATH_TO_VALUES_YAML>

And for a cron job, include the ``-r`` argument to ensure the job is recreated.

::

    ./run-weekly-job.sh -r <PATH_TO_VALUES_YAML>

Run Backup Collected Pricing Data to AWS
========================================

Once your ``ae-backup/values.yaml`` is ready, you can automate backing up your collected + compressed pricing data from within the redis cluster and publish it to AWS S3 with the helper script:

.. warning:: Please remember AWS S3 has usage costs. Please `set only the tickers you need to backup before running the ae-backup job <https://github.com/AlgoTraders/stock-analysis-engine/blob/f8be749f5cdbc27ee83c66d2d7d4cad39ca949b0/helm/ae-backup/values.yaml#L98>`__.

::

    ./run-backup-job.sh <PATH_TO_VALUES_YAML>

And for a cron job, include the ``-r`` argument to ensure the job is recreated.

::

    ./run-backup-job.sh -r <PATH_TO_VALUES_YAML>

Cron Automation with Helm
=========================

Add the lines below to your cron with ``crontab -e`` for automating pricing data collection. All cron jobs using ``run-job.sh`` log to: ``/tmp/cron-ae.log``.

.. note:: This will pull data on holidays or closed trading days, but PR's welcomed!

Minute
------

Pull pricing data every minute ``M-F`` between 9 AM and 5 PM (assuming system time is ``EST``)

::

    # intraday job:
    # min hour day  month dayofweek job script path              job    KUBECONFIG
    *     9-17 *    *     1,2,3,4,5 /opt/sa/helm/cron/run-job.sh intra  /opt/k8/config

Daily
-----

Pull only on Friday at 6:01 PM (assuming system time is ``EST``)

::

    # daily job:
    # min hour day  month dayofweek job script path              job   KUBECONFIG
    1     18   *    *     1,2,3,4,5 /opt/sa/helm/cron/run-job.sh daily /opt/k8/config

Weekly
------

Pull only on Friday at 7:01 PM (assuming system time is ``EST``)

::

    # weekly job:
    # min hour day  month dayofweek job script path              job    KUBECONFIG
    1     19   *    *     5         /opt/sa/helm/cron/run-job.sh weekly /opt/k8/config

Backup
------

Run Friday at 8:01 PM (assuming system time is ``EST``)

::

    # backup job:
    # min hour day  month dayofweek job script path              job    KUBECONFIG
    1     20   *    *     1,2,3,4,5 /opt/sa/helm/cron/run-job.sh backup /opt/k8/config

Restore on Reboot
-----------------

Restore Latest Backup from S3 to Redis on a server reboot.

::

    # restore job:
    # on a server reboot (assuming your k8 cluster is running on just 1 host)
    @reboot /opt/sa/helm/cron/run-job.sh restore /opt/k8/config

Debugging Helm Deployed Components
==================================

Cron Jobs
---------

The ``engine`` pods handle pulling pricing data for the cron jobs. Please review ``./logs-engine.sh`` for any authentication errors for missing ``IEX Cloud Token`` and ``Tradier Token`` messages like:

**Missing IEX Token log**

::

    2019-03-01 06:03:58,836 - analysis_engine.work_tasks.get_new_pricing_data - WARNING - ticker=SPY - please set a valid IEX Cloud Account token (https://iexcloud.io/cloud-login/#/register) to fetch data from IEX Cloud. It must be set as an environment variable like: export IEX_TOKEN=<token>

**Missing Tradier Token log**

::

    2019-03-01 06:03:59,721 - analysis_engine.td.fetch_api - CRITICAL - Please check the TD_TOKEN is correct received 401 during fetch for: puts

If there is an ``IEX Cloud`` or ``Tradier`` authentication issue, then please check out the `Configure Data Collection Jobs section <https://stock-analysis-engine.readthedocs.io/en/latest/deploy_on_kubernetes_using_helm.html#configure-data-collection-jobs>`__ and then rerun the job with the updated ``values.yaml`` file.

Engine
------

Describe:

::
    
    ./describe-engine.sh

View Logs:

::

    ./logs-engine.sh

Intraday Data Collection
------------------------
    
Describe:

::

    ./describe-intraday.sh

View Logs:

::

    ./logs-job-intraday.sh
    
Daily Data Collection
---------------------
    
Describe:

::

    ./describe-daily.sh

View Logs:

::

    ./logs-job-daily.sh
    
Weekly Data Collection
----------------------
    
Describe:

::

    ./describe-weekly.sh

View Logs:

::

    ./logs-job-weekly.sh
    
Jupyter
-------

Describe Pod:

::

    ./describe-jupyter.sh
    
View Logs:

::

    ./logs-jupyter.sh

View Service:

::

    ./describe-service-jupyter.sh

Backtester
----------

Jupyter uses the backtester pod to peform asynchronous processing like running an algo backtest. To debug this run:

Describe:

::

    ./describe-backtester.sh
    
View Logs:

::

    ./logs-backtester.sh

Minio
-----

Describe:

::

    ./describe-minio.sh

Describe Service:

::

    ./describe-service-minio.sh

Describe Ingress:

::

    ./describe-ingress-minio.sh

Redis
-----

Describe:

::
    
    ./describe-redis.sh

Stop
====

To stop AE run:

::

    ./stop.sh

Full Delete
-----------

And if you really, really want to permanently delete ``ae-minio`` and ``ae-redis`` run:

.. warning:: Running this can delete cached pricing data. Please be careful.

::

    ./stop.sh -f 
