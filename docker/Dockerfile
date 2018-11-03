FROM jayjohnson/ai-core:latest

RUN echo "installing talib for python pip ta-lib" \
  && cd /opt \
  && echo "getting ta-lib: http://prdownloads.sourceforge.net/ta-lib/ta-lib-0.4.0-src.tar.gz" \
  && wget http://prdownloads.sourceforge.net/ta-lib/ta-lib-0.4.0-src.tar.gz \
  && ls /opt/ta-lib-0.4.0-src.tar.gz \
  && echo "extracting /opt/ta-lib-0.4.0-src.tar.gz" \
  && tar xvf ta-lib-0.4.0-src.tar.gz \
  && ls /opt/ta-lib \
  && cd /opt/ta-lib \
  && echo "configuring ta-lib with /usr" \
  && ./configure --prefix=/usr \
  && echo "making ta-lib" \
  && make \
  && echo "installing ta-lib" \
  && make install \
  && echo "activating virtualenv" \
  && . /opt/venv/bin/activate \
  && echo "installing ta-lib pip" \
  && pip install ta-lib

RUN echo "installing redis-tools" \
  && apt-get install -y redis-tools \
  && echo "creating project directories" \
  && git clone https://github.com/AlgoTraders/stock-analysis-engine.git /opt/sa \
  && mkdir -p -m 777 /var/log/sa \
  && mkdir -p -m 777 /opt/notebooks \
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
  && echo "installing notebooks from: /opt/sa/compose/docker/notebooks/ to /opt/notebooks" \
  && cp -r /opt/sa/compose/docker/notebooks/* /opt/notebooks/ \
  && echo "activating venv" \
  && . /opt/venv/bin/activate \
  && cd /opt/sa \
  && echo "upgrading pip" \
  && pip install --upgrade pip \
  && echo "installing pip upgrades" \
  && pip install --upgrade -e . \
  && echo "installing pip fixes for 2018-10-06" \
  && pip install --upgrade awscli boto3 botocore \
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
    WORKER_TASKS="analysis_engine.work_tasks.get_new_pricing_data,analysis_engine.work_tasks.handle_pricing_update_task,analysis_engine.work_tasks.prepare_pricing_dataset,analysis_engine.work_tasks.publish_from_s3_to_redis,analysis_engine.work_tasks.publish_pricing_update,analysis_engine.work_tasks.task_screener_analysis,analysis_engine.work_tasks.publish_ticker_aggregate_from_s3" \
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
RUN find /opt/notebooks -type d -exec chmod 777 {} \;

ENTRYPOINT . /opt/venv/bin/activate \
  && /opt/sa/start-workers.sh
