#!/bin/bash

container="sa-dataset-collection"
echo ""
echo "docker logs -f ${container}"
docker logs -f ${container}
