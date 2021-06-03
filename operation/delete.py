import logging

from . import register_as_operation
from variable import operation as OP

logger = logging.getLogger(__name__)



@register_as_operation(name=OP.DELETE_ONE_BY_ID)
def delete_one_by_id(body=None, storage_engine=None):
    target_index = body["target_index"]

    try:
        result = storage_engine.delete_one(target_index)

        if result:
            return {
                "success": True,
                "body": {}
            }
        else:
            return {
                "success": False,
                "body": {}
            }

    except Exception as e:
        logger.error(e)

        return {
            "success": False,
            "body": {}
        }


@register_as_operation(name=OP.DELETE_MANY_BY_IDS)
def delete_many_by_ids(body=None, storage_engine=None):
    target_index_list = body["target_index_list"]

    try:
        result = storage_engine.delete_many(target_index_list)

        if result:
            return {
                "success": True,
                "body": {}
            }
        else:
            return {
                "success": False,
                "body": {}
            }

    except Exception as e:
        logger.error(e)

        return {
            "success": False,
            "body": {}
        }
