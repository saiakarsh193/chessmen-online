import threading

class sharedMem:
    def __init__(self, data):
        self.data = data
        self.mutex = threading.Lock()

    def lock(self):
        self.mutex.acquire()

    def unlock(self):
        self.mutex.release()
    
    def __str__(self):
        return str(self.data)
