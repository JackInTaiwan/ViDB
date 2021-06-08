import base64
import logging

from . import register_as_operation
from variable import operation as OP

logger = logging.getLogger(__name__)



@register_as_operation(name=OP.RETRIEVE_ONE)
def retrieve_one(body=None, storage_engine=None):
    try:
        target_index = body["target_index"]
        return_origin_size = body["return_origin_size"] if "return_origin_size" in body.keys() else False

        mode = "metadata|image" if return_origin_size else "metadata|thumbnail"
        image, thumbnail, _, metadata = storage_engine.read_one(target_index, mode)

        image_byte = image if return_origin_size else thumbnail
        image_str = base64.b64encode(image_byte).decode()

        return {
            "success": True,
            "body": {
                target_index: {
                    "image": image_str,
                    "metadata": metadata
                }
            }
        }
    
    except Exception as e:
        logger.error(e)

        return {
            "success": False,
            "body": {}
        }


@register_as_operation(name=OP.RETRIEVE_MANY)
def retrieve_many(body=None, storage_engine=None):
    try:
        target_index_list = body["target_index_list"]
        return_origin_size = body["return_origin_size"] if "return_origin_size" in body.keys() else False

        mode = "metadata|image" if return_origin_size else "metadata|thumbnail"
        image_list, thumbnail_list, _, metadata_list = storage_engine.read_many(target_index_list, mode)

        image_byte = image_list if return_origin_size else thumbnail_list
        image_str_list = map(lambda x: base64.b64encode(x).decode(), image_byte)

        output = dict()
        for index, image_str, metadata in zip(target_index_list, image_str_list, metadata_list):
            output[index] = {
                "image": image_str,
                "metadata": metadata
            }

        return {
            "success": True,
            "body": output
        }
    
    except Exception as e:
        logger.error(e)

        return {
            "success": False,
            "body": {}
        }