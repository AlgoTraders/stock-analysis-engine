#!/bin/bash

container="ae-jupyter"
echo ""
echo "docker exec -it ${container} bash"
docker exec -it ${container} bash
