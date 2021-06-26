import io
import os
import logging
import base64
import time

from PIL import Image
from . import register_as_operation
from variable import operation as OP
from visual_model.function import extract_feature

logger = logging.getLogger(__name__)



@register_as_operation(name=OP.INSERT_ONE_BY_PATH)
def insert_one_by_path(body=None, storage_engine=None, cache=None):
    image_path, metadata = body["image_path"], body["metadata"]

    try:
        insert_time = time.time()
        result = insert_one(image_path, metadata, storage_engine=storage_engine)

        if result["success"]:
            cache.InsertUpdate()
            return {
                "success": True,
                "body": {
                    "index": result["index"]
                }
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


@register_as_operation(name=OP.INSERT_MANY_BY_DIR)
def insert_many_by_dir(body=None, storage_engine=None, cache=None):
    image_fold_dir, metadata = body["image_fold_dir"], body["metadata"]

    try:
        if not os.path.isdir(image_fold_dir):
            raise ValueError("Invalid image_fold_dir")

        metadata = metadata or {}
        meta_file_list = metadata.keys()
        index_list = []

        insert_time = time.time()

        for filename in os.listdir(image_fold_dir):
            metadata_ = metadata[filename] if filename in meta_file_list else None
            result = insert_one(os.path.join(image_fold_dir, filename), metadata_, storage_engine=storage_engine)
            if not result["success"]:
                break
            else:
                index_list.append(result["index"])
        else:
            cache.InsertUpdate()
            return {
                "success": True,
                "body": {
                    "index_list": index_list
                }
            }

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


@register_as_operation(name=OP.INSERT_ONE_BY_BYTE)
def insert_one_by_bytes(body=None, storage_engine=None, cache=None):
    bytes, metadata = body["bytes"], body["metadata"]

    try:
        result = insert_one_byte(bytes, metadata, storage_engine=storage_engine)

        if result["success"]:
            cache.InsertUpdate()
            return {
                "success": True,
                "body": {
                    "index": result["index"]
                }
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


@register_as_operation(name=OP.INSERT_MANY_BY_BYTE)
def insert_many_by_bytes(body=None, storage_engine=None, cache=None):
    bytes_list, metadata_list = body["bytes_list"], body["metadata"]

    try:
        metadata_list = metadata_list or []
        index_list = []

        insert_time = time.time()
        for img_b, md in zip(bytes_list, metadata_list):
            result = insert_one_byte(img_b, md, storage_engine=storage_engine)
            if not result["success"]:
                break
            else:
                index_list.append(result["index"])
        else:
            cache.InsertUpdate()
            return {
                "success": True,
                "body": {
                    "index_list": index_list
                }
            }

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


def insert_one(image_path, metadata, storage_engine=None):
    img_PIL = Image.open(image_path)

    # PIL image to numpy
    compressed_img = compress(img_PIL)

    # Transform image to string and store as .txt file
    original_byte = image_to_byte(img_PIL)
    compressed_byte = image_to_byte(compressed_img)

    # Read metadata and store as .json file
    metadata = register_metadata(img_PIL.format, img_PIL.size, img_PIL.mode, metadata)

    # Extract feature and store as .pt file
    feature = extract_feature(img_PIL)
    
    result = storage_engine.create_one(original_byte, compressed_byte, feature, metadata)

    return result


def insert_one_byte(bytes, metadata, storage_engine=None):
    # decode to PIL
    # Reading image.txt to decode it as image
    original_byte = base64.b64decode(bytes)
    img_PIL = Image.open(io.BytesIO(original_byte))

    # PIL image to numpy
    compressed_img = compress(img_PIL)

    # Transform image to string and store as .txt file
    compressed_bytes = image_to_byte(compressed_img)

    # Read metadata and store as .json file
    metadata = register_metadata(img_PIL.format, img_PIL.size, img_PIL.mode, metadata)

    # Extract feature and store as .pt file
    feature = extract_feature(img_PIL)
    
    result = storage_engine.create_one(original_byte, compressed_bytes, feature, metadata)

    return result


def register_metadata(form, size, mode, md):
    # format: image type e.g.PNG, JPEG...
    # size: image shape e.g.(227,227)
    # mode: e.g. RGB, RGBA
    metadata = {}
    metadata['format'] = form
    metadata['size'] = size
    metadata['mode'] = mode
    metadata['tag_style'] = None
    metadata['tag_content'] = None

    if md is not None:
        for key in md.keys():
            metadata[key] = md[key]

    return metadata


def compress(img): 
    w, h = img.size
    compressed_ratio = 100/h
    MAX_SIZE = (int(w*compressed_ratio), 100)
    
    # creating thumbnail
    img2 = img.copy()
    img2.thumbnail(MAX_SIZE)          
    

    return img2


def image_to_byte(img):
    #img: should be a PIL image
    output = io.BytesIO()
    img.save(output, format="png")
    image_as_bytes = output.getvalue()
    
    return image_as_bytes
