from . import register_as_operation
from variable import operation as OP



@register_as_operation(name=OP.INSERT_ONE)
def insert_instance(image_byte):
    # TODO
    # do nothing
    return {
        "success": True,
        "body": {}
    }