Use Helm to Run the Analysis Engine on Kubernetes
=================================================

.. image:: https://asciinema.org/a/230411.png
    :target: https://asciinema.org/a/230411?autoplay=1
    :alt: Use Helm to Run the Analysis Engine on Kubernetes

To run the Analysis Engine (AE) on kubernetes using helm please ensure you have:

#.  Access to a running Kubernetes cluster
#.  `Helm is installed <https://helm.sh/docs/using_helm/>`__
#.  A valid account for `IEX Cloud <https://iexcloud.io/cloud-login#/register/>`__
#.  A valid account for `Tradier <https://developer.tradier.com/user/sign_up>`__
#.  Optional - `Install Ceph Cluster for Persistent Storage Support <https://deploy-to-kubernetes.readthedocs.io/en/latest/ceph.html>`__

Getting Started
===============

AE builds multiple helm charts that are hosted on a local helm repository, and everything runs within the ``ae`` kubernetes namespace.

Please change to the ``./helm`` directory:

::

    cd helm

Build Charts
------------

This will build all the AE charts, download ``stable/redis`` and ``stable/minio``, and ensure the local helm server is running:

::

    ./build.sh

Configuration
=============

Each AE chart contains authentication attributes for connecting components to:

#.  Private Docker Registry
#.  Redis
#.  S3 (Minio or AWS)
#.  IEX Cloud
#.  Tradier
#.  Jupyter
#.  Nginx Ingress

Depending on your environment these services may require you to edit the helm chart ``values.yaml`` files before using the ``start.sh`` script to deploy AE.

Below are some of the common integration questions and how to set them up (hopefully) for your environment:

Configure Redis
---------------

By default the ``start.sh`` script uses the ``stable/redis`` chart with the included ``./redis/values.yaml`` for configuring as needed before the start script boots up the included `Bitnami Redis cluster <https://bitnami.com/stack/redis/helm>`__

Configure Minio
---------------

By default the ``start.sh`` script uses the ``stable/redis`` chart with the included ``./redis/values.yaml`` for configuring as needed before the start script boots up the included `Bitnami Redis cluster <https://bitnami.com/stack/redis/helm>`__

Configure AE Stack
------------------

Each of the AE charts can be configured prior to running the stack's core chart found in:

``./ae/values.yaml``

Configure the AE Backup to AWS S3 Job
-------------------------------------

Please set your AWS credentials (which will be installed as kubernetes secrets) in the file:

``./ae-backup/values.yaml``

Configure Data Collection Jobs
------------------------------

Data collection is broken up into three categories of jobs: intraday, daily and weekly data to collect. Intraday data collection is built to be fast and pull data that changes often vs weekly data that is mostly static and expensive for ``IEX Cloud`` users. These chart jobs are intended to be used with cron jobs that fire work into the AE workers which compress + cache the pricing data for algorithms and backtesting.

#.  Set your ``IEX Cloud`` account up in each chart:
    
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

#.  ``ae-intraday``

    - Set the ``intraday.tickers`` to a comma-delimited list of tickers to pull per minute.

#.  ``ae-daily``

    Set the ``daily.tickers`` to a comma-delimited list of tickers to pull at the end of each trading day.

#.  ``ae-weekly``

    Set the ``weekly.tickers`` to a comma-delimited list of tickers to pull every week. This is used for pulling "quota-expensive" data that does not change often like ``IEX Financials or Earnings`` data every week.

Set Jupyter Login Credentials
-----------------------------

Please set your Jupyter login username and password for logging in with a browser:

::

    jupyter:
      username: trex
      password: admin

View Jupyter
------------

By default, Jupyter is hosted with `nginx-ingress with TLS encryption <https://github.com/nginxinc/kubernetes-ingress>`__ at:

https://aejupyter.example.com

Default login credentials are:

- username: ``trex``
- password: ``admin``

View Minio
----------

By default, Minio is hosted with `nginx-ingress with TLS encryption <https://github.com/nginxinc/kubernetes-ingress>`__ at:

https://aeminio.example.com

Default login credentials are:

- Access Key: ``trexaccesskey``
- Secret Key: ``trex123321``

Optional - Set Default Storage Class
------------------------------------

The AE pods are using a `Distributed Ceph Cluster <https://deploy-to-kubernetes.readthedocs.io/en/latest/ceph.html>`__ for persistenting data outside kubernetes with ``~300 GB`` of disk space.

To set your kubernetes cluster StorageClass to use the ``ceph-rbd`` use the script:

``./set-storage-class.sh ceph-rbd``

Optional - Set the Charts to Pull from a Private Docker Registry
----------------------------------------------------------------

By default the AE charts use the `Stock Analysis Engine container <https://hub.docker.com/r/jayjohnson/stock-analysis-engine>`__, and here is how to set up each AE component chart to use a private docker image in a private docker registry (for building your own algos in-house).

Each of the AE charts ``values.yaml`` files contain a section for using a private docker registry.

Please set the registry address, secret name and docker config json for authentication using this format:

.. note:: ``imagePullSecrets`` is included in each the AE chart with a naming convention. The convention is the base ``ae.docker.creds.`` secret name has the AE component name appended to it. This allows differnt docker images to be used (and for testing) intraday data collection vs running a backup job or say hosting jupyter. The ``<core|backup|intraday|daily|weekly|jupyter>`` below is a placeholder indicating that the component name must be set to the one you are editing like: ``ae.docker.creds.core`` means the engine will use this secret.

::

    registry:
      addToSecrets: true
      address: <FQDN to docker registry>:<PORT registry uses a default port 5000>
      imagePullSecrets: ae.docker.creds.<core|backtester|backup|intraday|daily|weekly|jupyter>
      dockerConfigJSON: '{"auths":{"<FQDN>:<PORT>":{"Username":"username","Password":"password","Email":""}}}'

Then in the chart's AE component section at the bottom of the values.yaml file set the following attributes for the using your own docker image name, tag and pullPolicy:

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

::

    ./run-backup-job.sh <PATH_TO_VALUES_YAML>

And for a cron job, include the ``-r`` argument to ensure the job is recreated.

::

    ./run-backup-job.sh -r <PATH_TO_VALUES_YAML>

Debugging
=========

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
