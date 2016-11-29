#!/bin/bash
# Trader service
docker service create \
	--network swarm_net \
	--name trader \
	--replicas 1 \
	--publish 5003:5003 \
	sthordall/microtrader:latest \
	python services/trader.py

# Stocks service
docker service create \
	--network swarm_net \
	--name stocks \
	--endpoint-mode dnsrr \
	--replicas 1 \
	sthordall/microtrader:latest \
	python services/stocks.py

# Stocks-DB
docker service create \
	--network swarm_net \
	--name stocks-db \
	--replicas 1 \
	redis:latest

# Account service
docker service create \
	--network swarm_net \
	--name account \
	--endpoint-mode dnsrr \
	--replicas 1 \
	sthordall/microtrader:latest \
	python services/account.py

# Account-DB
docker service create \
	--network swarm_net \
	--name account-db \
	--replicas 1 \
	redis:latest

