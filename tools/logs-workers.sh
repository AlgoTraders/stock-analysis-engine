#!/bin/bash

container="sa-workers-${USER}"
echo ""
echo "docker logs -f ${container}"
docker logs -f ${container}
