#!/bin/bash

namespace="ae"
recreate="0"
prometheus="./prometheus/values.yaml"
grafana="./grafana/values.yaml"

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
    elif [[ -e ${1} ]]; then
        ae=${1}
    else
        err "Failed to find ae values file: ${1}"
        exit 1
    fi
fi
if [[ "${2}" != "" ]]; then
    if [[ "${2}" == "-r" ]]; then
        recreate="1"
    elif [[ -e ${2} ]]; then
        ae=${2}
    else
        err "Failed to find ae values file: ${2}"
        exit 1
    fi
fi

test_secret_prom=$(kubectl get secret -n ${namespace} | grep tls.prometheus | wc -l)
test_secret_graf=$(kubectl get secret -n ${namespace} | grep tls.grafana | wc -l)

if [[ "${test_secret_prom}" == "0" ]]; then
    good "installing tls.prometheus secret:"
    ./install-tls.sh tls.prometheus ./prometheus/ssl/aeprometheus_server_key.pem ./prometheus/ssl/aeprometheus_server_cert.pem ${namespace}
fi
if [[ "${test_secret_graf}" == "0" ]]; then
    good "installing tls.grafana secret:"
    ./install-tls.sh tls.grafana ./grafana/ssl/grafana_server_key.pem ./grafana/ssl/grafana_server_cert.pem ${namespace}
fi

test_prometheus=$(helm ls | grep ae-prometheus | wc -l)
test_grafana=$(helm ls | grep ae-grafana | wc -l)

if [[ "${test_prometheus}" == "0" ]]; then
    anmt "installing prometheus"
    good "helm install --name=ae-prometheus stable/prometheus --namespace=${namespace} -f ${prometheus}"
    helm install \
        --name=ae-prometheus \
        stable/prometheus \
        --namespace=${namespace} \
        -f ${prometheus}
else
    if [[ "${recreate}" == "1" ]]; then
        helm delete --purge ae-prometheus
        anmt "sleeping to let cleanup finish"
        sleep 10
        anmt "installing prometheus"
        good "helm install --name=ae-prometheus stable/prometheus --namespace=${namespace} -f ${prometheus}"
        helm install \
            --name=ae-prometheus \
            stable/prometheus \
            --namespace=${namespace} \
            -f ${prometheus}
    else
        good "prometheus is already installed"
    fi
fi

if [[ "${test_grafana}" == "0" ]]; then
    anmt "installing grafana"
    good "helm install --name=ae-grafana local/grafana --namespace=${namespace} -f ${grafana}"
    helm install \
        --name=ae-grafana \
        local/grafana \
        --namespace=${namespace} \
        -f ${grafana}
else
    if [[ "${recreate}" == "1" ]]; then
        helm delete --purge ae-grafana
        anmt "sleeping to let cleanup finish"
        sleep 10
        anmt "installing grafana"
        good "helm install --name=ae-grafana local/grafana --namespace=${namespace} -f ${grafana}"
        helm install \
            --name=ae-grafana \
            local/grafana \
            --namespace=${namespace} \
            -f ${grafana}
    else
        good "grafana is already installed"
    fi
fi
echo ""

anmt "checking running charts:"
helm ls

anmt "getting pods in ${namespace} namespace:"
kubectl get pods -n ${namespace}
