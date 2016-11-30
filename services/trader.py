from services import root_dir, nice_json, error_response
from flask import Flask, request
from werkzeug.exceptions import NotFound
from shared.CircuitBreaker import CircuitBreaker
import json
import requests
import threading

app = Flask(__name__)

request_timeout = 0.11
max_connections = 100
circuit_maxfail = 3
circuit_timeout = 1

account_sema = threading.BoundedSemaphore(value=max_connections)
account_circuit = CircuitBreaker("account", circuit_maxfail, circuit_timeout)

stock_sema = threading.BoundedSemaphore(value=max_connections)
stock_circuit = CircuitBreaker("stock", circuit_maxfail, circuit_timeout)

def getAccount(accountId):
    global account_sema
    global account_circuit
    global request_timeout
    
    account_sema.acquire()
    res = account_circuit.call(lambda:
                               requests.get("http://account:5001/account/" + str(accountId),
                                            timeout=request_timeout))
    account_sema.release()
    return res.json()

def getStock(stockName):
    global stock_sema
    global stock_circuit
    global request_timeout
    
    stock_sema.acquire()
    res = stock_circuit.call(lambda:
                             requests.get("http://stocks:5002/stock/" + str(stockName),
                                          timeout=request_timeout))
    stock_sema.release()
    return res.json()

def updateAccount(accountId, amount, stockName, stockAmount):
    global account_sema
    global account_circuit
    global request_timeout
    
    payload = { "amount": amount, "stock": {"name": stockName, "amount": stockAmount} }
    account_sema.acquire()
    res = account_circuit.call(lambda:
                               requests.put("http://account:5001/account/" + str(accountId),
                                            timeout=request_timeout,
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

    try:
        accountData = getAccount(accountId)
    except:
        account_sema.release()
        return error_response("account service")
        
    balance = int(accountData['balance'])
    stockHolding = 0
    if 'stocks:' + stockName in accountData:
        stockHolding = int(accountData['stocks:' + stockName])

    try:
        stockData = getStock(stockName)
    except:
        stock_sema.release()
        return error_response("stock service")

    quote = int(stockData['quote'])

    if amount > 0 and balance < amount*quote:
        res = {'success': False, 'message': "Not enough funds to buy."}
    elif amount < 0 and stockHolding < amount*-1:
        res = {'success': False, 'message': "Not enough shares owned to sell."}
    else:
        payload = { "amount": -1*amount*quote, "stock": {"name": stockName, "amount": amount} }
        try:
            res = updateAccount(accountId, -1*amount*quote, stockName, amount)
        except:
            account_sema.release()
            return error_response("account service")

    
    return nice_json(res)

@app.route("/setup", methods=['GET'])
def setup_get():
    global request_timeout
    global max_connections
    global circuit_maxfail
    global circuit_timeout

    res = { "request_timeout": request_timeout,
            "max_connections": max_connections,
            "circuit_maxfail": circuit_maxfail,
            "circuit_timeout": circuit_timeout }

    return nice_json(res)

@app.route("/setup", methods=['PUT'])
def setup_update():
    try:
        req = request.get_json(force=True)

        global request_timeout
        global max_connections
        global circuit_maxfail
        global circuit_timeout

        request_timeout = req["request_timeout"]
        max_connections = req["max_connections"]
        circuit_maxfail = req["circuit_maxfail"]
        circuit_timeout = req["circuit_timeout"]

        global account_sema
        global account_circuit
        global stock_sema
        global stock_circuit

        account_sema = threading.BoundedSemaphore(value=max_connections)
        account_circuit = CircuitBreaker("account", circuit_maxfail, circuit_timeout)

        stock_sema = threading.BoundedSemaphore(value=max_connections)
        stock_circuit = CircuitBreaker("stock", circuit_maxfail, circuit_timeout)

        res = { "request_timeout": request_timeout,
                "max_connections": max_connections,
                "circuit_maxfail": circuit_maxfail,
                "circuit_timeout": circuit_timeout }
    except:
        return error_response("Setup update failed")

    return nice_json(res)

if __name__ == "__main__":
    app.run(port=5003, host="0.0.0.0", debug=True, threaded=True)

