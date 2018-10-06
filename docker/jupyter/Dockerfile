FROM jayjohnson/stock-analysis-engine:latest

ENV PROJECT_NAME="jupyter" \
    LOG_LEVEL="DEBUG" \
    LOG_FILE="/var/log/sa/jupyter.log" \
    USE_VENV="/opt/venv" \
    API_USER="trex" \
    API_PASSWORD="123321" \
    API_EMAIL="bugs@antinex.com" \
    API_FIRSTNAME="Guest" \
    API_LASTNAME="Guest" \
    API_URL="https://api.antinex.com" \
    API_VERBOSE="true" \
    API_DEBUG="false" \
    USE_FILE="false" \
    SILENT="-s" \
    RUN_JUPYTER="/opt/sa/docker/jupyter/start-container.sh" \
    JUPYTER_CONFIG="/opt/sa/docker/jupyter/jupyter_notebook_config.py" \
    NOTEBOOK_DIR="/opt/sa/docker/notebooks"

RUN . /opt/venv/bin/activate \
  && /opt/sa \
  && echo "pulling latest" \
  && git pull \
  && echo "upgrading pip" \
  && pip install --upgrade pip \
  && echo "installing pip upgrades" \
  && pip install --upgrade -e . \
  && echo "installing pip fixes for 2018-10-06" \
  && pip install --upgrade awscli boto3 botocore

WORKDIR /opt/sa/docker/jupyter

ENTRYPOINT . /opt/venv/bin/activate \
  && /opt/sa/docker/jupyter \
  && /opt/sa/docker/jupyter/start-container.sh
