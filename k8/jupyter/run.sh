#!/bin/bash

# use the bash_colors.sh file
found_colors="./analysis_engine/scripts/common_bash.sh"
if [[ "${DISABLE_COLORS}" == "" ]] && [[ "${found_colors}" != "" ]] && [[ -e ${found_colors} ]]; then
    . ${found_colors}
else
    inf() {
        echo "$@"
    }
    anmt() {
        echo "$@"
    }
    good() {
        echo "$@"
    }
    err() {
        echo "$@"
    }
    critical() {
        echo "$@"
    }
    warn() {
        echo "$@"
    }
fi

should_cleanup_before_startup=0
deploy_suffix=""
cert_env="dev"
for i in "$@"
do
    if [[ "${i}" == "prod" ]]; then
        cert_env="prod"
    elif [[ "${i}" == "splunk" ]]; then
        deploy_suffix="-splunk"
    elif [[ "${i}" == "antinex" ]]; then
        cert_env="an"
    elif [[ "${i}" == "qs" ]]; then
        cert_env="qs"
    elif [[ "${i}" == "redten" ]]; then
        cert_env="redten"
    fi
done

use_path="."
if [[ ! -e deployment.yml ]]; then
    use_path="./k8/jupyter"
fi

anmt "----------------------------------------------------------------------------------"
anmt "deploying jupyter with cert_env=${cert_env}: https://github.com/jay-johnson/deploy-to-kubernetes/blob/master/jupyter"
inf ""

inf "applying secrets"
kubectl apply -f ${use_path}/secrets.yml
inf ""

deploy_file=${use_path}/deployment${deploy_suffix}.yml
warn "applying deployment: ${deploy_file}"
kubectl apply -f ${deploy_file}
inf ""

inf "applying service"
kubectl apply -f ${use_path}/service.yml
inf ""

inf "applying ingress cert_env: ${cert_env}"
kubectl apply -f ${use_path}/ingress-${cert_env}.yml
inf ""

good "done deploying: jupyter"
