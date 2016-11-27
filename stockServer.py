from werkzeug.exceptions import NotFound
import json
import redis
import threading

r = redis.StrictRedis(host='localhost', port=6379, db=0)

stocks = ["novo",
          "danske bank",
          "william demant",
          "carlsberg",
          "coloplast",
          "dsv",
          "iss",
          "vestas",
          "tdc",
          "pandora"
          ]

def update():
  threading.Timer(5.0, update).start()
  print "Hello, World!"
  
if __name__ == "__main__":
    update()

