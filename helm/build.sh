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

anmt "checking if helm is running already"
helm_running=$(ps auwwx | grep helm | grep serve | wc -l)
if [[ "${helm_running}" == "0" ]]; then
    anmt "initalizing local helm server"
    helm init
    anmt "starting local helm server"
    helm serve &
    echo " - sleeping"
    sleep 5
    helm_running=$(ps auwwx | grep helm | grep serve | wc -l)
    if [[ "${helm_running}" == "0" ]]; then
        echo "failed starting local helm server"
        exit 1
    else
        good "helm is running"
    fi
else
    good " - helm is already serving charts"
fi
echo ""

# Make sure to remove previous and charts to prevent
# duplicated resources on helm install
anmt "cleaning previous builds"
rm -f ae-*.tgz >> /dev/null
rm -f */charts/*.tgz >> /dev/null

anmt "adding ae to local helm repo charts:"
echo "helm repo add local http://localhost:8879/charts"
helm repo add local http://localhost:8879/charts
if [[ "$?" != "0" ]]; then
    err "failed adding ae to helm charts"
    ps awuwx | grep helm
    exit 1
fi

anmt "building ae charts in local/ae"
make
if [[ "$?" != "0" ]]; then
    err "failed building charts with: make"
    exit 1
fi

echo "updating helm repo"
helm repo update
if [[ "$?" != "0" ]]; then
    err "failed updating helm repos"
    ps awuwx | grep helm
    exit 1
fi

good "start ae on kubernetes with: ./start.sh"
