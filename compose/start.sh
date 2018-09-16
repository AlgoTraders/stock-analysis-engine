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

anmt "-------------"
test_redis=$(docker ps | grep redis | wc -l | tr -d '[:space:]')
if [[ "${test_redis}" == "0" ]]; then
    inf "starting redis"
    if [[ ! -e ./redis.yml ]] && [[ -e ./compose/redis.yml ]] ; then
        pushd compose
        down_dir="1"
    fi
    docker-compose -f ./redis.yml up -d
else
    inf "redis is already running"
fi

test_minio=$(docker ps | grep minio | wc -l | tr -d '[:space:]')
if [[ "${test_minio}" == "0" ]]; then
    inf "starting minio"
    ./run-minio.sh
else
    inf "minio is already running"
fi

inf ""
docker ps -a | grep -E "minio|redis|IMAGE"

if [[ "${down_dir}" == "1" ]]; then
    popd
fi

good "redis and minio are running"
