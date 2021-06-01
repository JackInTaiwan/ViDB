import os
import random
import numpy as np
import torch
import torch.nn as nn
import torchvision.transforms as transforms

from PIL import Image
from torchvision import models
from torch.nn.functional import mse_loss, avg_pool2d
from sklearn.cluster import KMeans
from sklearn.metrics import pairwise_distances_argmin_min



class Resnet50(nn.Module):
    def __init__(self):
        super(Resnet50, self).__init__()
        resnet = models.resnet50(pretrained=True)
        self.layer1 = nn.Sequential(*list(resnet.children())[:-6])
        self.layer2 = nn.Sequential(*list(resnet.children())[-6:-4])
        self.layer3 = nn.Sequential(*list(resnet.children())[-4:-2])
        
        for param in self.parameters():
            param.requires_grad = False


    @torch.no_grad()
    def forward(self, x):
        f1 = self.layer1(x)
        f2 = self.layer2(f1)
        f3 = self.layer3(f2)
        return (f1, f2, f3)



class Vgg16(nn.Module):
    def __init__(self):
        super(Vgg16, self).__init__()
        features = models.vgg16(pretrained=True).features
        self.to_relu_1_2 = nn.Sequential()
        self.to_relu_2_2 = nn.Sequential()
        self.to_relu_3_3 = nn.Sequential()
        self.to_relu_4_3 = nn.Sequential()

        for x in range(4):
            self.to_relu_1_2.add_module(str(x), features[x])
        for x in range(4, 9):
            self.to_relu_2_2.add_module(str(x), features[x])
        for x in range(9, 16):
            self.to_relu_3_3.add_module(str(x), features[x])
        for x in range(16, 23):
            self.to_relu_4_3.add_module(str(x), features[x])

        for param in self.parameters():
            param.requires_grad = False


    @torch.no_grad()
    def forward(self, x):
        h = self.to_relu_1_2(x)
        h_relu_1_2 = h
        h = self.to_relu_2_2(h)
        h_relu_2_2 = h
        h = self.to_relu_3_3(h)
        h_relu_3_3 = h
        h = self.to_relu_4_3(h)
        h_relu_4_3 = h
        out = (h_relu_1_2, h_relu_2_2, h_relu_3_3, h_relu_4_3)
        return out