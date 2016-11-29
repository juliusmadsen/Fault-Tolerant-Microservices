from services import root_dir, nice_json
from flask import Flask, request
from werkzeug.exceptions import NotFound
from shared.CircuitBreaker import CircuitBreaker
import json
import requests
import threading

app = Flask(__name__)

max_connections = 5

account_sema = threading.BoundedSemaphore(value=max_connections)
account_circuit = CircuitBreaker("account", 2, 1)

stock_sema = threading.BoundedSemaphore(value=max_connections)

def getAccount(accountId):
    account_sema.acquire()
    res = account_circuit.call(lambda:
                               requests.get("http://localhost:5001/account/" + str(accountId),
                                            timeout=0.9))
    account_sema.release()
    return res.json()

def getStock(stockName):
    stock_sema.acquire()
    res = account_circuit.call(lambda:
                               requests.get("http://localhost:5002/stock/" + str(stockName),
                                            timeout=0.9))
    stock_sema.release()
    return res.json()

def updateAccount(accountId, amount, stockName, stockAmount):
    payload = { "amount": amount, "stock": {"name": stockName, "amount": stockAmount} }
    account_sema.acquire()
    res = account_circuit.call(lambda:
                               requests.put("http://localhost:5001/account/" + str(accountId),
                                            timeout=0.9,
                                            json=payload))
    account_sema.release()
    return res.json()

@app.route("/", methods=['PUT'])
def stock_update():
    global account_sema
    global stock_sema
    
    req = request.get_json(force=True)
    
    accountId = req['accountId']
    stockName = req['stockName']
    amount = int(req['amount'])

    accountData = getAccount(accountId)
    balance = int(accountData['balance'])
    stockHolding = 0
    if 'stocks:' + stockName in accountData:
        stockHolding = int(accountData['stocks:' + stockName])

    stockData = getStock(stockName)
    quote = int(stockData['quote'])

    if amount > 0 and balance < amount*quote:
        res = {'success': False, 'message': "Not enough funds to buy."}
    elif amount < 0 and stockHolding < amount*-1:
        res = {'success': False, 'message': "Not enough shares owned to sell."}
    else:
        payload = { "amount": -1*amount*quote, "stock": {"name": stockName, "amount": amount} }
        res = updateAccount(accountId, -1*amount*quote, stockName, amount)
    
    return nice_json(res)

if __name__ == "__main__":
    app.run(port=5003, debug=True, threaded=True)

