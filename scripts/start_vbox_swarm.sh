#!/bin/bash
MANAGERS=2
WORKERS=2

echo "Starting $TOTALINSTANCES instances in virtualbox:"

# Creating instances for managers
for n in $(seq 1 $MANAGERS)
do
	echo " Starting manager-$n in virtualbox..."
	docker-machine create --driver "virtualbox" "manager-$n" >> /dev/null
done

for n in $(seq 1 $WORKERS)
do
	echo " Starting worker-$n in virtualbox..."
	docker-machine create --driver "virtualbox" "worker-$n" >> /dev/null
done

echo "Initializing swarm on manager-1..."
eval $(docker-machine env manager-1)
MANAGER_1_IP=$(docker-machine ip manager-1)
docker swarm init --advertise-addr $MANAGER_1_IP >> /dev/null
MANAGER_TOKEN=$(docker swarm join-token manager -q)
WORKER_TOKEN=$(docker swarm join-token worker -q)

for n in $(seq 2 $MANAGERS)
do
	echo " Joining manager-$n to swarm..."
	eval $(docker-machine env manager-$n)
	docker swarm join \
	 	--token $MANAGER_TOKEN \
	 	$MANAGER_1_IP:2377 >> /dev/null
done

for n in $(seq 1 $WORKERS)
do
	echo " Joining worker-$n to swarm..."
	eval $(docker-machine env worker-$n)
	docker swarm join \
	 	--token $WORKER_TOKEN \
	 	$MANAGER_1_IP:2377 >> /dev/null
done

echo "Creating overlay network swarm_net.."
eval $(docker-machine env manager-1)
docker network create --driver overlay swarm_net >> /dev/null

export DOCKER_HOST=$MANAGER_1_IP:2377

