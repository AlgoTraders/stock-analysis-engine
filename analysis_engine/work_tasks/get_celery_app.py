"""
Celery Get Application Helper
=============================
"""

import os
import celery
from spylunking.log.setup_logging import build_colorized_logger


log = build_colorized_logger(
    name=__name__)


def get_celery_app(
        name=os.getenv(
            'APP_NAME',
            'worker'),
        auth_url=os.getenv(
            'WORKER_BROKER_URL',
            'redis://localhost:6379/13'),
        backend_url=os.getenv(
            'WORKER_BACKEND_URL',
            'redis://localhost:6379/14'),
        include_tasks=[],
        ssl_options=None,
        transport_options=None,
        path_to_config_module=os.getenv(
            'WORKER_CELERY_CONFIG_MODULE',
            'analysis_engine.work_tasks.celery_config'),
        worker_log_format=os.getenv(
            'WORKER_LOG_FORMAT',
            '%(asctime)s: %(levelname)s %(message)s'),
        **kwargs):
    """get_celery_app

    Build a Celery app with support for environment variables
    to set endpoints locations.

    - export WORKER_BROKER_URL=redis://localhost:6379/13
    - export WORKER_BACKEND_URL=redis://localhost:6379/14
    - export WORKER_CELERY_CONFIG_MODULE=analysis_engine.work_tasks.cel
      ery_config

    .. note:: Jupyter notebooks need to use the
        ``WORKER_CELERY_CONFIG_MODULE=analysis_engine.work_tasks.celery
        service_config`` value which uses resolvable hostnames with
        docker compose:

        - export WORKER_BROKER_URL=redis://redis:6379/13
        - export WORKER_BACKEND_URL=redis://redis:6379/14

    :param name: name for this app
    :param auth_url: Celery broker address
        (default is ``redis://localhost:6379/13``
        or ``analysis_engine.consts.WORKER_BROKER_URL``
        environment variable)
        this is required for distributing algorithms
    :param backend_url: Celery backend address
        (default is ``redis://localhost:6379/14``
        or ``analysis_engine.consts.WORKER_BACKEND_URL``
        environment variable)
        this is required for distributing algorithms
    :param include_tasks: list of modules containing tasks to add
    :param ssl_options: security options dictionary
        (default is ``analysis_engine.consts.SSL_OPTIONS``)
    :param trasport_options: transport options dictionary
        (default is ``analysis_engine.consts.TRANSPORT_OPTIONS``)
    :param path_to_config_module: config module for advanced
        Celery worker connectivity requirements
        (default is ``analysis_engine.work_tasks.celery_config``
        or ``analysis_engine.consts.WORKER_CELERY_CONFIG_MODULE``)
    :param worker_log_format: format for logs
    """

    if len(include_tasks) == 0:
        log.error(
            'creating celery app={} MISSING tasks={}'.format(
                name,
                include_tasks))
    else:
        log.info(
            'creating celery app={} tasks={}'.format(
                name,
                include_tasks))

    # get the Celery application
    app = celery.Celery(
        name,
        broker_url=auth_url,
        result_backend=backend_url,
        include=include_tasks)

    app.config_from_object(
        path_to_config_module,
        namespace='CELERY')

    app.conf.update(kwargs)

    if transport_options:
        log.info(
            'loading transport_options={}'.format(
                transport_options))
        app.conf.update(**transport_options)
    # custom tranport options

    if ssl_options:
        log.info(
            'loading ssl_options={}'.format(
                ssl_options))
        app.conf.update(**ssl_options)
    # custom ssl options

    if len(include_tasks) > 0:
        app.autodiscover_tasks(include_tasks)

    return app
# end of get_celery_app
