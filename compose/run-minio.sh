#!/bin/bash


test_exists=$(docker ps | grep minio | wc -l)
if [[ "${test_exists}" == "1" ]]; then
    docker stop minio
    docker rm minio
fi

access_key="trexaccesskey"
secret_key="trex123321"

# probably not ideal but needed for getting it to work on MacOS
# will also need to manually add /data to Docker -> Preferences -> File Sharing
if [[ ! -d "/data" ]]; then
    sudo mkdir -p -m 777 /data
fi

docker run \
    -e "MINIO_ACCESS_KEY=${access_key}" \
    -e "MINIO_SECRET_KEY=${secret_key}" \
    -p 22001:22001 \
    --name minio \
    --network=host \
    -v /data/minio/data:/data \
    -d \
  minio/minio server /data
