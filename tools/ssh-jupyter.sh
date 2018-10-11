#!/bin/bash

container="sa-jupyter-${USER}"
echo ""
echo "docker exec -it ${container} bash"
docker exec -it ${container} bash
