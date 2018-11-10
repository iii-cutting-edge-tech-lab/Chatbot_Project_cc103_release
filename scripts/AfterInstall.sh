#!/bin/bash -ex
sudo yum install -y awslogs
sudo sed -i 's/us-east-1/ap-northeast-1/g' /etc/awslogs/awscli.conf
sudo sed -i 's/\/var\/log\/messages/\/home\/ec2-user\/Chatbot_Project_cc103\/Chatbot_Dev_cc103\/code\/my.log/g' /etc/awslogs/awslogs.conf
sudo service awslogs start
cd /home/ec2-user/deploy/Chatbot_Line_cc103/code
aws s3 cp s3://cc103-deploy-certification/secret_key .
cd /home/ec2-user/deploy/Chatbot_Line_cc103/docker_vol/cert-letsencrypt/
aws s3 cp s3://cc103-deploy-certification/cert-letsencrypt/cc103awsbot.crt .
aws s3 cp s3://cc103-deploy-certification/cert-letsencrypt/cc103awsbot.key .
exit 0
