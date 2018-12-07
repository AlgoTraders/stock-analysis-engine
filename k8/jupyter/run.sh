#!/bin/bash

# the current kubernetes cluster installs AntiNex Jupyter
# so remove it if exists already
antinex_deployment_name="jupyter"
found_antinex_jupyter=$(kubectl get deployment | grep jupyter | grep -v sa-jupyter)
if [[ "${found_antinex_jupyter}" ]]; then
    podname="jupyter"
    deployment_name="jupyter"
    kubectl delete deployment ${deployment_name}

    not_done=$(/usr/bin/kubectl get po | grep ${podname} | wc -l)
    while [[ "${not_done}" != "0" ]]; do
        date -u +"%Y-%m-%d %H:%M:%S"
        echo "sleeping while waiting for ${podname} to stop"
        sleep 5
        /usr/bin/kubectl get po | grep ${podname}
        not_done=$(/usr/bin/kubectl get po | grep ${podname} | wc -l)
    done

    not_done=$(/usr/bin/kubectl get po | grep ${podname} | grep "Running" | wc -l)
    while [[ "${not_done}" == "0" ]]; do
        date -u +"%Y-%m-%d %H:%M:%S"
        echo "sleeping while waiting for ${podname} to start"
        sleep 5
        /usr/bin/kubectl get po | grep ${podname}
        not_done=$(/usr/bin/kubectl get po | grep ${podname} | grep "Running" | wc -l)
    done

    echo "done removing previous jupyter deployment"
fi

echo "jupyter on kubernetes deployment starting"

if [[ -e ./k8/jupyter/secrets.yml ]]; then
    echo "applying secrets"
    kubectl apply -f k8/jupyter/secrets.yml
fi

if [[ -e ./k8/jupyter/service.yml ]]; then
    echo "applying service"
    kubectl apply -f k8/jupyter/service.yml
fi

if [[ -e ./k8/jupyter/ingress.yml ]]; then
    echo "applying ingress"
    kubectl apply -f k8/jupyter/ingress.yml
fi

if [[ -e ./k8/jupyter/deployment.yml ]]; then
    echo "applying jupyter"
    kubectl apply -f k8/jupyter/deployment.yml
fi

echo "checking deployment"
kubectl get deployment
echo ""

echo "checking pods"
kubectl get deployment
echo ""

echo "jupyter on kubernetes deployment done"

exit 0
