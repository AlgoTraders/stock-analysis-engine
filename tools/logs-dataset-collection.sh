#!/bin/bash

container="sa-dataset-collection-${USER}"
echo ""
echo "docker logs -f ${container}"
docker logs -f ${container}
