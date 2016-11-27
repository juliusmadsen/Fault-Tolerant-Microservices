from services import root_dir, nice_json
from flask import Flask, request
from werkzeug.exceptions import NotFound
from shared import CircuitBreaker
import json
import requests
import threading

app = Flask(__name__)

max_connections = 5
account_sema = threading.BoundedSemaphore(value=max_connections)

def do_get(path):
    return requests.get(path, timeout=50)

def do_put(path, payload):
    return requests.put(path, timeout=0.9, json=payload)

@app.route("/", methods=['PUT'])
def stock_update():
    global account_sema
    req = request.get_json(force=True)
    
    accountId = req['accountId']
    stockName = req['stockName']
    amount = int(req['amount'])

    try:
        print "Getting semaphore!"
        account_sema.acquire()
        print "WOHOO!! Got it :D"
        accountData = do_get("http://localhost:5001/account/" + str(accountId)).json()
        account_sema.release()
    except ValueError:
        return nice_json({"status": "MEGA FAIL!"})
        
    balance = int(accountData['balance'])
    stockHolding = 0
    if 'stocks:' + stockName in accountData:
        stockHolding = int(accountData['stocks:' + stockName])
    
    quote = int(do_get("http://localhost:5002/stock/" + str(stockName)).json()['quote'])

    if amount > 0 and balance < amount*quote:
        res = {'success': False, 'message': "Not enough funds to buy."}
    elif amount < 0 and stockHolding < amount*-1:
        res = {'success': False, 'message': "Not enough shares owned to sell."}
    else:
        payload = { "amount": -1*amount*quote, "stock": {"name": stockName, "amount": amount} }
        update = do_put("http://localhost:5001/account/" + str(accountId), payload)
        res = update.json()
    
    return nice_json(res)

if __name__ == "__main__":
    app.run(port=5003, debug=True, threaded=True)

