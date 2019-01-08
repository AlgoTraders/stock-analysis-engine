#!/bin/bash

container="ae-workers"
echo ""
echo "docker exec -it ${container} bash"
docker exec -it ${container} bash
