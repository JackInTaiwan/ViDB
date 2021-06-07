import abc



class BaseResolver(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def encode(self, decoded_msg):
        return NotImplemented


    @abc.abstractmethod
    def dry_decode(self, encoded_msg):
        return NotImplemented


    @abc.abstractmethod
    def decode(self, encoded_msg):
        return NotImplemented
    

    @abc.abstractmethod
    def parse(self):
        return NotImplemented
