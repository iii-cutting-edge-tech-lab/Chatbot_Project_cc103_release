#!/bin/bash -ex
touch /home/ec2-user/container_log
touch /home/ec2-user/start_log
sudo docker ps > /home/ec2-user/container_log
containerNum=sudo cat /home/ec2-user/container_log|wc -l
for ((i=0;i<3;i++))
do
  sleep 5
  if [ "$containerNum" == "6"  ]; then
    	echo "deploy success!" > /home/ec2-user/start_log
	break
	exit 0
fi
  if [ "$i" == "2" ]; then
	echo "deploy fail" > /home/ec2-user/start_log
fi
done
exit 0
