#!/bin/bash

if [[ -e /opt/deploy-to-kubernetes/tools/bash_colors.sh ]]; then
    source /opt/deploy-to-kubernetes/tools/bash_colors.sh
else
    inf() {
        echo "$@"
    }
    anmt() {
        echo "$@"
    }
    good() {
        echo "$@"
    }
    err() {
        echo "$@"
    }
    critical() {
        echo "$@"
    }
    warn() {
        echo "$@"
    }
fi

down_dir="0"
debug="0"
compose="dev.yml"
for i in "$@"
do
    # just redis and minio testing:
    if [[ "${i}" == "-d" ]]; then
        debug="1"
    # end-to-end integration testing:
    elif [[ "${i}" == "-a" ]]; then
        debug="1"
        compose="integration.yml"
    # end-to-end integration testing with notebook editing
    # over <repo base>/docker/notebooks:
    elif [[ "${i}" == "-j" ]]; then
        debug="1"
        compose="notebook-integration.yml"
    # automation - dataset collection
    elif [[ "${i}" == "-c" ]]; then
        debug="1"
        compose="automation-dataset-collection.yml"
    fi
done

anmt "-------------"
if [[ "${compose}" == "dev.yml" ]]; then
    inf "stopping redis and minio"
elif [[ "${compose}" == "integration.yml" ]]; then
    inf "stopping integration stack: redis, minio, workers and jupyter"
elif [[ "${compose}" == "notebook-integration.yml" ]]; then
    inf "stopping end-to-end with notebook integration stack: redis, minio, workers and jupyter"
elif [[ "${compose}" == "automation-dataset-collection.yml" ]]; then
    inf "stopping dataset collection"
else
    err "unsupported compose file: ${compose}"
    exit 1
fi

if [[ ! -e ./${compose} ]]; then
    pushd compose >> /dev/null
    down_dir="1"
fi
docker-compose -f ./${compose} down

if [[ "${down_dir}" == "1" ]]; then
    popd >> /dev/null
fi

if [[ "${compose}" == "dev.yml" ]]; then
    good "stopped redis and minio"
elif [[ "${compose}" == "integration.yml" ]]; then
    good "stopped end-to-end integration stack: redis, minio, workers and jupyter"
fi

exit 0
