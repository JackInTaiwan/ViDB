import io
import logging
import random
import base64
import torch
import numpy as np

from PIL import Image
from sklearn.cluster import KMeans
from sklearn.metrics import pairwise_distances_argmin_min
from torch.nn.functional import avg_pool2d

from . import register_as_operation
from variable import operation as OP

logger = logging.getLogger(__name__)



@register_as_operation(name=OP.BROWSE_BY_RANDOM)
def browse_by_random(body=None, storage_engine=None):
    num_inst = body["num_inst"]
    random_seed = body["random_seed"] if "random_seed" in body else None

    try:
        result = browse(num_inst, "random", random_seed, storage_engine)

        return {
            "success": True,
            "body": result
        }   

    except Exception as e:
        logger.error(e)

        return {
            "success": False,
            "body": {}
        }


@register_as_operation(name=OP.BROWSE_BY_CLUSTER)
def browse_by_cluster(body=None, storage_engine=None):
    num_inst = body["num_inst"]

    try:
        result = browse(num_inst, "cluster", storage_engine)

        return {
            "success": True,
            "body": result
        }   

    except Exception as e:
        logger.error(e)

        return {
            "success": False,
            "body": {}
        }


def browse(num_inst=30, mode="random", random_seed=None, storage_engine=None):
    """Browse the database

    Args:
        num_inst (int): Number of images to return
        mode ("random" or "cluster"): Return images by random selection or k-means clustering
        random_seed (str): A random seed for the random mode.
    """

    index_list = storage_engine.read_all_idx()
    total_instance_num = len(index_list)
    browse_instance_num = min(num_inst, len(index_list))
    
    if mode == "random":
        if random_seed: random.seed(random_seed)
        selected_idxs = random.sample(index_list, browse_instance_num)
            
    
    elif mode == "cluster":
        for i, index in enumerate(index_list):
            _, _, feature, _ = storage_engine.read_one(index, "features")
            feature = feature[-1]                           # (1, 2048, 7, 7)
            feature = avg_pool2d(feature, feature.size(-1)) # (1, 2048, 1, 1)
            feature = feature.view(1, -1)                   # (1, 2048)

            if i == 0:
                features = feature
            else:
                features = torch.cat((features, feature), 0)
        
        features = features.cpu().numpy()
        kmeans = KMeans(n_clusters=browse_instance_num).fit(features)
        closest_idx, _ = pairwise_distances_argmin_min(kmeans.cluster_centers_, features)
        selected_idxs = np.array(index_list)[closest_idx].tolist()

    
    _, thumbnail_bytes_imgs, _, _ = storage_engine.read_many(selected_idxs, mode="thumbnail")

    instace = {}
    
    for idx, img in zip(selected_idxs, thumbnail_bytes_imgs):
        instace[idx] = base64.b64encode(img).decode()

    return {
        "total_instance_num": total_instance_num,
        "browse_instance_num": browse_instance_num,
        "instance": instace
    }
