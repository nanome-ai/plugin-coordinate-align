#!/bin/bash

parent_path=$( cd "$(dirname "${BASH_SOURCE[0]}")" ; pwd -P )
cd "$parent_path"

# Create redeploy.sh
echo "./deploy.sh $*" > redeploy.sh
chmod +x redeploy.sh

docker run -d \
--name align \
--restart unless-stopped \
-e ARGS="$*" \
align

