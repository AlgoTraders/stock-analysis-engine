#!/bin/bash

container="sa-jupyter-${USER}"
echo ""
echo "docker logs -f ${container}"
docker logs -f ${container}
