#!/bin/bash

if [[ -e /opt/venv/bin/activate ]]; then
    source /opt/venv/bin/activate
fi

use_fork="0"
remote_uri=""
remote_name=""
remote_branch="master"

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
    cd ${d}
    echo ""
    echo "pulling latest: ${d} origin master"
    git pull origin master
    echo ""
    if [[ "${use_fork}" == "1" ]]; then
        has_fork=$(cat ${d}/.git/config | grep ${remote_uri} | wc -l)
        if [[ "${has_fork}" == "0" ]]; then
            echo "adding remote:"
            echo "git remote add ${remote_name} ${remote_uri}"
            git remote add ${remote_name} ${remote_uri}
        fi
        echo "fetching: ${remote_name}"
        echo "git fetch ${remote_name}"
        git fetch ${remote_name}
        echo ""
        echo "checking out: ${remote_name} ${remote_branch}"
        git checkout ${remote_branch}
        echo ""
        echo "checking git status"
        git status
        echo ""
        echo "pulling: ${remote_name} ${remote_branch}"
        git pull ${remote_name} ${remote_branch}
        echo ""
        echo "checking git status"
        git status
    fi
    echo "installing latest"
    pip install --upgrade -e .
done

echo ""
echo "checking pip versions:"
pip list --format=columns

echo ""
echo "done"
