#!/bin/bash

container="ae-dataset-collection"
echo ""
echo "docker logs -f ${container}"
docker logs -f ${container}
