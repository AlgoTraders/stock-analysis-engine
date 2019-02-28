FROM jayjohnson/stock-analysis-engine:base-1.9.3

RUN echo "installing source" \
  && echo "activating venv" \
  && . /opt/venv/bin/activate \
  && cd /opt \
  && echo "uninstalling previous builds from the base image" \
  && pip uninstall -y stock-analysis-engine spylunking \
  && echo "removing /opt/sa /opt/spylunking repository directories" \
  && rm -rf /opt/sa /opt/spylunking \
  && echo "cloning" \
  && git clone https://github.com/AlgoTraders/stock-analysis-engine.git /opt/sa \
  && git clone https://github.com/jay-johnson/spylunking.git /opt/spylunking \
  && echo "updating logging" \
  && cd /opt/spylunking \
  && pip install --upgrade -e . \
  && echo "updating ae" \
  && cd /opt/sa \
  && pip install --upgrade -e . \
  && echo "updating repo" \
  && ls -l /opt/sa \
  && echo "installing notebooks from: /opt/sa/compose/docker/notebooks/ to /opt/notebooks" \
  && cp -r /opt/sa/compose/docker/notebooks/* /opt/notebooks/ \
  && /opt/sa/tools/prepare_for_k8.sh

ENV PROJECT_NAME="sa" \
    TICKER="SPY" \
    TICKER_ID="1" \
    WORKER_BROKER_URL="redis://0.0.0.0:6379/13" \
    WORKER_BACKEND_URL="redis://0.0.0.0:6379/14" \
    WORKER_CELERY_CONFIG_MODULE="analysis_engine.work_tasks.celery_service_config" \
    WORKER_TASKS="analysis_engine.work_tasks.get_new_pricing_data,analysis_engine.work_tasks.handle_pricing_update_task,analysis_engine.work_tasks.prepare_pricing_dataset,analysis_engine.work_tasks.publish_from_s3_to_redis,analysis_engine.work_tasks.publish_pricing_update,analysis_engine.work_tasks.task_screener_analysis,analysis_engine.work_tasks.publish_ticker_aggregate_from_s3,analysis_engine.work_tasks.task_run_algo" \
    ENABLED_S3_UPLOAD="1" \
    S3_ACCESS_KEY="trexaccesskey" \
    S3_SECRET_KEY="trex123321" \
    S3_REGION_NAME="us-east-1" \
    S3_ADDRESS="0.0.0.0:9000" \
    S3_SECURE="0" \
    S3_BUCKET="pricing" \
    S3_COMPILED_BUCKET="compileddatasets" \
    S3_KEY="SPY_latest" \
    ENABLED_REDIS_PUBLISH="1" \
    REDIS_ADDRESS="0.0.0.0:6379" \
    REDIS_KEY="SPY_latest" \
    REDIS_DB="0" \
    DEBUG_SHARED_LOG_CFG="0" \
    LOG_LEVEL="DEBUG" \
    LOG_FILE="/var/log/sa/worker.log" \
    SHARED_LOG_CFG="/opt/sa/analysis_engine/log/logging.json" \
    LOG_CONFIG_PATH="/opt/sa/analysis_engine/log/logging.json" \
    USE_VENV="/opt/venv"

WORKDIR /opt/sa

ENTRYPOINT . /opt/venv/bin/activate \
  && /opt/sa/start-workers.sh
