#!/bin/bash 
sudo curl -L "https://github.com/docker/compose/releases/download/1.10.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
sudo ln -s /usr/local/bin/docker-compose /usr/bin/docker-compose
sudo yum install -y awslogs
sudo sed -i 's/us-east-1/ap-northeast-1/g' /etc/awslogs/awscli.conf
sudo sed -i 's/\/var\/log\/messages/\/home\/ec2-user\/deploy\/Chatbot_Dev_cc103\/code\/my.log/g' /etc/awslogs/awslogs.conf
sudo service awslogs start
cd /home/ec2-user/deploy/Chatbot_Line_cc103/code
aws s3 cp s3://cc103-deploy-certification/secret_key .
cd /home/ec2-user/deploy/Chatbot_Line_cc103/docker_vol/cert-letsencrypt/
aws s3 cp s3://cc103-deploy-certification/cert-letsencrypt/cc103awsbot.crt .
aws s3 cp s3://cc103-deploy-certification/cert-letsencrypt/cc103awsbot.key .
cd /home/ec2-user/deploy/Chatbot_Dev_cc103/mysql_init
aws s3 cp s3://cc103-deploy-certification/SA .
aws s3 cp s3://cc103-deploy-certification/Develope .
aws s3 cp s3://cc103-deploy-certification/SYS .
cd /home/ec2-user/deploy/Chatbot_Dev_cc103
aws s3 cp s3://cc103-devops/mysql_data/ . --recursive
exit 0


