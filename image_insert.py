import argparse
import yaml
import sys
from PIL import Image
import os
import uuid
import datetime
import numpy as np
import cv2
from io import BytesIO
import base64
import math
import json
from test_function.utils import extract_feature
import torch
import torch.nn as nn
from torchvision import models
import torchvision.transforms as transforms
from torch.nn.functional import mse_loss, avg_pool2d


output_dir = 'output/'
if not os.path.exists(output_dir):
    os.makedirs(output_dir)


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

def ImageToString(img, filename):
    #img: should be a numpy
    #Run_length_encoding
    arranged = img.flatten()

    # Now RLE encoded data is written to a text file (You can check no of bytes in text file is very less than no of bytes in the image
    # THIS IS COMPRESSION WE WANTED, NOTE THAT ITS JUST COMPRESSION DUE TO RLE, YOU CAN COMPRESS IT FURTHER USING HUFFMAN CODES OR MAY BE 
    # REDUCING MORE FREQUENCY COEFFICIENTS TO ZERO)

    bitstream = get_run_length_encoding(arranged)

    # Two terms are assigned for size as well, semicolon denotes end of image to reciever
    bitstream = str(img.shape[0]) + " " + str(img.shape[1]) + " " + bitstream + ";"

    # Written to image.txt
    path =os.path.join(output_dir,filename+'.txt')
    file1 = open(path,"w")
    file1.write(bitstream)
    file1.close()
    
    return bitstream

def Compression(img, ratio=2):
        
    hsv = cv2.cvtColor(img, cv2.COLOR_RGB2YCR_CB)

    Y_d = hsv
    #img_bgr = cv2.cvtColor(Y_d, cv2.COLOR_YCrCb2BGR)
    #cv2.imwrite('original_image.png', np.uint8(img_bgr))
    #downsample
    Y_d[:,:,1] = ratio*np.round(Y_d[:,:,1]/ratio)
    Y_d[:,:,2] = ratio*np.round(Y_d[:,:,2]/ratio)
    #img_bgr = cv2.cvtColor(Y_d, cv2.COLOR_YCrCb2BGR)
    #cv2.imwrite('downsample_image.png', np.uint8(img_bgr))

    #Discrete cosine transform
    Y_dct_freq = np.zeros_like(Y_d)
    Y_dct_show = np.zeros_like(Y_d)
    Y_d = np.float32(Y_d)
    for channel in range(Y_d.shape[-1]):
        img_dct = cv2.dct(Y_d[:, :, channel])
        Y_dct_show[:, :, channel] = cv2.idct(img_dct)
        Y_dct_freq[:, :, channel] = img_dct

    img_bgr = cv2.cvtColor(Y_dct_show, cv2.COLOR_YCrCb2BGR)
    #cv2.imwrite('dct_image.png', np.uint8(img_bgr))

    return img_bgr

def MetaDataRegister(filename, form, size, mode, md):
    #format: image type e.g.PNG, JPEG...
    #size: image shape e.g.(227,227)
    #mode: e.g. RGB, RGBA
    metaData = {}
    metaData['format'] = form
    metaData['size'] = size
    metaData['mode'] = mode
    metaData['tag_style'] = None
    metaData['tag_content'] = None

    if md is not None:
        for key in md.keys():
            metaData[key] = md[key]

    
    ret = json.dumps(metaData)

    path = os.path.join(output_dir,filename+'_metaData'+'.json')
    file1 =open(path, 'w')
    file1.write(ret)
    file1.close()

    return metaData

class Resnet(nn.Module):
    def __init__(self):
        super(Resnet, self).__init__()
        resnet = models.resnet50(pretrained=True)
        self.layer1 = nn.Sequential(*list(resnet.children())[:-6])
        self.layer2 = nn.Sequential(*list(resnet.children())[-6:-4])
        self.layer3 = nn.Sequential(*list(resnet.children())[-4:-2])
        
        for param in self.parameters():
            param.requires_grad = False


    def forward(self, x):
        f1 = self.layer1(x)
        f2 = self.layer2(f1)
        f3 = self.layer3(f2)
        return (f1, f2, f3)

def extract_feature(img, filename, device="cuda"):
    #Input: PIL image
    transform = transforms.Compose([
        transforms.Resize(224),
        transforms.ToTensor(),
        transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
    ])

    # model = Vgg16().to(device).eval()
    model = Resnet().to(device).eval()
    image = transform(img).to(device)
    image = image.unsqueeze(0)
    feature = model(image)

    torch.save(feature, os.path.join(output_dir, filename+'_feature'+".pt"))

def InsertOne(ImagePath, metaData=None):
    try:
        img_PIL = Image.open(ImagePath)
    except:
        print("Can not open the image from "+ ImagePath)
    
    filename = ImagePath.split('/')[-1].split('.')[0]
    
    #PIL image to numpy
    img = np.asarray(img_PIL)
    compressed_img = Compression(img)

    
    #Transform image to string and store as .txt file
    original_str = ImageToString(img, filename)
    compressed_str = ImageToString(compressed_img, filename+'_compressed')
    #print(sys.getsizeof(original_str))
    #print(sys.getsizeof(compressed_str))

    # Read metaData and store as .json file
    metaData = MetaDataRegister(filename, img_PIL.format, img_PIL.size, img_PIL.mode, metaData)

    #Extract feature and store as .pt file
    extract_feature(img_PIL, filename)
    
    return 0

def InsertMany(FolderPath, metaData):
    try:
        os.path.isdir(FolderPath)
    except:
        print("The file path is not a directory.")

    if metaData is not None:
        metaFiles = metaData.keys()

        for filename in os.listdir(FolderPath):
            if filename in metaFiles:      
                InsertOne(os.path.join(FolderPath, filename), metaData[filename])
            else:
                InsertOne(os.path.join(FolderPath, filename))
    else:
        for filename in os.listdir(FolderPath):
            InsertOne(os.path.join(FolderPath, filename))

    print("----------Finish inserting.------------")

    return 0



if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--command", default="INSERT many", help="INSERT ONE/INSERT MANY", type =str)
    parser.add_argument("--imagepath", default = "data/test/images",
                        help="image path for INSERT One/Folder path for INSERT Many", type=str)
    parser.add_argument("--metadatapath", default = None,
                        help="metadata path", type =str)
                        
    args = parser.parse_args()
    
    metaData = None
    if args.metadatapath is not None:
        f = open(args.metadatapath, "r")
        metaData = json.load(f)
    
    if args.command.upper() == "INSERT ONE".upper():
        InsertOne(args.imagepath, metaData)

    elif args.command.upper() == "INSERT MANY".upper():
        InsertMany(args.imagepath, metaData)

    else:
        sys.exit("Unrecognizable Command:"+args.command)

