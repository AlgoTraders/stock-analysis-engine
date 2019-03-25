#!/bin/bash

if [[ -e /opt/sa/analysis_engine/scripts/common_bash.sh ]]; then
    source /opt/sa/analysis_engine/scripts/common_bash.sh
elif [[ -e ./analysis_engine/scripts/common_bash.sh ]]; then
    source ./analysis_engine/scripts/common_bash.sh
fi

# exports for docker-compose pathing depending on the os
export PATH=${PATH}:/usr/bin:/usr/local/bin

# probably not ideal but needed for working on MacOS
# will also need to manually add:
# /data to Docker -> Preferences -> File Sharing
if [[ ! -e /data ]]; then
    sudo mkdir -p -m 777 /data
    if [[ ! -e /data/redis/data ]]; then
        sudo mkdir -p -m 777 /data/redis/data
    fi
    if [[ ! -e /data/minio/data ]]; then
        sudo mkdir -p -m 777 /data/minio/data
    fi
    if [[ ! -e /data/sa/notebooks/dev ]]; then
        sudo mkdir -p -m 777 /data/sa/notebooks/dev
    fi
    if [[ ! -e /data/registry ]]; then
        sudo mkdir -p -m 777 /data/registry
    fi
    if [[ ! -e /data/registry/auth ]]; then
        sudo mkdir -p -m 777 /data/registry/auth
        docker run --entrypoint htpasswd registry:2 -Bbn trex 123321 > /data/registry/auth/htpasswd
    fi
    if [[ ! -e /data/registry/data ]]; then
        sudo mkdir -p -m 777 /data/registry/data
    fi
    cp -r ./compose/docker/notebooks/* /data/sa/notebooks
fi

is_mac="0"
os_type=`uname -s`
case "$os_type" in
    Linux*)
        inf "Setting up environment for Linux"
        test_pkman=$(which dpkg | wc -l)
        if [[ "${test_pkman}" == "1" ]]; then
            test_deb=$(dpkg -s python3-distutils | grep 'install ok installed' | wc -l)
            if [[ "${test_deb}" == "0" ]]; then
                warn "using sudo to install python3-distutils python3-tk on ubuntu"
                sudo apt-get install python3-distutils python3-tk
            fi
        fi
        active_ports=`netstat -tulpn 2>> /dev/null | grep LISTEN`
        ;;
    Darwin*)
        inf "Setting up environment for MacOS"
        active_ports=`lsof -i -P -n | grep LISTEN`
        # sed replace without the '' does seem to work on mac and linux the same
        mac=".bak"
        is_mac="1"
        ;;
    *)
        warn "Unsupported OS, exiting."
        exit 1
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
    # overriding notebooks
    elif [[ "${i}" == "-jo" ]]; then
        debug="1"
        compose="notebook-integration.yml"
        rm -rf /data/sa/notebooks/
        cp -r ./compose/docker/notebooks/* /data/sa/notebooks
    # automation - dataset collection
    elif [[ "${i}" == "-c" ]]; then
        debug="1"
        # new v2 location that requires a new env file:
        # ./compose/envs/fetch.env
        # that is created manually
        compose="integration.yml"
        down_dir="0"
        if [[ ! -e ./${compose} ]]; then
            pushd compose >> /dev/null
            down_dir="1"
        fi
        anmt "starting dataset collection with: docker-compose -f ./${compose} start ae-dataset-collection"
        docker-compose -f ./${compose} start ae-dataset-collection
        if [[ "${down_dir}" == "1" ]]; then
            popd >> /dev/null
        fi
        exit 0
    elif [[ "${i}" == "-b" ]]; then
        debug="1"
        compose="bt/backtester.yml"
    elif [[ "${i}" == "-j" ]]; then
        debug="1"
        compose="jupyter/jupyter.yml"
    # end-to-end integration testing with notebook editing
    # over <repo base>/docker/notebooks:
    elif [[ "${i}" == "-j2" ]]; then
        debug="1"
        compose="notebook-integration.yml"
    elif [[ "${i}" == "-r" ]]; then
        debug="1"
        compose="registry/registry.yml"
    elif [[ "${i}" == "-s" ]]; then
        debug="1"
        compose="components/stack.yml"
    fi
done

anmt "-------------"
if [[ "${compose}" == "dev.yml" ]]; then
    inf "starting dev"
elif [[ "${compose}" == "redis-and-minio.yml" ]]; then
    inf "starting redis and minio"
elif [[ "${compose}" == "integration.yml" ]]; then
    inf "starting integration stack: redis, minio, workers, backtester, dataset collection and jupyter"
elif [[ "${compose}" == "notebook-integration.yml" ]]; then
    inf "starting end-to-end with notebook integration stack: redis, minio, workers and jupyter"
elif [[ "${compose}" == "automation-dataset-collection.yml" ]]; then
    inf "starting dataset collection"
elif [[ "${compose}" == "bt/backtester.yml" ]]; then
    inf "starting backtester"
elif [[ "${compose}" == "fetch/fetch.yml" ]]; then
    inf "starting dataset collection - version 2"
elif [[ "${compose}" == "jupyter/jupyter.yml" ]]; then
    inf "starting jupyter - version 2"
elif [[ "${compose}" == "registry/registry.yml" ]]; then
    inf "starting registry"
elif [[ "${compose}" == "components/stack.yml" ]]; then
    inf "starting stack: workers, backtester and jupyter"
else
    err "unsupported compose file: ${compose}"
    exit 1
fi

if [[ ! -e ./${compose} ]]; then
    pushd compose >> /dev/null
    down_dir="1"
fi

anmt "starting with: docker-compose -f ./${compose} up -d"
docker-compose -f ./${compose} up -d

if [[ "${down_dir}" == "1" ]]; then
    popd >> /dev/null
fi

if [[ "${compose}" == "dev.yml" ]]; then
    good "started dev"
elif [[ "${compose}" == "redis-and-minio.yml" ]]; then
    good "started redis (listening on 0.0.0.0:6379) and minio (listening on 0.0.0.0:9000)"
elif [[ "${compose}" == "integration.yml" ]]; then
    good "started integration stack: redis, minio, workers, backtester, dataset collection and jupyter"
elif [[ "${compose}" == "bt/backtester.yml" ]]; then
    good "started backtester"
elif [[ "${compose}" == "fetch/fetch.yml" ]]; then
    good "started dataset collection - version 2"
    docker ps -a | grep ae-fetch
elif [[ "${compose}" == "jupyter/jupyter.yml" ]]; then
    good "started jupyter - version 2"
elif [[ "${compose}" == "registry/registry.yml" ]]; then
    good "started registry"
elif [[ "${compose}" == "components/stack.yml" ]]; then
    good "started stack: workers, backtester and jupyter"
fi

exit 0
