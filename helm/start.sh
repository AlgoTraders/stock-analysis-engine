#!/bin/bash

namespace="ae"
redis="./redis/values.yaml"
minio="./minio/values.yaml"
ae="./ae/values.yaml"
jupyter="./ae-jupyter/values.yaml"

if [[ -e ./analysis_engine/scripts/common_bash.sh ]]; then
    source ./analysis_engine/scripts/common_bash.sh
elif [[ -e ../analysis_engine/scripts/common_bash.sh ]]; then
    source ../analysis_engine/scripts/common_bash.sh
elif [[ -e ../../analysis_engine/scripts/common_bash.sh ]]; then
    source ../../analysis_engine/scripts/common_bash.sh
elif [[ -e /opt/sa/analysis_engine/scripts/common_bash.sh ]]; then
    source /opt/sa/analysis_engine/scripts/common_bash.sh
fi

if [[ "${1}" != "" ]]; then
    if [[ ! -e ${1} ]]; then
        err "Failed to find ae values file: ${1}"
        exit 1
    fi
    ae=${1}
fi

test_running=$(helm ls | grep ae | grep -v -E "ae-backup|ae-intraday|ae-daily|ae-weekly|ae-jupyter|ae-redis|ae-minio|ae-grafana|ae-prometheus" | wc -l)
if [[ "${test_running}" == "0" ]]; then
    # install ae first to get the secrets for minio and redis
    anmt "installing ae core"
    good "helm install --name=ae ./ae --namespace=${namespace} -f ${ae}"
    helm install \
        --name=ae \
        ./ae \
        --namespace=${namespace} \
        -f ${ae}
else
    good "ae core is already running"
fi

test_minio=$(helm ls | grep ae-minio | wc -l)
if [[ "${test_minio}" == "0" ]]; then
    test_minio_tls=$(kubectl get --ignore-not-found -n ${namespace} secret | grep tls.minio | wc -l)
    if [[ "${test_minio_tls}" == "0" ]]; then
        anmt "installing minio secret: tls.minio"
        ./install-tls.sh tls.minio ./minio/ssl/aeminio_server_key.pem ./minio/ssl/aeminio_server_cert.pem
    else
        good "tls secret: tls.minio already exists"
    fi
    anmt "installing minio"
    good "helm install --name=ae-minio local/minio --namespace=${namespace} -f ${minio}"
    helm install \
        --name=ae-minio \
        local/minio \
        --namespace=${namespace} \
        -f ${minio}
else
    good "minio is already installed"
fi

test_redis=$(helm ls | grep ae-redis | wc -l)
if [[ "${test_redis}" == "0" ]]; then
    anmt "installing redis"
    good "helm install --name=ae-redis stable/redis --namespace=${namespace} -f ${redis}"
    helm install \
        --name=ae-redis \
        stable/redis \
        --namespace=${namespace} \
        -f ${redis}
else
    good "redis is already installed"
fi

test_jupyter=$(helm ls | grep ae-jupyter | wc -l)
if [[ "${test_jupyter}" == "0" ]]; then
    anmt "installing jupyter"
    good "helm install --name=ae-jupyter ./ae-jupyter --namespace=${namespace} -f ${jupyter}"
    helm install \
        --name=ae-jupyter \
        ./ae-jupyter \
        --namespace=${namespace} \
        -f ${jupyter}
else
    good "jupyter is already installed"
fi
echo ""

anmt "checking running charts:"
helm ls

anmt "getting pods in ae namespace:"
kubectl get pods -n ae
