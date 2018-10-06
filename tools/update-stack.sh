#!/bin/bash

echo "starting updates"
date -u +"%Y-%m-%d %H:%M:%S"
containers_to_update="sa-workers sa-jupyter"

echo "containers to update: ${containers_to_update}"

for c in ${containers_to_update}; do
    test_run=$(docker ps | grep ${c} | wc -l)
    if [[ "${test_run}" != "0" ]]; then
        echo "updating ${c}"
        docker exec -it ${c} /bin/bash /opt/sa/tools/deploy-new-build.sh
        echo ""
    else
        echo "cannot update: ${c} - it is not running"
    fi
done

date -u +"%Y-%m-%d %H:%M:%S"
echo "done updating images"
