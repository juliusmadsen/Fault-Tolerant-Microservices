from services import root_dir, nice_json
from flask import Flask, request
from werkzeug.exceptions import NotFound
import json
import requests

app = Flask(__name__)

def doGet(path):
    return requests.get(path, timeout=0.9)

def doPut(path, payload):
    return requests.put(path, timeout=0.9, json=payload)

@app.route("/", methods=['PUT'])
def stock_update():
    req = request.get_json(force=True)
    
    accountId = req['accountId']
    stockName = req['stockName']
    amount = int(req['amount'])

    accountData = doGet("http://localhost:5001/account/" + str(accountId)).json()
    balance = int(accountData['balance'])
    stockHolding = 0
    if 'stocks:' + stockName in accountData:
        stockHolding = int(accountData['stocks:' + stockName])
    
    quote = int(doGet("http://localhost:5002/stock/" + str(stockName)).json()['quote'])

    if amount > 0 and balance < amount*quote:
        res = {'success': False, 'message': "Not enough funds to buy."}
    elif amount < 0 and stockHolding < amount*-1:
        res = {'success': False, 'message': "Not enough shares owned to sell."}
    else:
        payload = { "amount": -1*amount*quote, "stock": {"name": stockName, "amount": amount} }
        update = doPut("http://localhost:5001/account/" + str(accountId), payload)
        res = update.json()
    
    return nice_json(res)

if __name__ == "__main__":
    app.run(port=5003, debug=True, threaded=True)

