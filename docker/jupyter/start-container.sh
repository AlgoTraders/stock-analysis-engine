#!/bin/bash

venv=/opt/venv

# support for using venv in other locations
if [[ "${USE_VENV}" != "" ]]; then
    if [[ -e ${USE_VENV}/bin/activate ]]; then
        echo "Using custom virtualenv: ${USE_VENV}"
        venv=${USE_VENV}
    else
        echo "Did not find custom virtualenv: ${USE_VENV}"
        exit 1
    fi
fi

echo "Activating pips: ${venv}/bin/activate"
. ${venv}/bin/activate
echo ""

pip list --format=columns

if [[ "${SHARED_LOG_CFG}" != "" ]]; then
    echo ""
    echo "Logging config: ${SHARED_LOG_CFG}"
    echo ""
fi

echo "Starting Jupyter"
notebook_config=/opt/sa/docker/jupyter/jupyter_notebook_config.py
notebook_dir=/opt/notebooks
notebook_ip="0.0.0.0"
notebook_port="8888"

if [[ "${JUPYTER_CONFIG}" != "" ]]; then
    if [[ -e ${JUPYTER_CONFIG} ]]; then
        notebook_config=${JUPYTER_CONFIG}
        echo " - using notebook_config: ${notebook_config}"
    else
        echo " - Failed to find notebook_config: ${JUPYTER_CONFIG}"
    fi
fi

if [[ "${NOTEBOOK_DIR}" != "" ]]; then
    if [[ -e ${NOTEBOOK_DIR} ]]; then
        notebook_dir=${NOTEBOOK_DIR}
        echo " - using notebook_dir: ${notebook_dir}"
    else
        echo " - Failed to find notebook_dir: ${NOTEBOOK_DIR}"
    fi
fi

if [[ "${NOTEBOOK_IP}" != "" ]]; then
    notebook_ip="${NOTEBOOK_IP}"
fi
if [[ "${NOTEBOOK_PORT}" != "" ]]; then
    notebook_port="${NOTEBOOK_PORT}"
fi

echo ""
echo "Starting Jupyter with command: "
echo "jupyter notebook --ip=${notebook_ip} --port=${notebook_port} --no-browser --config=${notebook_config} --notebook-dir=${notebook_dir} --allow-root"
jupyter notebook \
    --ip=${notebook_ip} \
    --port=${notebook_port} \
    --no-browser \
    --config=${notebook_config} \
    --notebook-dir=${notebook_dir} \
    --allow-root

exit 0
