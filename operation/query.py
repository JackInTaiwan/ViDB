import base64
import logging

from . import register_as_operation
from variable import operation as OP
from visual_model.function import content_loss, style_loss, get_central_feature, get_average_distance

logger = logging.getLogger(__name__)



@register_as_operation(name=OP.QUERY_NEAREST_BY_CONTENT)
def query_nearest_by_content(body=None, storage_engine=None):
    target_index, num_inst, return_origin_size = body["target_index"], body["num_inst"], body["return_origin_size"]

    try:
        result = find_instance_by_mode(target_index, num_inst, True, "content", storage_engine, return_origin_size)

        if result:
            return {
                "success": True,
                "body": result
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


@register_as_operation(name=OP.QUERY_NEAREST_BY_STYLE)
def query_nearest_by_style(body=None, storage_engine=None):
    target_index, num_inst, return_origin_size = body["target_index"], body["num_inst"], body["return_origin_size"]

    try:
        result = find_instance_by_mode(target_index, num_inst, True, "style", storage_engine, return_origin_size)

        if result:
            return {
                "success": True,
                "body": result
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


@register_as_operation(name=OP.QUERY_FARTHEST_BY_CONTENT)
def query_farthest_by_content(body=None, storage_engine=None):
    target_index, num_inst, return_origin_size = body["target_index"], body["num_inst"], body["return_origin_size"]

    try:
        result = find_instance_by_mode(target_index, num_inst, False, "content", storage_engine, return_origin_size)

        if result:
            return {
                "success": True,
                "body": result
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


@register_as_operation(name=OP.QUERY_FARTHEST_BY_STYLE)
def query_farthest_by_style(body=None, storage_engine=None):
    target_index, num_inst, return_origin_size = body["target_index"], body["num_inst"], body["return_origin_size"]

    try:
        result = find_instance_by_mode(target_index, num_inst, False, "style", storage_engine, return_origin_size)

        if result:
            return {
                "success": True,
                "body": result
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


@register_as_operation(name=OP.QUERY_BY_TAG_ALL)
def query_by_tag_all(body=None, storage_engine=None):
    target_index, num_inst, tags, return_origin_size = body["target_index"], body["num_inst"], body["tags"], body["return_origin_size"]

    try:
        result = find_instance_by_tag(target_index, num_inst, "all", tags, storage_engine, return_origin_size)

        if result:
            return {
                "success": True,
                "body": result
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


@register_as_operation(name=OP.QUERY_BY_TAG_PARTIAL)
def query_by_tag_partial(body=None, storage_engine=None):
    target_index, num_inst, tags, return_origin_size = body["target_index"], body["num_inst"], body["tags"], body["return_origin_size"]

    try:
        result = find_instance_by_tag(target_index, num_inst, "partial", tags, storage_engine, return_origin_size)

        if result:
            return {
                "success": True,
                "body": result
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


@register_as_operation(name=OP.QUERY_RANGE_BY_CONTENT)
def query_range_by_content(body=None, storage_engine=None):
    group_index, num_inst, return_origin_size = body["group_index"], body["num_inst"], body["return_origin_size"]

    try:
        result = find_instance_by_range(group_index, num_inst, "content", storage_engine, return_origin_size)

        if result:
            return {
                "success": True,
                "body": result
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


@register_as_operation(name=OP.QUERY_RANGE_BY_STYLE)
def query_range_by_style(body=None, storage_engine=None):
    group_index, num_inst, return_origin_size = body["group_index"], body["num_inst"], body["return_origin_size"]

    try:
        result = find_instance_by_range(group_index, num_inst, "style", storage_engine, return_origin_size)

        if result:
            return {
                "success": True,
                "body": result
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


def find_instance_by_mode(target_index, num_inst, nearest=True, mode="content", storage_engine=None, return_origin_size=False):
    """Query the most similar/dissimilar instances

    Args:
        target_index (uuid): The index of the image to be compared with
        num_inst (int): Number of images to query
        nearest (bool): Find the most similar ones if nearest=True, else find the most dissimilar ones
        mode ("content" or "style"): The comparison metric
    """
    try:
        index_list = storage_engine.read_all_idx()
        
        _, _, target_feature, _ = storage_engine.read_one(target_index, 'features')
        
        losses = []
        for index in index_list:
            if index != target_index:
                _, _, feature, _ = storage_engine.read_one(index, 'features')

                if mode == "content":
                    loss = content_loss(feature, target_feature)
                elif mode == "style":
                    loss = style_loss(feature, target_feature)

                losses.append((index, loss.item()))
        
        losses = sorted(losses, key=lambda tup: tup[1])
        if not nearest:
            # reverse the order
            losses = losses[::-1]
        
        n = min(num_inst, len(losses))
        selected = []
        for i in range(n):
            selected.append(losses[i][0])

        if return_origin_size:
            img_bytes, _, _, _ = storage_engine.read_many(selected, mode ='image')
        else:
            _, img_bytes, _, _ = storage_engine.read_many(selected, mode ='thumbnail')
        
        output = {}
        
        for idx, img in zip(selected, img_bytes):
            output[idx] = base64.b64encode(img).decode()

        return output

    except:
        return None


def find_instance_by_tag(target_index, num_inst, mode, tags, storage_engine=None, return_origin_size=False):
    """Query the most similar instances given tags

    Args:
        target_index (uuid): The index of the image to be compared with
        num_inst (int): Number of images to query
        mode ("all" or "partial"): "all" if both content and style have to match tags, or "partial" otherwise
        tags (list): Content and/or style tags
    """
    try:
        index_list = storage_engine.read_all_idx()
        
        _, _, target_feature, _ = storage_engine.read_one(target_index, 'features')
        
        losses = []
        ratio = 5e6 # normalize content and style losses

        for index in index_list:
            if index != target_index:
                _, _, feature, metadata = storage_engine.read_one(index, ['features', 'metadata'])
                
                content_tag = metadata["tag_content"]
                style_tag = metadata["tag_style"]

                if mode == "all":
                    if content_tag in tags and style_tag in tags:
                        loss_c = content_loss(feature, target_feature)
                        loss_s = style_loss(feature, target_feature) * ratio
                        loss = (loss_c + loss_s) / 2
                        losses.append((index, loss.item()))
                
                elif mode == "partial":
                    if content_tag in tags:
                        loss = content_loss(feature, target_feature)
                        losses.append((index, loss.item()))
                    if style_tag in tags:
                        loss = style_loss(feature, target_feature) * ratio
                        losses.append((index, loss.item()))
        
        losses = sorted(losses, key=lambda tup: tup[1])

        n = min(num_inst, len(losses))
        selected = []
        for i in range(n):
            selected.append(losses[i][0])

        if return_origin_size:
            img_bytes, _, _, _ = storage_engine.read_many(selected, mode ='image')
        else:
            _, img_bytes, _, _ = storage_engine.read_many(selected, mode ='thumbnail')
        
        output = {}
        
        for idx, img in zip(selected, img_bytes):
            output[idx] = base64.b64encode(img).decode()

        return output
    
    except:
        return None


def find_instance_by_range(group_index, num_inst=0, mode="content", storage_engine=None, return_origin_size=False):
    """Query similar instances given a group of instances

    Args:
        group_index (list): The index of a group of instances
        num_inst (int): Number of images to query
        mode ("content" or "style"): The comparison metric
    """
    try:
        index_list = storage_engine.read_all_idx()
        
        target_features = []
        for index in group_index:
            _, _, target_feature, _ = storage_engine.read_one(index, 'features')
            target_features.append(target_feature)
        
        central_feature = get_central_feature(target_features)
        
        losses = []
        for index in index_list:
            if index not in group_index:
                _, _, feature, _ = storage_engine.read_one(index, 'features')

                if mode == "content":
                    loss = content_loss(feature, central_feature)
                elif mode == "style":
                    loss = style_loss(feature, central_feature)
                
                losses.append((index, loss.item()))
        
        losses = sorted(losses, key=lambda tup: tup[1])
        
        selected = []
        if num_inst == 0:
            thre = get_average_distance(target_features, central_feature, mode)
            for loss in losses:
                if loss[1] <= thre:
                    selected.append(loss[0])
                else:
                    break
        else:
            n = min(num_inst, len(losses))
            for i in range(n):
                selected.append(losses[i][0])

        if return_origin_size:
            img_bytes, _, _, _ = storage_engine.read_many(selected, mode ='image')
        else:
            _, img_bytes, _, _ = storage_engine.read_many(selected, mode ='thumbnail')
        
        output = {}
        
        for idx, img in zip(selected, img_bytes):
            output[idx] = base64.b64encode(img).decode()

        return output

    except:
        return None