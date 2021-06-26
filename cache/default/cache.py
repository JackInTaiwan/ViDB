import os
import time



class Cache:
    def __init__(self):
        self.cache = {
            "browse_by_cluster": self.set_parameters(["num_inst"])
        }
        self.new_insert = False

    
    def set_parameters(self, paraList):
        cache = {}
        for p in paraList:
            cache[p]=None
        cache["update_time"] = -1
        cache["result"] = None
        return cache


    def checkupdateByCommand(self, operation, command):
        for k in command.keys():
            if self.cache[operation][k] != command[k]:
                return True
        return False


    def checkInsert(self):
        return self.new_insert


    def checkupdateByTime(self, operation, query_t):
        buffer_time = os.getenv("cache.{}.buffer_time".format(operation))
        if query_t - self.cache[operation]["update_time"] > int(buffer_time):
            return True
        
        return False


    def update(self, operation, result):
        if result != None:
            self.cache[operation]["result"] = result
            self.cache[operation]["update_time"] = time.time()
        self.new_insert = False


    def getCacheContent(self, operation):
        return self.cache[operation]["result"]


    def InsertUpdate(self):
        self.new_insert = True
    