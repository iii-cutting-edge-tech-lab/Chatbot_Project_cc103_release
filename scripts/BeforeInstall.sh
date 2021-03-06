#!/bin/bash -ex
echo "Logging in to AWS ECR and pull images"
$(aws ecr get-login --no-include-email --region ap-northeast-1)
docker pull 204065533127.dkr.ecr.ap-northeast-1.amazonaws.com/api:latest
docker pull 204065533127.dkr.ecr.ap-northeast-1.amazonaws.com/jupyter:latest
docker pull mysql:latest
docker pull redis:latest
docker pull nginx:latest
exit 0
