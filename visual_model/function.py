import os
import torchvision.transforms as transforms

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