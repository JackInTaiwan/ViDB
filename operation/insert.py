import os
import uuid
import datetime
import base64
import cv2
import json
import numpy as np

from io import BytesIO
from PIL import Image

from . import register_as_operation
from variable import operation as OP

from .util.visual_model import extract_feature

from storage_engine.default.storage_engine import (
    create_one,
    create_many,
)



@register_as_operation(name=OP.INSERT_ONE_BY_PATH)
def insert_one(body=None, storage_engine=None):
    image_path, meta_data=body["image_path", "meta_data"]
    try:
        img_PIL = Image.open(image_path)

        filename = image_path.split('/')[-1].split('.')[0]
    
        #PIL image to numpy
        img = np.asarray(img_PIL)
        compressed_img = compress(img)

        
        #Transform image to string and store as .txt file
        original_str = image_to_string(img, filename)
        compressed_str = image_to_string(compressed_img, filename+'_compressed')

        # Read meta_data and store as .json file
        meta_data = register_meta_data(filename, img_PIL.format, img_PIL.size, img_PIL.mode, meta_data)

        #Extract feature and store as .pt file
        feature = extract_feature(img_PIL)
        
        create_one(original_str, compressed_str, feature, meta_data)

        return {
            "success": True,
            "body": {}
        }   

    except:
        return {
            "success": False,
            "body": {}
        }


@register_as_operation(name=OP.INSERT_MANY_BY_DIR)
def insert_many(body=None, storage_engine=None):
    image_fold_dir, meta_data = body["image_fold_dir"], body["meta_data"]

    try:
        os.path.isdir(image_fold_dir)

        if meta_data is not None:
            metaFiles = meta_data.keys()

            for filename in os.listdir(image_fold_dir):
                if filename in metaFiles:      
                    insert_one(os.path.join(image_fold_dir, filename), meta_data[filename])
                else:
                    insert_one(os.path.join(image_fold_dir, filename))
        else:
            for filename in os.listdir(image_fold_dir):
                insert_one(os.path.join(image_fold_dir, filename))

        return {
            "success": True,
            "body": {}
        }   

    except:
        return {
            "success": False,
            "body": {}
        }


def register_meta_data(form, size, mode, md):
    #format: image type e.g.PNG, JPEG...
    #size: image shape e.g.(227,227)
    #mode: e.g. RGB, RGBA
    meta_data = {}
    meta_data['format'] = form
    meta_data['size'] = size
    meta_data['mode'] = mode
    meta_data['tag_style'] = None
    meta_data['tag_content'] = None

    if md is not None:
        for key in md.keys():
            meta_data[key] = md[key]

    return meta_data


def compress(img, ratio=2): 
    hsv = cv2.cvtColor(img, cv2.COLOR_RGB2YCR_CB)
    Y_d = hsv

    #downsample
    Y_d[:,:,1] = ratio*np.round(Y_d[:,:,1]/ratio)
    Y_d[:,:,2] = ratio*np.round(Y_d[:,:,2]/ratio)

    #Discrete cosine transform
    Y_dct_freq = np.zeros_like(Y_d)
    Y_dct_show = np.zeros_like(Y_d)
    Y_d = np.float32(Y_d)

    for channel in range(Y_d.shape[-1]):
        img_dct = cv2.dct(Y_d[:, :, channel])
        Y_dct_show[:, :, channel] = cv2.idct(img_dct)
        Y_dct_freq[:, :, channel] = img_dct

    img_bgr = cv2.cvtColor(Y_dct_show, cv2.COLOR_YCrCb2BGR)

    return img_bgr


def image_to_string(img, filename):
    #img: should be a numpy
    #Run_length_encoding
    arranged = img.flatten()

    # Now RLE encoded data is written to a text file (You can check no of bytes in text file is very less than no of bytes in the image
    # THIS IS COMPRESSION WE WANTED, NOTE THAT ITS JUST COMPRESSION DUE TO RLE, YOU CAN COMPRESS IT FURTHER USING HUFFMAN CODES OR MAY BE 
    # REDUCING MORE FREQUENCY COEFFICIENTS TO ZERO)

    bitstream = get_run_length_encoding(arranged)

    # Two terms are assigned for size as well, semicolon denotes end of image to reciever
    bitstream = str(img.shape[0]) + " " + str(img.shape[1]) + " " + bitstream + ";"
    
    return bitstream


def get_run_length_encoding(image):
    i = 0
    skip = 0
    stream = []    
    bitstream = ""
    image = image.astype(int)

    while i < image.shape[0]:
        if image[i] != 0:            
            stream.append((image[i],skip))
            bitstream = bitstream + str(image[i])+ " " +str(skip)+ " "
            skip = 0
        else:
            skip = skip + 1
        i = i + 1

    return bitstream