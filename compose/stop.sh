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
        workers=`ps auwwx | grep $USER | grep python3 | grep start_worker | awk '{print $2}'`
        if [[ ! -z "$workers" ]]; then
            echo $workers | xargs kill -9
        fi
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

# start getting ports and setting vars for containers
if [[ -z `cat envs/.env | grep $USER` ]]; then
    sed -i $mac "s/redis:/redis-$USER:/g" envs/.env
    sed -i $mac "s/-$USER:\/\//:\/\//" envs/.env
    sed -i $mac "s/minio:/minio-$USER:/g" envs/.env
fi

# if containers for the current user are not running
if [[ -z `docker ps | grep $USER | grep redis` ]]; then
    BASE_REDIS_PORT=6379
    while [[ ! -z `echo "$active_ports" | grep $BASE_REDIS_PORT` ]]
    do
        BASE_REDIS_PORT=$((BASE_REDIS_PORT+1))
    done
else
    BASE_REDIS_PORT=`docker ps | grep $USER | grep redis | cut -f1 -d">" | sed -e 's/.*://' | cut -f1 -d"-"`
fi

if [[ -z `docker ps | grep $USER | grep minio` ]]; then
    BASE_MINIO_PORT=9000
    while [[ ! -z `echo "$active_ports" | grep $BASE_MINIO_PORT` ]]
    do
        BASE_MINIO_PORT=$((BASE_MINIO_PORT+1))
    done
else
    BASE_MINIO_PORT=`docker ps | grep $USER | grep minio | cut -f1 -d">" | sed -e 's/.*://' | cut -f1 -d"-"`
fi

if [[ -z `docker ps | grep $USER | grep jupyter` ]]; then
    BASE_JUPYTER_PORT_1=8888
    BASE_JUPYTER_PORT_2=8889
    BASE_JUPYTER_PORT_3=8890
    BASE_JUPYTER_PORT_4=6006
    while [[ ! -z `echo "$active_ports" | grep $BASE_JUPYTER_PORT_1` ]]
    do
        BASE_JUPYTER_PORT_1=$((BASE_JUPYTER_PORT_1+3))
        BASE_JUPYTER_PORT_2=$((BASE_JUPYTER_PORT_2+3))
        BASE_JUPYTER_PORT_3=$((BASE_JUPYTER_PORT_3+3))
        BASE_JUPYTER_PORT_4=$((BASE_JUPYTER_PORT_4+1))
    done
else
    BASE_JUPYTER_PORT_1=`docker ps | grep $USER | grep jupyter | sed -e 's/.*,//' | cut -f1 -d">" | sed -e 's/.*://' | cut -f1 -d"-"`
    BASE_JUPYTER_PORT_2=$((BASE_JUPYTER_PORT_1+1))
    BASE_JUPYTER_PORT_3=$((BASE_JUPYTER_PORT_2+1))
    BASE_JUPYTER_PORT_4=`docker ps | grep $USER | grep jupyter | cut -f1 -d">" | sed -e 's/.*://' | cut -f1 -d"-"`
fi

echo "export REDIS_PORT=$BASE_REDIS_PORT" > env.sh
echo "export MINIO_PORT=$BASE_MINIO_PORT" >> env.sh
echo "export JUPYTER_PORT_1=$BASE_JUPYTER_PORT_1" >> env.sh
echo "export JUPYTER_PORT_2=$BASE_JUPYTER_PORT_2" >> env.sh
echo "export JUPYTER_PORT_3=$BASE_JUPYTER_PORT_3" >> env.sh
echo "export JUPYTER_PORT_4=$BASE_JUPYTER_PORT_4" >> env.sh
source ./env.sh
rm env.sh
# end getting ports and setting vars for containers

docker-compose -f ./${compose} -p $USER down

containers="sa-workers-${USER} sa-jupyter-${USER} redis-${USER} minio-${USER} sa-dataset-collection-${USER}"
for c in ${containers}; do
    test_exists=$(docker ps -a | grep ${c} | wc -l)
    if [[ "${test_exists}" != "0" ]]; then
        echo "cleaning up ${c}"
        docker stop ${c} >> /dev/null 2>&1
        docker rm ${c} >> /dev/null 2>&1
    fi
done

# MacOS specific, remove the backup file that is created by sed -i 
if [[ -n $mac && -f envs/.env$mac ]]; then
    rm envs/.env$mac
fi

if [[ "${down_dir}" == "1" ]]; then
    popd >> /dev/null
fi

if [[ "${compose}" == "dev.yml" ]]; then
    good "stopped redis and minio"
elif [[ "${compose}" == "integration.yml" ]]; then
    good "stopped end-to-end integration stack: redis, minio, workers and jupyter"
fi

exit 0
