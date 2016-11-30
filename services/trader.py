from services import root_dir, nice_json, error_response
from flask import Flask, request
from werkzeug.exceptions import NotFound
from shared.CircuitBreaker import CircuitBreaker
import json
import requests
import threading

app = Flask(__name__)

request_timeout = 0.08

max_connections = 3

account_sema = threading.BoundedSemaphore(value=max_connections)
account_circuit = CircuitBreaker("account", 3, 1)

stock_sema = threading.BoundedSemaphore(value=max_connections)
stock_circuit = CircuitBreaker("stock", 3, 1)

def getAccount(accountId):
    global account_sema
    global account_circuit
    global request_timeout
    
    account_sema.acquire()
    res = account_circuit.call(lambda:
                               requests.get("http://localhost:5001/account/" + str(accountId),
                                            timeout=request_timeout))
    account_sema.release()
    return res.json()

def getStock(stockName):
    global stock_sema
    global stock_circuit
    global request_timeout
    
    stock_sema.acquire()
    res = stock_circuit.call(lambda:
                             requests.get("http://localhost:5002/stock/" + str(stockName),
                                          timeout=request_timeout))
    stock_sema.release()
    return res.json()

def updateAccount(accountId, amount, stockName, stockAmount):
    global account_sema
    global account_circuit
    global request_timeout
    
    payload = { "amount": amount, "stock": {"name": stockName, "amount": stockAmount} }
    account_sema.acquire()
    #res = account_circuit.call(lambda:
    #                           requests.put("http://localhost:5001/account/" + str(accountId),
    #                                        timeout=request_timeout,
    #                                        json=payload))
    res = requests.put("http://localhost:5001/account/" + str(accountId),
                       timeout=request_timeout,
                       json=payload)

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

if __name__ == "__main__":
    app.run(port=5003, debug=True, threaded=True)

