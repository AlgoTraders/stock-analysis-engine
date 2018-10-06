#!/bin/bash

container="sa-jupyter"
echo ""
echo "docker logs -f ${container}"
docker logs -f ${container}
