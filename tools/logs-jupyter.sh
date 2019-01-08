#!/bin/bash

container="ae-jupyter"
echo ""
echo "docker logs -f ${container}"
docker logs -f ${container}
