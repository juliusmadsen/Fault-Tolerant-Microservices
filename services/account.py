from services import root_dir, nice_json
from flask import Flask, request
from werkzeug.exceptions import NotFound
import json
import redis
import random
import time

app = Flask(__name__)

r = redis.StrictRedis(host='localhost', port=6379, db=0)

@app.route("/account/<accountId>", methods=['PUT'])
def account_update(accountId):
    sleep_duration = random.randint(0,10)/100.0
    time.sleep(sleep_duration)

    req = request.get_json(force=True)
    res = {"updated": False}
    
    if 'amount' in req:
        amount = req['amount']
        balance = r.hincrby("user:" + accountId, "balance", amount)
        res['balance'] = balance
        res['updated'] = True

    if 'stock' in req:
        stock = req['stock']
        name = stock['name']
        amount = stock['amount']
        stockBalance = r.hincrby("user:" + accountId, "stocks:" + name, amount)
        res['stock'] = {name: stockBalance}
        res['updated'] = True
        
    return nice_json(res)

@app.route("/account/<accountId>", methods=['GET'])
def account_get(accountId):
    sleep_duration = random.randint(0,10)/100.0
    time.sleep(sleep_duration)
    data = r.hgetall("user:" + accountId)
    return nice_json(data)
    
if __name__ == "__main__":
    app.run(port=5001, debug=True, threaded=True)

