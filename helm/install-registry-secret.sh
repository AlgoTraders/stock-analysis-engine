#!/bin/bash

if [[ -e ./analysis_engine/scripts/common_bash.sh ]]; then
    source ./analysis_engine/scripts/common_bash.sh
elif [[ -e ../analysis_engine/scripts/common_bash.sh ]]; then
    source ../analysis_engine/scripts/common_bash.sh
elif [[ -e ../../analysis_engine/scripts/common_bash.sh ]]; then
    source ../../analysis_engine/scripts/common_bash.sh
elif [[ -e /opt/sa/analysis_engine/scripts/common_bash.sh ]]; then
    source /opt/sa/analysis_engine/scripts/common_bash.sh
fi


src_namespace="default"
src_secret="ae.docker.creds"
dst_namespace="ae"
dst_secret="ae.docker.creds"

anmt "------------------------------------"
anmt "copying ${src_secret} secret from ${src_namespace} namespace to ${dst_namespace}"

key_exists_in_default=$(kubectl get secret ${src_secret} --namespace=${src_namespace} | wc -l)

if [[ "${key_exists_in_default}" == "0" ]]; then
    err "ERROR failed to find ${src_namespace} secret in ${src_namespace} namespace for credentials to use persistent volumes using c
ommand:"
    err "kubectl get secret ${src_secret} --namespace=${src_namespace}"
    exit 1
fi

kubectl \
    get secret \
    ${src_secret} --namespace=${src_namespace} \
    --export -o yaml | kubectl apply \
    --namespace=${dst_namespace} -f -

key_exists_in_ae=$(kubectl get secret ${dst_secret} --namespace=${dst_namespace} | wc -l)

if [[ "${key_exists_in_ae}" == "0" ]]; then
    err "ERROR failed to find ${dst_secret} secret in ${dst_namespace} namespace for credentials to use persistent volumes using command:"
    err "kubectl get secret ${dst_secret} --namespace=${dst_namespace}"
    exit 1
fi

exit 0
