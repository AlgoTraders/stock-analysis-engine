k8_logs() {
    ae_pod_name="${1}"
    pod_name=$(kubectl get po | grep ${ae_pod_name} | grep Running |tail -1 | awk '{print $1}')
    if [[ "${pod_name}" == "" ]]; then
        kubectl logs ${pod_name}
    else
        echo "did not find ${pod_name} in a Running state"
    fi
}

k8_restart_pod() {
    # ae_k8_pod_engine="sa-engine"
    # ae_k8_file_engine="/opt/sa/k8/engine/deployment.yml"
    # ae_k8_pod_dataset_collector="sa-dataset-collector"
    # ae_k8_file_dataset_collector="/opt/sa/k8/datasets/job.yml"

    ae_pod_name="sa-dataset-collector"
    ae_k8_file="/opt/sa/k8/datasets/job.yml"
    use_kube_config="${KUBECONFIG}"

    if [[ "${1}" != "" ]]; then
        ae_pod_name="${1}"
    fi

    if [[ "${2}" != "" ]]; then
        ae_k8_file="${2}"
    fi

    if [[ "${3}" != "" ]]; then
        if [[ -e ${3} ]]; then
            use_kube_config="${3}"
            export KUBECONFIG=${use_kube_config}
        fi
    fi
    
    echo "Deleting ${ae_pod_name} with ${ae_k8_file}"

    test_exists=$(/usr/bin/kubectl get po | grep "${ae_pod_name}" | awk '{print $1}')
    if [[ "${test_exists}" != "" ]]; then
        echo ""
        echo "deleting previous: ${ae_pod_name}"
        echo "/usr/bin/kubectl delete -f ${ae_k8_file}"
        /usr/bin/kubectl delete -f ${ae_k8_file}
    fi

    not_done=$(/usr/bin/kubectl get po | grep ${ae_pod_name} | wc -l)
    while [[ "${not_done}" != "0" ]]; do
        date -u +"%Y-%m-%d %H:%M:%S"
        echo "sleeping while waiting for ${ae_pod_name} to stop"
        sleep 5
        /usr/bin/kubectl get po | grep ${ae_pod_name}
        not_done=$(/usr/bin/kubectl get po | grep ${ae_pod_name} | wc -l)
    done

    echo ""
    echo "Starting dataset collector: ${ae_k8_file} with ${ae_k8_file}"
    echo "/usr/bin/kubectl apply -f ${ae_k8_file}"
    /usr/bin/kubectl apply -f ${ae_k8_file}

    not_done=$(/usr/bin/kubectl get po | grep ${ae_pod_name} | grep "Running" | wc -l)
    while [[ "${not_done}" == "0" ]]; do
        date -u +"%Y-%m-%d %H:%M:%S"
        echo "sleeping while waiting for ${ae_pod_name} to start"
        sleep 5
        /usr/bin/kubectl get po | grep ${ae_pod_name}
        not_done=$(/usr/bin/kubectl get po | grep ${ae_pod_name} | grep "Running" | wc -l)
    done

    echo "getting logs for: ${ae_pod_name}"

    k8_logs ${ae_pod_name}
}
