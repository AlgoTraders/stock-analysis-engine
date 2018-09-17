version: '2'

services:

  # Stock Analysis Engine
  sa-workers:
    container_name: "sa-workers"
    hostname: sa-workers
    image: jayjohnson/stock-analysis-engine:latest
    network_mode: "host"
    environment:
      - SHARED_DIR=/opt/data
      - BROKER_URL=redis://0.0.0.0:6379/4
    volumes:
      - /tmp:/tmp
    entrypoint: "/bin/sh -c 'cd /opt/sa && 
                 /opt/sa/start-workers.sh'"
