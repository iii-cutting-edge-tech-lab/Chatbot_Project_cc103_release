#!/bin/bash -ex
sudo docker ps > /home/ec2-user/container_log
containerNum=sudo cat /home/ec2-user/container_log|wc -l
if [ $containerNum >= 1 ]; then
	echo "stop service container "
	cd /home/ec2-user/deploy
	docker-compose down --rmi all
	exit 0
    else
	echo "nothing to stop"
fi
exit 0
