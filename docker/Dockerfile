FROM python:3.6-slim

RUN apt-get update \
  && apt-get install -y \
    autoconf \
    build-essential \
    cmake \
    curl \
    gcc \
    git \
    libcurl4-openssl-dev \
    libssl-dev \
    libffi6 \
    libffi-dev \
    lsof \
    make \
    mlocate \
    netcat \
    net-tools \
    openssl \
    pandoc \
    python3 \
    python3-dev \
    python3-pip \
    python3-tk \
    python-setuptools \
    python-virtualenv \
    python-pip \
    redis-tools \
    s3cmd \
    software-properties-common \
    strace \
    telnet \
    unzip \
    uuid-runtime \
    vim \
    wget

RUN echo "preparing virtualenv" \
  && pip install --upgrade virtualenvwrapper pip \
  && echo "creating virtualenv" \
  && virtualenv -p python3 /opt/venv \
  && chmod 777 /opt/venv \
  && echo "setting up virtualenv" \
  && . /opt/venv/bin/activate \
  && pip install --upgrade setuptools pip

RUN echo "" >> /root/.bashrc \
  && echo "if [[ -e /opt/venv/bin/activate ]]; then" >> /root/.bashrc \
  && echo "    . /opt/venv/bin/activate" >> /root/.bashrc \
  && echo "fi" >> /root/.bashrc \
  && echo "" >> /root/.bashrc \
  && echo "if [[ -e /opt/sa/analysis_engine/scripts/common_bash.sh ]]; then" >> /root/.bashrc \
  && echo "    . /opt/sa/analysis_engine/scripts/common_bash.sh" >> /root/.bashrc \
  && echo "fi" >> /root/.bashrc \
  && echo "" >> /root/.bashrc \
  && echo "alias dev='cd /opt/sa'" >> /root/.bashrc \
  && echo "alias sp='cd /opt/spylunking'" >> /root/.bashrc \
  && echo "alias vi='/usr/bin/vim'" >> /root/.bashrc

RUN echo "setting up /etc/pip.conf" \
  && echo "" >> /etc/pip.conf \
  && echo "[list]" >> /etc/pip.conf \
  && echo "format=columns" >> /etc/pip.conf

RUN echo "installing source" \
  && echo "activating venv" \
  && . /opt/venv/bin/activate \
  && echo "cloning repos" \
  && git clone https://github.com/AlgoTraders/stock-analysis-engine.git /opt/sa \
  && git clone https://github.com/jay-johnson/deploy-to-kubernetes.git /opt/deploy-to-kubernetes \
  && git clone https://github.com/jay-johnson/spylunking.git /opt/spylunking \
  && chmod 775 \
    /opt/deploy-to-kubernetes \
    /opt/spylunking \
  && if [[ -e /opt/sa/docker/vimrc ]]; then cp /opt/sa/docker/vimrc /root/.vimrc; fi \
  && mkdir -p -m 777 /var/log/sa \
  && mkdir -p -m 777 /opt/notebooks \
  && chmod 777 /var/log/sa \
  && touch /var/log/sa/worker.log \
  && chmod 777 /var/log/sa/worker.log \
  && touch /var/log/sa/jupyter.log \
  && chmod 777 /var/log/sa/jupyter.log \
  && echo "updating repo" \
  && ls -l /opt/sa \
  && echo "installing notebooks from: /opt/sa/compose/docker/notebooks/ to /opt/notebooks" \
  && cp -r /opt/sa/compose/docker/notebooks/* /opt/notebooks/ \
  && echo "upgrading pip" \
  && pip install --upgrade pip \
  && cd /opt/spylunking \
  && echo "installing spylunking" \
  && pip install --upgrade -e . \
  && echo "installing ta-lib dependencies" \
  && pip install --upgrade numpy \
  && cd /opt/sa \
  && echo "installing ta-lib with: /opt/sa/tools/linux-install-talib.sh" \
  && /opt/sa/tools/linux-install-talib.sh \
  && echo "installing pip upgrades" \
  && pip install --upgrade -e . \
  && echo "installing pip fixes for 2018-10-06" \
  && pip install --upgrade awscli boto3 botocore \
  && echo "installing jupyter pips" \
  && pip install --upgrade \
    requests \
    seaborn \
    RISE \
    vega3 \
    jupyter \
  && pip list --format=columns

RUN cp -r /root/.jupyter /root/.bak_jupyter || true
RUN rm -rf /root/.jupyter || true
RUN cp -r /root/notebooks /root/.bak_notebooks || true
RUN rm -rf /root/notebooks || true

RUN echo "Installing Vega" \
  && . /opt/venv/bin/activate \
  && /opt/venv/bin/jupyter-nbextension install vega3 --py

RUN echo "Enabling Vega" \
  && . /opt/venv/bin/activate \
  && /opt/venv/bin/jupyter-nbextension enable vega3 --py

RUN echo "Installing Rise" \
  && . /opt/venv/bin/activate \
  && /opt/venv/bin/jupyter-nbextension install rise --py

RUN echo "Enabling Rise" \
  && . /opt/venv/bin/activate \
  && /opt/venv/bin/jupyter-nbextension enable rise --py

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

# set for anonymous user access in the container
RUN find /opt/deploy-to-kubernetes -type d -exec chmod 777 {} \;
RUN find /opt/spylunking -type d -exec chmod 777 {} \;
RUN find /opt/venv -type d -exec chmod 777 {} \;
RUN find /opt/sa -type d -exec chmod 777 {} \;
RUN find /var/log -type d -exec chmod 777 {} \;
RUN find /opt/notebooks -type d -exec chmod 777 {} \;

ENTRYPOINT . /opt/venv/bin/activate \
  && /opt/sa/start-workers.sh
