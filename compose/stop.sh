#!/bin/bash

if [[ -e /opt/sa/analysis_engine/scripts/common_bash.sh ]]; then
    source /opt/sa/analysis_engine/scripts/common_bash.sh
elif [[ -e ./analysis_engine/scripts/common_bash.sh ]]; then
    source ./analysis_engine/scripts/common_bash.sh
fi

# exports for docker-compose pathing depending on the os
export PATH=${PATH}:/usr/bin:/usr/local/bin

os_type=`uname -s`
case "$os_type" in
    Linux*)
        inf "Stopping environment for Linux"
        active_ports=`netstat -tulpn 2>> /dev/null | grep LISTEN`
        ;;
    Darwin*)
        inf "Stopping environment for MacOS"
        active_ports=`lsof -i -P -n | grep LISTEN`
        # sed replace without the '' does seem to work on mac and linux the same
        mac=".bak"
        ;;
    *)
        warn "Unsupported OS, exiting."
        exit 0
        ;;
esac

down_dir="0"
debug="0"
compose="integration.yml"
for i in "$@"
do
    # just redis and minio testing:
    if [[ "${i}" == "-d" ]]; then
        debug="1"
    # end-to-end integration testing:
    elif [[ "${i}" == "-a" ]]; then
        debug="1"
        compose="redis-and-minio.yml"
    # end-to-end integration testing with notebook editing
    # over <repo base>/docker/notebooks:
    elif [[ "${i}" == "-j1" ]]; then
        debug="1"
        compose="notebook-integration.yml"
    # automation - dataset collection
    elif [[ "${i}" == "-c" ]]; then
        debug="1"
        compose="automation-dataset-collection.yml"
        workers=`ps auwwx | grep $USER | grep python3 | grep start_worker | awk '{print $2}'`
        if [[ ! -z "$workers" ]]; then
            echo $workers | xargs kill -9
        fi
        # new v2 location that requires a new env file:
        # ./compose/envs/fetch.env
        # that is created manually
        if [[ -e ./compose/fetch/fetch.yml ]]; then
            compose="fetch/fetch.yml"
        fi
    elif [[ "${i}" == "-b" ]]; then
        debug="1"
        compose="bt/backtester.yml"
    elif [[ "${i}" == "-j" ]]; then
        debug="1"
        compose="jupyter/jupyter.yml"
    elif [[ "${i}" == "-r" ]]; then
        debug="1"
        compose="registry/registry.yml"
    elif [[ "${i}" == "-s" ]]; then
        debug="1"
        compose="components/stack.yml"
    fi
done

anmt "-------------"
containers=""
if [[ "${compose}" == "dev.yml" ]]; then
    inf "stopping dev"
    containers="redis minio"
elif [[ "${compose}" == "redis-and-minio.yml" ]]; then
    inf "stopping redis and minio"
    containers="redis minio"
elif [[ "${compose}" == "integration.yml" ]]; then
    inf "stopping integration stack: redis, minio, workers, backtester, dataset collection and jupyter"
    containers="ae-workers ae-jupyter ae-backtester ae-dataset-collection redis minio"
elif [[ "${compose}" == "notebook-integration.yml" ]]; then
    inf "stopping end-to-end with notebook integration stack: redis, minio, workers and jupyter"
    containers="ae-workers ae-jupyter redis minio"
elif [[ "${compose}" == "automation-dataset-collection.yml" ]]; then
    inf "stopping dataset collection"
    containers="ae-dataset-collection ae-fetch"
elif [[ "${compose}" == "bt/backtester.yml" ]]; then
    inf "stopping backtester"
    containers="ae-backtester"
elif [[ "${compose}" == "fetch/fetch.yml" ]]; then
    inf "stopping dataset collection - version 2"
    containers="ae-fetch"
elif [[ "${compose}" == "jupyter/jupyter.yml" ]]; then
    inf "stopping jupyter - version 2"
    containers="ae-jupyter"
elif [[ "${compose}" == "registry/registry.yml" ]]; then
    inf "stopping registry"
    containers="registry"
elif [[ "${compose}" == "components/stack.yml" ]]; then
    inf "stopping stack: workers, backtester and jupyter"
    containers="ae-workers ae-backtester ae-jupyter"
else
    err "unsupported compose file: ${compose}"
    exit 1
fi

if [[ ! -e ./${compose} ]]; then
    pushd compose >> /dev/null
    down_dir="1"
fi

docker-compose -f ./${compose} down >> /dev/null 2>&1

for c in ${containers}; do
    test_exists=$(docker ps -a | grep ${c} | wc -l)
    if [[ "${test_exists}" != "0" ]]; then
        echo "cleaning up ${c}"
        docker stop ${c} >> /dev/null 2>&1
        docker rm ${c} >> /dev/null 2>&1
    fi
done

if [[ "${down_dir}" == "1" ]]; then
    popd >> /dev/null
fi

if [[ "${compose}" == "dev.yml" ]]; then
    good "stopped redis and minio"
elif [[ "${compose}" == "redis-and-minio.yml" ]]; then
    good "stopped redis and minio"
elif [[ "${compose}" == "integration.yml" ]]; then
    good "stopped integration stack: redis, minio, workers, backtester, dataset collection and jupyter"
elif [[ "${compose}" == "bt/backtester.yml" ]]; then
    good "stopped backtester"
elif [[ "${compose}" == "fetch/fetch.yml" ]]; then
    good "stopped dataset collection - version 2"
elif [[ "${compose}" == "jupyter/jupyter.yml" ]]; then
    good "stopped jupyter - version 2"
elif [[ "${compose}" == "registry/registry.yml" ]]; then
    good "stopped registry"
elif [[ "${compose}" == "components/stack.yml" ]]; then
    good "stopped stack: workers, backtester and jupyter"
fi

exit 0
