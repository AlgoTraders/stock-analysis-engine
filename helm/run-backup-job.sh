#!/bin/bash

namespace="ae"
values="./ae-backup/values.yaml"
recreate="0"

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
    if [[ "${1}" == "-r" ]]; then
        recreate="1"
    else
        if [[ ! -e ${1} ]]; then
            err "Failed to find backup job values file: ${1}"
            exit 1
        fi
        values=${1}
    fi
fi

if [[ "${2}" != "" ]]; then
    if [[ "${2}" == "-r" ]]; then
        recreate="1"
    else
        if [[ ! -e ${2} ]]; then
            err "Failed to find backup job values file: ${2}"
            exit 1
        fi
        values=${2}
    fi
fi

if [[ "${recreate}" == "1" ]]; then
    anmt "deleting previous ae backup job"
    helm delete --purge ae-backup
    pod_name="backup"
    not_done=$(/usr/bin/kubectl get po -n ${namespace} | grep ${pod_name} | wc -l)
    while [[ "${not_done}" != "0" ]]; do
        date -u +"%Y-%m-%d %H:%M:%S"
        echo "sleeping while waiting for ${pod_name} to stop"
        sleep 5
        /usr/bin/kubectl get po -n ${namespace} | grep ${pod_name}
        not_done=$(/usr/bin/kubectl get po -n ${namespace} | grep ${pod_name} | wc -l)
    done
fi

# install ae first to get the secrets for minio and redis
anmt "installing ae backup job"
good "helm install --name=ae-backup ./ae-backup --namespace=${namespace} -f ${values}"
helm install \
    --name=ae-backup \
    ./ae-backup \
    --namespace=${namespace} \
    -f ${values}

anmt "checking running charts:"
helm ls

anmt "getting pods in ae namespace:"
kubectl get pods -n ae
