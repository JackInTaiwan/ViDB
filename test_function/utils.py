import os
import random
import numpy as np
import torch
import torch.nn as nn
from torchvision import models
import torchvision.transforms as transforms
from torch.nn.functional import mse_loss, avg_pool2d
from PIL import Image
from tqdm import tqdm
from sklearn.cluster import KMeans
from sklearn.metrics import pairwise_distances_argmin_min



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


def extract_feature(img_dir, feat_dir, device="cuda"):
    if not os.path.exists(feat_dir):
        os.makedirs(feat_dir)
    
    img_files = sorted(os.listdir(img_dir))

    transform = transforms.Compose([
        transforms.Resize(224),
        transforms.ToTensor(),
        transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
    ])

    # model = Vgg16().to(device).eval()
    model = Resnet().to(device).eval()

    for img_file in tqdm(img_files):
        image = Image.open(os.path.join(img_dir, img_file))
        image = transform(image).to(device)
        image = image.unsqueeze(0)
        feature = model(image)
        torch.save(feature, os.path.join(feat_dir, img_file.replace("jpg", "pt")))


def browse(feat_dir, k=30, mode="random"):
    """Browse the database

    Args:
        feat_dir (str): Directory of features
        k (int): Number of images to return
        mode ("random" or "cluster"): Return images by random selection or k-means clustering
    """

    feature_files = sorted(os.listdir(feat_dir))

    if mode == "random":
        sampled_data = random.sample(feature_files, k)
        sampled_data = [data[:-3] for data in sampled_data]
        print("\n{} selected data by random sampling\n".format(k))
        print(", ".join(sampled_data))
    
    elif mode == "cluster":
        for i, feat_file in enumerate(feature_files):
            feature = torch.load(os.path.join(feat_dir, feat_file), map_location="cpu")
            feature = feature[-1]                           # (1, 2048, 7, 7)
            feature = avg_pool2d(feature, feature.size(-1)) # (1, 2048, 1, 1)
            feature = feature.reshape(1, -1)                # (1, 2048)

            if i == 0:
                features = feature
            else:
                features = torch.cat((features, feature), 0)
        
        features = features.numpy()
        kmeans = KMeans(n_clusters=k).fit(features)
        closest_idx, _ = pairwise_distances_argmin_min(kmeans.cluster_centers_, features)
        selected_data = np.array(feature_files)[closest_idx]
        selected_data = [data[:-3] for data in selected_data]
        print("\n{} selected data by k-means clustering\n".format(k))
        print(", ".join(selected_data))
    
    else:
        print("The mode of browsing have to be \'random\' or \'cluster\'.")
    return


def find_instance_by_mode(feat_dir, target_idx, k, nearest=True, mode="content", device="cuda"):
    """Query the most similar/dissimilar instances

    Args:
        feat_dir (str): Directory of features
        target_idx (int): The index of the image to be compared with
        k (int): Number of images to query
        nearest (bool): Find the most similar ones if nearest=True, else find the most dissimilar ones
        mode ("content" or "style"): The comparison metric
        device (torch.device or int): The device type ("cpu" or "cuda")
    """

    feature_files = sorted(os.listdir(feat_dir))
    target_feature = torch.load(os.path.join(feat_dir, feature_files[target_idx]), map_location=device)
    
    losses = []
    for i, feat_file in enumerate(feature_files):
        if i != target_idx:
            feature = torch.load(os.path.join(feat_dir, feat_file), map_location=device)

            if mode == "content":
                loss = content_loss(feature, target_feature)
            elif mode == "style":
                loss = style_loss(feature, target_feature)
            else:
                print("The mode of querying instances have to be \'content\' or \'style\'.")
                return
            
            losses.append((i, loss.item()))
    
    losses = sorted(losses, key=lambda tup: tup[1])
    if not nearest:
        # reverse the order
        losses = losses[::-1]
    
    selected = []
    for i in range(k):
        selected.append(feature_files[losses[i][0]][:-3])

    if nearest:
        print("\n{} images most similar to the {} of {}\n".format(k, mode, feature_files[target_idx][:-3]))
    else:
        print("\n{} images most dissimilar to the {} of {}\n".format(k, mode, feature_files[target_idx][:-3]))
    print(", ".join(selected))
    return


def find_instance_by_tag(feat_dir, target_idx, k, mode, tags, device="cuda"):
    """Query the most similar instances given tags

    Args:
        feat_dir (str): Directory of features
        target_idx (int): The index of the image to be compared with
        k (int): Number of images to query
        mode ("all" or "partial"): "all" if both content and style have to match tags, or "partial" otherwise
        tags (list): Content and/or style tags
        device (torch.device or int): The device type ("cpu" or "cuda")
    """

    feature_files = sorted(os.listdir(feat_dir))
    target_feature = torch.load(os.path.join(feat_dir, feature_files[target_idx]), map_location=device)
    
    losses = []
    ratio = 5e6 # normalize content and style losses

    for i, feat_file in enumerate(feature_files):
        if i != target_idx:
            feature = torch.load(os.path.join(feat_dir, feat_file), map_location=device)
            s = feat_file.split("_")
            content_tag = s[-2]
            style_tag = "_".join(s[:-2])

            if mode == "all":
                if content_tag in tags and style_tag in tags:
                    loss_c = content_loss(feature, target_feature)
                    loss_s = style_loss(feature, target_feature) * ratio
                    loss = (loss_c + loss_s) / 2
                    losses.append((i, loss.item()))
            
            elif mode == "partial":
                if content_tag in tags:
                    loss = content_loss(feature, target_feature)
                    losses.append((i, loss.item()))
                if style_tag in tags:
                    loss = style_loss(feature, target_feature) * ratio
                    losses.append((i, loss.item()))
            
            else:
                print("The mode of querying instances have to be \'all\' or \'partial\'.")
                return
    
    losses = sorted(losses, key=lambda tup: tup[1])
    
    selected = []
    for i in range(k):
        selected.append(feature_files[losses[i][0]][:-3])

    print("\n{} images most similar to {} given tags \'{}\' (mode \'{}\')\n".format(k, feature_files[target_idx][:-3], ", ".join(tags), mode))
    print(", ".join(selected))
    return


def find_instance_by_range(feat_dir, group_idx, k=0, mode="content", device="cuda"):
    """Query similar instances given a group of instances

    Args:
        feat_dir (str): Directory of features
        group_idx (list): The index of a group of instances
        k (int): Number of images to query
        mode ("content" or "style"): The comparison metric
        device (torch.device or int): The device type ("cpu" or "cuda")
    """

    feature_files = sorted(os.listdir(feat_dir))
    target_features = []
    for idx in group_idx:
        target_feature = torch.load(os.path.join(feat_dir, feature_files[idx]), map_location=device)
        target_features.append(target_feature)
    
    central_feature = get_central_feature(target_features, device)
    
    losses = []
    for i, feat_file in enumerate(feature_files):
        if i not in group_idx:
            feature = torch.load(os.path.join(feat_dir, feat_file), map_location=device)

            if mode == "content":
                loss = content_loss(feature, central_feature)
            elif mode == "style":
                loss = style_loss(feature, central_feature)
            else:
                print("The mode of querying instances have to be \'content\' or \'style\'.")
                return
            
            losses.append((i, loss.item()))
    
    losses = sorted(losses, key=lambda tup: tup[1])
    
    selected = []
    if k == 0:
        thre = get_average_distance(target_features, central_feature, mode)
        for loss in losses:
            if loss[1] <= thre:
                selected.append(feature_files[loss[0]][:-3])
            else:
                break
    else:
        for i in range(k):
            selected.append(feature_files[losses[i][0]][:-3])

    group_files = []
    for idx in group_idx:
        group_files.append(feature_files[idx][:-3])
    print("\n{} images similar to the {} of group \'{}\'\n".format(len(selected), mode, ", ".join(group_files)))
    print(", ".join(selected))
    return


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


def get_central_feature(target_features, device):
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
