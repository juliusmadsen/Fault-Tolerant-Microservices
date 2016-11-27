#!/bin/bash
MANAGER=3
WORKER=5

echo "Creating Docker hosts, $MANAGER managers and $WORKER workers..."
for i in $(seq 1 $MANAGER)
do 
	echo "	-> creating manager$i"
	docker-machine create --driver virtualbox manager$i >> /dev/null
done
for i in $(seq 1 $WORKER)
do
	echo "	-> creating worker$i"
	docker-machine create --driver virtualbox worker$i >> /dev/null
done
echo

echo "Initializing swarm on manager1..."
docker-machine ssh manager1 docker swarm init --auto-accept manager --auto-accept worker --listen-addr $(docker-machine ip manager1):2377 >> /dev/null
echo

echo "Adding additional managers to swarm..."
for i in $(seq 2 $MANAGER)
do 
	echo "	-> manager$i joining"
	docker-machine ssh manager$i docker swarm join --manager --listen-addr $(docker-machine ip manager$i):2377 $(docker-machine ip manager1):2377
done

for i in $(seq 1 $WORKER)
do
	echo "	-> worker$i joining"
	docker-machine ssh worker$i docker swarm join --listen-addr $(docker-machine ip worker$i):2377 $(docker-machine ip manager1):2377
done

echo "Done!"
