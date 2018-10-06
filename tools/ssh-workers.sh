#!/bin/bash

container="sa-workers"
echo ""
echo "docker exec -it ${container} bash"
docker exec -it ${container} bash
