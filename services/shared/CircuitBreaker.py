import datetime as dt
import sys

class CircuitOpenError(Exception):
    def __init__(self, value = ""):
        self.value = value
    def __str__(self):
        return repr(self.value)

class CircuitBreaker(object):
    # Circuit states
    CLOSED = "closed"
    OPEN = "open"
    HALFOPEN = "halfopen"

    # Circuit events
    
    def __init__(self, name, fail_max, reset_timeout):
        print "initializing circuit!"
        self.state = self.CLOSED
        self.tries = 0
        self.name = name
        self.fail_max = fail_max
        self.reset_timeout = reset_timeout
        self.reset_timer_start = dt.datetime.now()

    def log(self, msg):
        print "[CircuitBreaker '" + self.name + "'] " + msg

    def reset(self):
        self.log("event: reset")
        if self.state == self.OPEN:
            self.state = self.HALFOPEN; self.log("state: " + self.state)
            self.tries = 0; self.log("tries: " + str(self.tries))

    def success(self):
        self.log("event: success")
        if self.state == self.CLOSED or self.state == self.HALFOPEN :
            self.state = self.CLOSED; self.log("state: " + self.state)
            self.tries = 0; self.log("tries: " + str(self.tries))

    def fail(self):
        self.log("event: fail")
        if self.state == self.CLOSED and self.tries < self.fail_max:
            self.tries += 1; self.log("tries: " + str(self.tries))
        elif self.state == self.CLOSED and self.tries >= self.fail_max:
            self.state = self.OPEN; self.log("state: " + self.state)
        elif self.state == self.HALFOPEN:
            self.state = self.OPEN; self.log("state: " + self.state)

    def call(self, func):
        if self.state == self.CLOSED:
            try:
                res = func()
                self.success()
            except:
                print "Unexpected error:", sys.exc_info()[0]
                self.fail()
                if self.state == self.CLOSED:
                    res = self.call(func) # Calling again
                else:
                    self.reset_timer_start = dt.datetime.now()
                    raise CircuitOpenError()
                    
        elif self.state == self.OPEN:
            print "Reset time is at: " + str((dt.datetime.now() -
                self.reset_timer_start).total_seconds())
            if self.reset_timeout <= (dt.datetime.now() - self.reset_timer_start).total_seconds():
                try:
                    self.reset()
                    res = func()
                    self.success()
                except:
                    self.fail()
                    self.reset_timer_start = dt.datetime.now()
                    raise CircuitOpenError()
            else:
                raise CircuitOpenError()

        elif self.state == self.HALFOPEN:
            try:
                res = func()
                self.success()
            except:
                self.fail()
                self.reset_timer_start = dt.datetime.now()
                raise CircuitOpenError()
        return res
