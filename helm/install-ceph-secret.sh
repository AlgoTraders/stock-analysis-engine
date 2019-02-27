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

namespace="ae"

anmt "------------------------------------"
anmt "copying ceph secret from ceph namespace to ${namespace}"

key_exists_in_ceph=$(kubectl get secret pvc-ceph-client-key --namespace=ceph | wc -l)

if [[ "${key_exists_in_ceph}" == "0" ]]; then
    err "ERROR failed to find ceph secret in ceph namespace for credentials to use persistent volumes using c
ommand:"
    err "kubectl get secret pvc-ceph-client-key --namespace=ceph"
    exit 1
fi

kubectl \
    get secret \
    pvc-ceph-client-key --namespace=ceph \
    --export -o yaml | kubectl apply \
    --namespace=${namespace} -f -

key_exists_in_ae=$(kubectl get secret pvc-ceph-client-key --namespace=${namespace} | wc -l)

if [[ "${key_exists_in_ae}" == "0" ]]; then
    err "ERROR failed to find ceph secret in ae namespace for credentials to use persistent volumes using command:"
    err "kubectl get secret pvc-ceph-client-key --namespace=${namespace}"
    exit 1
fi

exit 0
