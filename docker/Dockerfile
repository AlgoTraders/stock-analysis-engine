FROM jayjohnson/ai-core:latest

RUN echo "creating project directories" \
  && git clone https://github.com/AlgoTraders/stock-analysis-engine.git /opt/sa \
  && mkdir -p -m 777 /var/log/sa \
  && chmod 777 /var/log/sa \
  && touch /var/log/sa/worker.log \
  && chmod 777 /var/log/sa/worker.log \
  && touch /var/log/sa/jupyter.log \
  && chmod 777 /var/log/sa/jupyter.log \
  && echo "updating repo" \
  && cd /opt/sa \
  && git checkout master \
  && git pull \
  && echo "checking repo in container" \
  && ls -l /opt/sa \
  && echo "activating venv" \
  && . /opt/venv/bin/activate \
  && cd /opt/sa \
  && echo "installing pip upgrades" \
  && pip install --upgrade -e . \
  && echo "building docs" \
  && cd /opt/sa/docs \
  && ls -l \
  && make html

ENV PROJECT_NAME="sa" \
    TICKER="SPY" \
    TICKER_ID="1" \
    WORKER_BROKER_URL="redis://0.0.0.0:6379/13" \
    WORKER_BACKEND_URL="redis://0.0.0.0:6379/14" \
    WORKER_CELERY_CONFIG_MODULE="analysis_engine.work_tasks.celery_service_config" \
    ENABLED_S3_UPLOAD="1" \
    S3_ACCESS_KEY="trexaccesskey" \
    S3_SECRET_KEY="trex123321" \
    S3_REGION_NAME="us-east-1" \
    S3_ADDRESS="0.0.0.0:9000" \
    S3_SECURE="0" \
    S3_BUCKET="pricing" \
    S3_KEY="SPY_latest" \
    ENABLED_REDIS_PUBLISH="1" \
    REDIS_ADDRESS="0.0.0.0:6379" \
    REDIS_KEY="SPY_latest" \
    REDIS_DB="4" \
    DEBUG_SHARED_LOG_CFG="0" \
    LOG_LEVEL="DEBUG" \
    LOG_FILE="/var/log/sa/worker.log" \
    SHARED_LOG_CFG="/opt/sa/analysis_engine/log/logging.json" \
    LOG_CONFIG_PATH="/opt/sa/analysis_engine/log/logging.json" \
    USE_VENV="/opt/venv" \
    API_USER="trex" \
    API_PASSWORD="123321" \
    API_EMAIL="bugs@antinex.com" \
    API_FIRSTNAME="Guest" \
    API_LASTNAME="Guest" \
    API_URL="https://api.example.com" \
    API_VERBOSE="true" \
    API_DEBUG="false" \
    USE_FILE="false" \
    SILENT="-s"

WORKDIR /opt/sa

# set for anonymous user access in the container
RUN find /opt/sa -type d -exec chmod 777 {} \;
RUN find /var/log/sa -type d -exec chmod 777 {} \;

ENTRYPOINT . /opt/venv/bin/activate \
  && /opt/sa/start-workers.sh
