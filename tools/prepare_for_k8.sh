#!/bin/bash

# set for anonymous user access in the container
echo "setting container directory permissions"
find /opt/venv -type d -exec chmod 777 {} \;
find /opt/spylunking -type d -exec chmod 777 {} \;
find /opt/sa -type d -exec chmod 777 {} \;
find /var/log -type d -exec chmod 777 {} \;
find /opt/notebooks -type d -exec chmod 777 {} \;

exit 0
