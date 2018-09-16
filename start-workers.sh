#!/bin/bash

if [[ -e /opt/venv/bin/activate ]]; then
    source /opt/venv/bin/activate
fi

num_workers=1
log_level=INFO
worker_module=analysis_engine.start_worker
worker_name="analysis_engine@%h"

if [[ "${NUM_WORKERS}" != "" ]]; then
    num_workers=$NUM_WORKERS
fi
if [[ "${LOG_LEVEL}" != "" ]]; then
    log_level=$LOG_LEVEL
fi
if [[ "${WORKER_MODULE}" != "" ]]; then
    worker_module=$WORKER_MODULE
fi
if [[ "${WORKER_NAME}" != "" ]]; then
    worker_name=$WORKER_NAME
fi

echo ""
if [[ "${num_workers}" == "1" ]]; then
    echo "starting worker=${worker_module}"
    echo "celery worker -A ${worker_module} -c ${num_workers} -l ${log_level} -n ${worker_name}"
    celery worker -A ${worker_module} -c ${num_workers} -l ${log_level} -n ${worker_name}
else
    echo "starting workers=${worker_module}"
    echo "celery worker -A ${worker_module} -c ${num_workers} -l ${log_level} -n ${worker_name}"
    celery worker -A ${worker_module} -c ${num_workers} -l ${log_level} -n ${worker_name}
fi
echo ""
