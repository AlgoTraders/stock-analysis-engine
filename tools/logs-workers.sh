#!/bin/bash

container="sa-workers"
echo ""
echo "docker logs -f ${container}"
docker logs -f ${container}
