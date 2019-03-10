#!/bin/bash

if [[ "${KUBECONFIG}" == "" ]]; then
    export KUBECONFIG=/opt/k8/config
fi

namespace="default"
use_repo_path="/opt/sa"
use_venv="/opt/venv"

if [[ "${1}" != "" ]]; then
    namespace="${1}"
fi
if [[ "${2}" != "" ]]; then
    use_repo_path="${2}"
fi

source ${use_repo_path}/analysis_engine/scripts/common_bash.sh
source ${use_repo_path}/analysis_engine/scripts/k8_env.sh

s3_bucket="YOUR_BACKUP_BUCKET_NAME"
engine_container="ae-workers"
ae_k8_pod_engine="ae-engine"
ae_k8_secrets="${use_repo_path}/k8/secrets/secrets.yml"
ae_k8_file_engine="${use_repo_path}/k8/engine/deployment.yml"
ae_k8_importer="${use_repo_path}/analysis_engine/scripts/sa.py"
ae_k8_ns_secrets="${use_repo_path}/k8/secrets/${namespace}-secrets.yml"
ae_k8_s3_keys_file="${use_repo_path}/k8/env/s3_keys"

cur_date=$(date)
anmt "-------------------------------------------"
anmt "${cur_date} - starting AE deployment and auto-deploy S3 backups to Redis (in k8 and docker)"
anmt "${cur_date} - KUBECONFIG=${KUBECONFIG}"
echo ""

if [[ -e ${ae_k8_ns_secrets} ]]; then
    anmt "applying ns secrets: ${ae_k8_ns_secrets}"
    kubectl -n ${namespace} apply -f ${ae_k8_ns_secrets}
else
    inf "- did not find optional namespace secrets file: ${ae_k8_ns_secrets}"
    inf "using default secrets: ${ae_k8_secrets}"
    kubectl -n ${namespace} apply -f ${ae_k8_secrets}
fi

load_s3_env_keys() {
    if [[ -e ${ae_k8_s3_keys_file} ]]; then
        inf "loading S3 keys: source ${ae_k8_s3_keys_file}"
        source ${ae_k8_s3_keys_file}
    elif [[ -e ${S3_KEYS_FILE} ]]; then
        inf "loading S3 file: source ${S3_KEYS_FILE}"
        source ${S3_KEYS_FILE}
    else
        err "---------------------------------------------------------------------"
        err "Missing S3 Keys file for auto-deploying backed up data in S3 to Redis"
        err "please set your S3 Access and Secret key in ${ae_k8_s3_keys_file} or in an export S3_KEYS_FILE=<path to file with keys>"
        anmt "The S3 Keys file should have the following contents:"
        echo ""
        echo "export S3_ACCESS_KEY=ACCESS_KEY"
        echo "export S3_SECRET_KEY=SECRET_KEY"
        echo "export S3_BUCKET=BUCKET_NAME"
        echo "export S3_REGION_NAME=REGION_NAME"
        echo "export S3_ADDRESS=s3.REGION_NAME.amazonaws.com"
        echo "export AWS_ACCESS_KEY_ID=\${S3_ACCESS_KEY}"
        echo "export AWS_SECRET_ACCESS_KEY=\${S3_SECRET_KEY}"
        echo ""
        err "---------------------------------------------------------------------"
    fi
}

container_running=$(docker ps | grep ${engine_container} | wc -l)

if [[ "${container_running}" == "0" ]]; then
    cd ${use_repo_path}
    pwd
    anmt "starting redis and minio"
    ./compose/start.sh -a
    anmt "starting stack"
    ./compose/start.sh -s
    container_running=$(docker ps | grep ${engine_container} | wc -l)
else
    good "docker stack already running"
fi

pod_name=$(kubectl -n ${namespace} get po | grep ae-engine | grep Running |tail -1 | awk '{print $1}')
if [[ "${pod_name}" == "" ]]; then
    anmt "restarting engine: ${ae_k8_file_engine}"
    k8_restart_pod ${ae_k8_pod_engine} ${ae_k8_file_engine}
    pod_name=$(kubectl -n ${namespace} get po | grep ae-engine | grep Running |tail -1 | awk '{print $1}')
fi
anmt "found kubernetes engine pod: ${pod_name}"

cd ${use_repo_path}
anmt "Deploying Jupyter: ./k8/jupyter/run.sh ceph dev"
anmt "Deploying Jupyter: ./k8/jupyter/run.sh ceph dev"
./k8/jupyter/run.sh ceph dev

load_s3_env_keys

anmt "Getting latest date keys with: aws s3 ls s3://${s3_bucket} | grep archive | grep -o '.\{15\}$' | sort | uniq | tail -1 | sed -e 's/\.json//g'"
anmt "Getting latest date keys with: aws s3 ls s3://${s3_bucket} | grep archive | grep -o '.\{15\}$' | sort | uniq | tail -1 | sed -e 's/\.json//g'"
latest_date=$(aws s3 ls s3://${s3_bucket} | grep archive | grep -o '.\{15\}$' | sort | uniq | tail -1 | sed -e 's/\.json//g')
anmt "found latest date: ${latest_date}"
use_date=${latest_date}
anmt "Getting latest keys for date=${use_date} in S3 with: aws s3 ls s3://${s3_bucket} | grep 'archive_' | grep ${use_date} | awk '{print $NF}'"
anmt "Getting latest keys for date=${use_date} in S3 with: aws s3 ls s3://${s3_bucket} | grep 'archive_' | grep ${use_date} | awk '{print $NF}'"
latest_keys=$(aws s3 ls s3://${s3_bucket} | grep 'archive_' | grep ${use_date} | awk '{print $NF}')

today_date=$(date +"%Y-%m-%d")
path_to_backup_dir="/data2/ae/backup_${today_date}"
mkdir -p -m 777 ${path_to_backup_dir}
anmt "using backup dir: ${path_to_backup_dir}"
cd ${path_to_backup_dir}

for key in ${latest_keys}; do
    if [[ ! -e ${key} ]]; then
        anmt "downloading ${s3_bucket}/${key} to ${path_to_backup_dir}"
        s3cmd get s3://${s3_bucket}/${key}
    else
        inf " - already have ${s3_bucket}/${key} in ${path_to_backup_dir}"
    fi
    use_key_file=${path_to_backup_dir}/${key}
    if [[ -e ${use_key_file} ]]; then
        ticker=$(ls ${use_key_file} | sed -e 's/archive_/ /g' | sed -e 's/\.json/ /g' | sed -e "s/-${use_date}//g" | awk '{print $NF}')
        inf "deploying ${ticker} to k8 - ${use_key_file} to ${pod_name}:/tmp"
        /usr/bin/kubectl -n ${namespace} cp ${use_key_file} ${pod_name}:/tmp
        anmt "importing ${ticker} dataset with: /usr/bin/kubectl -n ${namespace} exec ${pod_name} -- ${use_venv}/bin/python ${ae_k8_importer} -m 0 -t ${ticker} -L /tmp/${key}"
        /usr/bin/kubectl -n ${namespace} exec ${pod_name} -- ${use_venv}/bin/python ${ae_k8_importer} -m 0 -t ${ticker} -L /tmp/${key}
        if [[ "${container_running}" == "1" ]]; then
            anmt "deploying to ${ticker} docker - ${use_key_file} to ${engine_container}:/tmp"
            docker cp ${use_key_file} ${engine_container}:/tmp
            docker exec -it ${engine_container} ${use_venv}/bin/python ${ae_k8_importer} -m 0 -t ${ticker} -L /tmp/${key}
        else
            err "docker not running"
        fi
    else
        err "Failed to download: ${key} to ${use_key_file}"
    fi
done

cur_date=$(date)
anmt "${cur_date} - Getting docker containers:"
docker ps

cur_date=$(date)
anmt "${cur_date} - Getting k8 pods:"
kubectl -n ${namespace} get po

cur_date=$(date)
anmt "${cur_date} - done deploying AE"
anmt "-------------------------------------------"

exit 0
