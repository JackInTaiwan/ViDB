from . import register_as_operation
from variable import operation as OP



@register_as_operation(name=OP.INSERT_ONE)
def insert_instance(body=None, storage_engine=None):
    # TODO
    # do nothing
    return {
        "success": True,
        "body": {}
    }