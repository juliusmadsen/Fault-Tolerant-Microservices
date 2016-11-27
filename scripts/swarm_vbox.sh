#!/bin/bash
MANAGER=2
NODE=2

echo "Creating initial Docker host..."
docker-machine create -d virtualbox local >> /dev/null
eval "$(docker-machine env local)"
echo "Creating swarm on initial Docker host..."
SWARM_CLUSTER_TOKEN=$(docker run swarm create)
echo

echo "Creating Docker hosts, $MANAGER managers and $NODE nodes..."
for i in $(seq 1 $MANAGER)
do 
	echo "	-> creating manager$i"
	docker-machine create \
    -d virtualbox \
    --swarm \
    --swarm-master \
    --swarm-discovery token://$SWARM_CLUSTER_TOKEN \
    manager$i >> /dev/null
done
for i in $(seq 1 $NODE)
do
	echo "	-> creating node$i"
	docker-machine create \
    -d virtualbox \
    --swarm \
    --swarm-discovery token://$SWARM_CLUSTER_TOKEN \
    node$i >> /dev/null
done
echo

echo "Done!"
echo 'Run following to connect to Swarm: eval "$(docker-machine env --swarm manager1)"'
