#!/bin/bash

namespace="ae"
repo="/opt/sa"
kubeconfig="/opt/k8/config"
redis="./redis/values.yaml"
minio="./minio/values.yaml"
ae="./ae/values.yaml"
jupyter="./ae-jupyter/values.yaml"
use_ceph="0"

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
if [[ "${2}" != "" ]]; then
    if [[ ! -e ${2} ]]; then
        err "Failed to find KUBECONFIG=${2}"
        exit 1
    fi
    kubeconfig=${2}
fi
if [[ "${3}" != "" ]]; then
    if [[ "${3}" == "-c" ]]; then
        good "will install ceph cluster"
        use_ceph=1
    elif [[ -e ${3} ]]; then
        repo=${3}
    else
        err "Failed to find helm repo dir=${3}"
        exit 1
    fi
fi
if [[ "${4}" != "" ]]; then
    if [[ ! -e ${4} ]]; then
        err "Failed to find helm repo dir=${4}"
        exit 1
    fi
    repo=${4}
fi

export PATH=${PATH}:/usr/bin:/snap/bin
export KUBECONFIG=${kubeconfig}

test_kubectl=$(which kubectl | wc -l)
if [[ "${test_kubectl}" == "0" ]]; then
    err "Failed to find kubectl on the supported PATH environment variable - please install kubectl and export the PATH for the cron job to work"
    exit 1
fi

test_helm=$(which helm | wc -l)
if [[ "${test_helm}" == "0" ]]; then
    err "Failed to find helm on the supported PATH environment variable - please install helm and export the PATH for the cron job to work"
    exit 1
fi

anmt "using ae values=${ae} repo=${repo} KUBECONFIG=${KUBECONFIG} use_ceph=${use_ceph}"
cur_dir=$(pwd)

if [[ "${use_ceph}" == "1" ]]; then
    if [[ ! -e /opt/deploy-to-kubernetes ]]; then
        anmt "cloning https://github.com/jay-johnson/deploy-to-kubernetes.git to /opt/deploy-to-kubernetes"
        git clone https://github.com/jay-johnson/deploy-to-kubernetes.git /opt/deploy-to-kubernetes
    fi
    if [[ ! -e /opt/deploy-to-kubernetes ]]; then
        err "Failed to clone https://github.com/jay-johnson/deploy-to-kubernetes.git to /opt/deploy-to-kubernetes"
        err "command:"
        echo "git clone https://github.com/jay-johnson/deploy-to-kubernetes.git /opt/deploy-to-kubernetes"
        exit 1
    fi
fi

anmt "getting kubernetes nodes:"
kubectl get nodes -o wide

anmt "getting kubernetes default pods:"
kubectl get pods

anmt "getting kubernetes ae pods:"
kubectl get pods -n ${namespace}

if [[ "${use_ceph}" == "1" ]]; then
    cd /opt/deploy-to-kubernetes >> /dev/null
    anmt "deploying ceph cluster pods and ceph-rbd storage pods"
    ./ceph/run.sh
else
    good "skipping ceph install"
fi

anmt "sleeping for 2 minutes before deploying"
sleep 120

cd ${repo}/helm

anmt "installing docker registry secret"
./install-registry-secret.sh

anmt "installing ceph secret"
./install-ceph-secret.sh

anmt "installing ceph as storageClass"
./set-storage-class.sh ceph-rbd

anmt "sleeping for 10 seconds before deploying"
sleep 10

anmt "starting ae with helm"
./start.sh

anmt "sleeping for 2 minutes before running restore job"
sleep 120

anmt "restoring latest pricing data from S3 to Redis with helm ae-restore chart"
./run-job.sh restore /opt/k8/config ${repo}

anmt "sleeping for 10 seconds before checking ae-restore job"
sleep 10

anmt "checking restore logs:"
./logs-job-restore.sh

anmt "getting kubernetes ae pods:"
kubectl get pods -n ${namespace}

anmt "checking engine pod:"
./describe-engine.sh
./logs-engine.sh

anmt "installing tls secrets"
./install-tls.sh tls.aeminio ./minio/ssl/aeminio_server_key.pem ./minio/ssl/aeminio_server_cert.pem ${namespace}
./install-tls.sh tls.prometheus ./prometheus/ssl/aeprometheus_server_key.pem ./prometheus/ssl/aeprometheus_server_cert.pem ${namespace}
./install-tls.sh tls.grafana ./grafana/ssl/grafana_server_key.pem ./grafana/ssl/grafana_server_cert.pem ${namespace}

anmt "sleeping for 10 seconds before checking Redis"
sleep 10

anmt "checking restored ticker pricing data in Redis:"
./view-ticker-data-in-redis.sh

anmt "starting monitoring"
./monitor-start.sh

anmt "sleeping for 10 seconds before checking pods"
sleep 10

anmt "getting kubernetes ae pods:"
kubectl get pods -n ${namespace}

cd ${cur_dir}

echo ""
good "done starting up ae"

exit 0
