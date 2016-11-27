from services import root_dir, nice_json
from flask import Flask, request
from werkzeug.exceptions import NotFound
import json
import redis

app = Flask(__name__)

r = redis.StrictRedis(host='localhost', port=6379, db=0)
"""
@app.route("/account/<accountId>", methods=['PUT'])
def account_info(accountId):
    amount = r.hget("user:" + accountId, "amount")
    return nice_json({
        "amount": amount
    })
"""
@app.route("/account/<accountId>", methods=['GET', 'PUT'])
def account_info(accountId):
    if request.method == 'PUT':
        amount = request.get_json()['amount']
        newAmount = r.hincrby("user:" + accountId, "amount", amount)
        return nice_json({
            "amount": newAmount
        })
    elif request.method == 'GET':
        amount = r.hget("user:" + accountId, "amount")
        return nice_json({
            "amount": amount
        })

if __name__ == "__main__":
    app.run(port=5001, debug=True)

