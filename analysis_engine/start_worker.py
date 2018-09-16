#!/usr/bin/env python

from celery import signals
from celery_loaders.work_tasks.get_celery_app import get_celery_app
from spylunking.log.setup_logging import build_colorized_logger
from analysis_engine.consts import APP_NAME
from analysis_engine.consts import LOG_CONFIG_PATH
from analysis_engine.consts import WORKER_BROKER_URL
from analysis_engine.consts import WORKER_BACKEND_URL
from analysis_engine.consts import WORKER_TASKS
from analysis_engine.consts import INCLUDE_TASKS


# Disable celery log hijacking
# https://github.com/celery/celery/issues/2509
@signals.setup_logging.connect
def setup_celery_logging(**kwargs):
    pass


log = build_colorized_logger(
    name=APP_NAME,
    log_config_path=LOG_CONFIG_PATH)

log.info((
    'start - {}').format(
        APP_NAME))

log.info((
    'broker={} backend={} include_tasks={}').format(
        WORKER_BROKER_URL,
        WORKER_BACKEND_URL,
        WORKER_TASKS))

# Get the Celery app from the project's get_celery_app module
app = get_celery_app(
    name=APP_NAME,
    auth_url=WORKER_BROKER_URL,
    backend_url=WORKER_BACKEND_URL,
    include_tasks=INCLUDE_TASKS)

log.info('starting celery')
app.start()

log.info(('end - {}')
         .format(
             APP_NAME))
