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

storage_class="ceph-rbd"
if [[ "${1}" != "" ]]; then
    storage_class="${1}"
fi

default_storage_class=$(kubectl get storageclass | grep default | awk '{print $1}')
anmt "setting default storage class for ae stack from:"
anmt "${default_storage_class} to: ${storage_class}"
kubectl patch storageclass ${default_storage_class} -p '{"metadata": {"annotations":{"storageclass.kubernetes.io/is-default-class":"false"}}}' >> /dev/null
kubectl patch storageclass ${storage_class} -p '{"metadata": {"annotations":{"storageclass.kubernetes.io/is-default-class":"true"}}}'

new_default_storage_class=$(kubectl get storageclass | grep default | awk '{print $1}')
if [[ "${new_default_storage_class}" == "${storage_class}" ]]; then
    good "${storage_class} is the default StorageClass"
    echo ""
    kubectl get storageclass
    echo ""
    exit 0
else
    err "Failed setting: ${storage_class} as the default StorageClass - default is: ${new_default_storage_class}"
    exit 1
fi
