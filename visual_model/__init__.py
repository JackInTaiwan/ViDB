import os

from .model import (
    Resnet50,
    Vgg16,
)



MODEL = {
    "resnet50": Resnet50,
    "vgg16": Vgg16
}

### Export model
model = MODEL[os.getenv("visual_model.model")]
model = model().to(os.getenv("visual_model.device")).eval()