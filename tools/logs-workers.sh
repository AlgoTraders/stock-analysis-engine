#!/bin/bash

container="ae-workers"
echo ""
echo "docker logs -f ${container}"
docker logs -f ${container}
