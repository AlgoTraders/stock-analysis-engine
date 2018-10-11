#!/bin/bash

container="sa-workers-${USER}"
echo ""
echo "docker exec -it ${container} bash"
docker exec -it ${container} bash
