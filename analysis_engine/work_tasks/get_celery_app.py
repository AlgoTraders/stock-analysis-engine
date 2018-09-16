"""
Build a Celery Application with a config module
and includable tasks lists
"""

import os
import celery
from celery_loaders.log.setup_logging import build_colorized_logger


log = build_colorized_logger(
    name='get_app')


def get_celery_app(
        name=os.getenv(
            'CELERY_NAME',
            'worker'),
        auth_url=os.getenv(
            'BROKER_URL',
            'redis://localhost:6379/9'),
        backend_url=os.getenv(
            'BACKEND_URL',
            'redis://localhost:6379/10'),
        include_tasks=[],
        ssl_options=None,
        transport_options=None,
        path_to_config_module=os.getenv(
            'CONFIG_MODULE_PATH',
            'celery_loaders.work_tasks.celery_config'),
        worker_log_format=os.getenv(
            'WORKER_LOG_FORMAT',
            '%(asctime)s: %(levelname)s %(message)s'),
        **kwargs):
    """get_celery_app

    :param name: name for this app
    :param auth_url: celery broker
    :param backend_url: celery backend
    :param include_tasks: list of modules containing tasks to add
    :param ssl_options: security options dictionary
    :param trasport_options: transport options dictionary
    :param path_to_config_module: config module
    :param worker_log_format: format for logs
    """

    if len(include_tasks) == 0:
        log.error((
            'creating celery app={} MISSING tasks={}').format(
                name,
                include_tasks))
    else:
        log.info((
            'creating celery app={} tasks={}').format(
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
        log.info((
            'loading transport_options={}').format(
                transport_options))
        app.conf.update(**transport_options)
    # custom tranport options

    if ssl_options:
        log.info((
            'loading ssl_options={}').format(
                ssl_options))
        app.conf.update(**ssl_options)
    # custom ssl options

    if len(include_tasks) > 0:
        app.autodiscover_tasks(include_tasks)

    return app
# end of get_celery_app
