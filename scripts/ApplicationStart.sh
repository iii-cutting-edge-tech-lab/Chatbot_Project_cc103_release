#!/bin/bash -ex
cd /home/ec2-user/deploy
echo "Running service container "
docker-compose up -d
exit 0
