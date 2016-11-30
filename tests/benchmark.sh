#!/bin/bash
SERVICE_HOST=$(docker-machine ip manager-1)
RESULT_FILE=results

function putJson {
	URL=$1
	JSON=$2
	curl -H 'Content-Type: application/json' \
			 -H 'Accept: application/json' \
			 -X PUT \
			 -d "$JSON" \
			 $URL
}

echo "Putting test data to account service..."
putJson $SERVICE_HOST/account/1 '{"amount": 99999999999 }'
echo

echo "Putting test data to account service..."
putJson $SERVICE_HOST/stock/novo '{"price": 1 }'
echo

ftsetups=(
	'{ "request_timeout": 0.5, "max_connections": 100, "circuit_maxfail": 5, "circuit_timeout": 1 }'
	'{ "request_timeout": 0.6, "max_connections": 100, "circuit_maxfail": 5, "circuit_timeout": 1 }'
	'{ "request_timeout": 0.7, "max_connections": 100, "circuit_maxfail": 5, "circuit_timeout": 1 }'
	'{ "request_timeout": 0.8, "max_connections": 100, "circuit_maxfail": 5, "circuit_timeout": 1 }'
	'{ "request_timeout": 0.9, "max_connections": 100, "circuit_maxfail": 5, "circuit_timeout": 1 }'
)

echo > $RESULT_FILE
for setup in "${ftsetups[@]}"
do
	echo "Load new fault tolerant setup..."
	echo "$setup" >> $RESULT_FILE
	putJson $SERVICE_HOST/trade/setup "$setup"
	echo
	
	echo "Benchmarking..."
	ab -n 100 -c 10 -T application/json -u data.json $SERVICE_HOST/trade/ \
	| grep -E 'Complete|Failed|Time taken|Time per' >> $RESULT_FILE
	echo "Benchmarking done."
	echo
	echo >> $RESULT_FILE
done

echo "Results stored in file: $RESULT_FILE"

