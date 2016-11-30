from services import root_dir, nice_json
from flask import Flask, request
from werkzeug.exceptions import NotFound
import json
import redis
import random
import time

app = Flask(__name__)

r = redis.StrictRedis(host='localhost', port=6379, db=0)

@app.route("/stock/<stockName>", methods=['PUT'])
def stock_update(stockName):
    sleep_duration = random.randint(0,10)/100.0
    time.sleep(sleep_duration)
    
    price = request.get_json(force=True)['price']
    r.set("stocks:" + stockName, price)
    return nice_json({
        "success": True
    })

@app.route("/stock/<stockName>", methods=['GET'])
def stock_quote(stockName):
    sleep_duration = random.randint(0,10)/100.0
    time.sleep(sleep_duration)

    quote = r.get("stocks:" + stockName)
    return nice_json({
        "quote": quote
    })
    
if __name__ == "__main__":
    app.run(port=5002, host="localhost", debug=True, threaded=True)

