#!/bin/bash
ab -n 10000 -c 100 -T application/json -u data.json http://127.0.0.1:5003/
