import abc
import json



class BaseStorageEngine(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def init_storage(self):
        return NotImplemented


    @abc.abstractmethod
    def create_one(self, image:str, thumbnail:str, features, metadata:json):
        return NotImplemented


    @abc.abstractmethod
    def create_many(self, image:list, thumbnail:list, features:list, metadata:list):
        return NotImplemented


    @abc.abstractmethod
    def read_one(self, index, mode):
        return NotImplemented


    @abc.abstractmethod
    def read_many(self, index:list, mode):
        return NotImplemented


    @abc.abstractmethod
    def delete_one(self, index): 
        return NotImplemented


    @abc.abstractmethod
    def delete_many(self, index:list): # TBD: how to relocate files
        return NotImplemented


    @abc.abstractmethod
    def update_one(self, index, metadata):
        return NotImplemented
    

    @abc.abstractmethod
    def update_many(self, index, metadata):
        return NotImplemented


    @abc.abstractmethod
    def generate_id(self):
        return NotImplemented


    @abc.abstractmethod
    def generate_c_at(self): # create time
        return NotImplemented


    @abc.abstractmethod
    def storage_reconstruct(self): # TBD: how to relocate files
        return NotImplemented


    @abc.abstractmethod
    def locate_id(self, index): # TBD: how to relocate files
        return NotImplemented
