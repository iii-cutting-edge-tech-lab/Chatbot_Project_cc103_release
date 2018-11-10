#!/bin/bash
echo "Logging in to AWS ECR and pull images"

$(aws ecr get-login --no-include-email --region ap-northeast-1)
docker pull 204065533127.dkr.ecr.ap-northeast-1.amazonaws.com/api:latest
docker pull 204065533127.dkr.ecr.ap-northeast-1.amazonaws.com/jupyter:latest
docker pull 204065533127.dkr.ecr.ap-northeast-1.amazonaws.com/ngrok:latest
docker pull mysql:latest
docker pull redis:latest
cd /home/ec2-user/deploy/Chatbot_Line_cc103/code
aws s3 cp s3://cc103-deploy-certification/secret_key.txt .
cd /home/ec2-user/deploy/Chatbot_Line_cc103/docker_vol/cert-letsencrypt/
aws s3 cp s3://cc103-deploy-certification/cert-letsencrypt/cc103awsbot.crt .
aws s3 cp s3://cc103-deploy-certification/cert-letsencrypt/cc103awsbot.key .
exit 0
