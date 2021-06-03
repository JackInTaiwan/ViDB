import logging

from . import register_as_operation
from variable import operation as OP

logger = logging.getLogger(__name__)



@register_as_operation(name=OP.UPDATE_ONE_BY_ID)
def update_one_by_id(body=None, storage_engine=None):
    target_index, metadata = body["target_index"], body["metadata"]

    try:
        result = storage_engine.update_one(target_index, metadata)

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


@register_as_operation(name=OP.UPDATE_MANY_BY_IDS)
def update_many_by_ids(body=None, storage_engine=None):
    target_index_list, metadata_list = body["target_index_list"], body["metadata_list"]

    try:
        result = storage_engine.update_many(target_index_list, metadata_list)

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
