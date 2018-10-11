docker stop $(docker ps -aq)
docker rm $(docker ps -aq)
docker rmi $(docker images -aq)
docker volume rm $(docker volume ls -q)
unset REDIS_PORT
unset MINIO_PORT
unset JUPYTER_PORT_1
unset JUPYTER_PORT_2
unset JUPYTER_PORT_3
unset JUPYTER_PORT_4
