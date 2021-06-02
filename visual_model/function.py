import os
import torch
import torchvision.transforms as transforms
from torch.nn.functional import mse_loss

from . import model



def extract_feature(img, device=os.getenv("visual_model.device")):
    #Input: PIL image
    transform = transforms.Compose([
        transforms.Resize(224),
        transforms.ToTensor(),
        transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
    ])

    image = transform(img).to(device)
    image = image.unsqueeze(0)
    feature = model(image)

    return feature


def content_loss(f1, f2):
    return mse_loss(f1[2], f2[2])


def style_loss(f1, f2):
    f1_gram = [gram(f) for f in f1]
    f2_gram = [gram(f) for f in f2]

    loss = 0
    for i in range(len(f1)):
        loss += mse_loss(f1_gram[i], f2_gram[i])
    return loss


def gram(x):
    (b, c, h, w) = x.size()
    f = x.view(b, c, w * h)
    f_T = f.transpose(1, 2)
    G = f.bmm(f_T) / (c * h * w)
    return G


def get_central_feature(target_features, device=os.getenv("visual_model.device")):
    n_features = len(target_features)
    central_feature = []

    for feature in target_features[0]:
        central_feature.append(torch.zeros(feature.size()).to(device))
    
    for target_feature in target_features:
        for i, feature in enumerate(target_feature):
            central_feature[i] += feature
    
    for feature in central_feature:
        feature = feature / n_features
    
    return central_feature


def get_average_distance(target_features, central_feature, mode):
    n_features = len(target_features)
    average_distance = 0

    for target_feature in target_features:
        if mode == "content":
            average_distance += content_loss(target_feature, central_feature)
        elif mode == "style":
            average_distance += style_loss(target_feature, central_feature)
    
    average_distance = average_distance / n_features
    return average_distance
