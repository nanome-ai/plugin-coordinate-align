#!/bin/bash

parent_path=$( cd "$(dirname "${BASH_SOURCE[0]}")" ; pwd -P )
cd "$parent_path"

container_name='align'

existing=$(docker ps -aq -f name=$container_name)
if [ -n "$existing" ]; then
    echo "removing existing container"
    docker rm -f $existing
fi

# Create redeploy.sh
echo "./deploy.sh $*" > redeploy.sh
chmod +x redeploy.sh

docker run -d \
--name $container_name \
--restart unless-stopped \
-e ARGS="$*" \
$container_name

