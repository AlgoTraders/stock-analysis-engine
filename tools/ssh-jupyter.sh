#!/bin/bash

container="sa-jupyter"
echo ""
echo "docker exec -it ${container} bash"
docker exec -it ${container} bash
