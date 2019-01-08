#!/bin/bash

echo "starting updates"
date -u +"%Y-%m-%d %H:%M:%S"
containers_to_update="ae-workers ae-jupyter"

use_fork="0"
remote_uri="https://github.com/AlgoTraders/stock-analysis-engine.git"
remote_name="upstream"
remote_branch="master"

# deploy your own fork with command:
# ./tools/update-stack.sh <git fork uri> <optional - branch name (master by default)> <optional - fork repo name>
# ./tools/update-stack.sh git@github.com:jay-johnson/stock-analysis-engine.git timeseries-charts jay
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

if [[ ! -e ./compose/start.sh ]]; then
    cd /opt/sa
fi

echo "containers to update: ${containers_to_update}"

for c in ${containers_to_update}; do
    test_run=$(docker ps | grep ${c} | wc -l)
    if [[ "${test_run}" != "0" ]]; then
        if [[ "${use_fork}" == "1" ]]; then
            echo "updating ${c} with fork: ${remote_name} ${remote_branch} ${remote_uri}"
            echo "docker exec -it ${c} /bin/bash /opt/sa/tools/deploy-new-build.sh ${remote_uri} ${remote_branch} ${remote_name}"
            docker exec -it ${c} /bin/bash /opt/sa/tools/deploy-new-build.sh ${remote_uri} ${remote_branch} ${remote_name}
            echo ""
        else
            echo "updating ${c} from ${remote} ${remote_branch} ${remote_uri}"
            docker exec -it ${c} /bin/bash /opt/sa/tools/deploy-new-build.sh
            echo ""
        fi

        container_id=$(docker ps | grep ${c} | awk '{print $1}')
        echo "saving container changes to container: ${c} with id: ${container_id}"
        image_name="jayjohnson/stock-analysis-engine"
        if [[ "${c}" == "ae-jupyter" ]]; then
            image_name="jayjohnson/stock-analysis-jupyter"
        fi
        echo "saving container changes as latest: container: ${c} container id: ${container_id} as image: ${image_name}"
        commit_msg=$(docker commit ${container_id} ${image_name}:latest)
        echo "commit msg: ${commit_msg}"
        image_id=$(echo "${commit_msg}" | sed -e 's/:/ /g' | awk '{print $NF}')
        echo "tagging image from container: ${c} with image id: ${image_id}"
        docker tag ${image_id} ${image_name}:latest

        echo "stopping container: ${c}"
        docker stop ${c}
        echo "removing container: ${c}"
        docker rm ${c}
    else
        echo "cannot update: ${c} - it is not running"
    fi

done

date -u +"%Y-%m-%d %H:%M:%S"
echo "done updating images"

echo ""
echo "Please restart the containers again:"
echo ""
echo "Start integration stack:"
echo "./compose/start.sh -a"
echo ""
echo "Start notebook-integration stack:"
echo "./compose/start.sh -j"

echo ""
echo "Starting jupyter integration by default:"
./compose/start.sh -j
