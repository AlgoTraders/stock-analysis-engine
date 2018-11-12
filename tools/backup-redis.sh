#!/bin/bash

redis-cli save
docker cp redis-${USER}:/data/dump.rdb /opt/sa/tests/datasets/redis/redis-0-backup-$(date +"%Y-%m-%d").rdb

ls -hlrt /opt/sa/tests/datasets/redis/redis-0-backup-*.rdb | tail -1
