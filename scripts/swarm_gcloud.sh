#!/bin/bash
GCLOUD_PROJECT_ID="ftmsb-148909"
GCLOUD_ZONES=(europe-west1-b europe-west1-c europe-west1-d asia-east1-a asia-east1-b asia-east1-c)
GCLOUD_MACHINE_TYPE="n1-standard-2"
HOSTS=4
SWARM_MASTERS=$(($HOSTS/2))
SWARM_NODES=$(($HOSTS-$SWARM_MANAGERS))

echo "Starting $SWARM_MASTERS swarm masters in google cloud project $GCLOUD_PROJECT_ID:"

function startMaster() {
	n=$1
	token=$2
	ZONE=${GCLOUD_ZONES[n-1]}
	MASTER_NAME="master-$n"
	echo "	Starting $MASTER_NAME in $ZONE..."
	docker-machine create --driver "google" \
		--google-project $GCLOUD_PROJECT_ID \
		--google-zone $ZONE \
		--google-machine-type $GCLOUD_MACHINE_TYPE \
		--swarm \
		--swarm-master \
		--swarm-strategy "spread" \
		--swarm-host "tcp://0.0.0.0:3376" \
		--swarm-discovery token://$token \
		$MASTER_NAME
}

for n in $(seq 1 $SWARM_MASTERS)
do
	if [ $n -eq 1 ]
	then
		# Need token from first master
		ZONE=${GCLOUD_ZONES[n-1]}
		echo "	Starting $MASTER_NAME in $ZONE..."
		docker-machine create --driver "google" \
			--google-project $GCLOUD_PROJECT_ID \
			--google-zone $ZONE \
			--google-machine-type $GCLOUD_MACHINE_TYPE \
			master-1
		eval "$(docker-machine env master_1)"
		SWARM_CLUSTER_TOKEN=$(docker-machine run swarm create)
	else
		startMaster $n $SWARM_CLUSTER_TOKEN&
	fi
done

echo "Starting $SWARM_NODES swarm nodes in google project $GCLOUD_PROJECT_ID:"

function startNode() {
	n=$1
	token=$2
	ZONE=${GCLOUD_ZONES[n-1]}
	NODE_NAME="node-$n"
	echo "	Starting $NODE_NAME in $ZONE..."
	docker-machine create --driver "google" \
		--google-project $GCLOUD_PROJECT_ID \
		--google-zone $ZONE \
		--google-machine-type $GCLOUD_MACHINE_TYPE \
		--swarm \
		--swarm-discovery token://$token \
		--swarm-strategy "spread" \
		$NODE_NAME
}

for n in $(seq 1 $SWARM_NODES)
do
	startNode $n $SWARM_CLUSTER_TOKEN&
done

# Wait for all parallel jobs to finish
while [ 1 ]; do fg 2> /dev/null; [ $? == 1 ] && break; done
