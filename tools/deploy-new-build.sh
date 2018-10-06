#!/bin/bash

if [[ -e /opt/venv/bin/activate ]]; then
    source /opt/venv/bin/activate
fi

use_fork="0"
remote_uri="https://github.com/AlgoTraders/stock-analysis-engine.git"
remote_name="upstream"
remote_branch="master"

# deploy your own fork with command:
# ./tools/deploy-new-build.sh <git fork uri> <optional - branch name (master by default)> <optional - fork repo name>
# ./tools/deploy-new-build.sh git@github.com:jay-johnson/stock-analysis-engine.git timeseries-charts jay
if [[ "${1}" != "" ]]; then
    use_fork="1"
    remote_uri="${1}"
    if [[ "${2}" != "" ]]; then
        remote_branch="${2}"
    fi
    if [[ "${3}" != "" ]]; then
        remote_name="${3}"
    else
        remote_name="myfork"
    fi
    echo "deploying new build from remote: ${remote_name} repo: ${remote_uri} branch: ${remote_branch}"
else
    echo "deploying new build"
fi

echo ""
echo "python version:"
which python

echo "updating pip"
pip install --upgrade pip

repos="/opt/sa"
echo "updating: ${repos}"
for d in ${repos}; do
    rm -rf ${d}
    git clone ${remote_uri} ${d}
    cd ${d}
    git checkout ${remote_branch}
    echo "installing latest"
    pip install --upgrade -e .
done

echo ""
echo "checking pip versions:"
pip list --format=columns

echo ""
echo "done"
