import os
import random
from shutil import copyfile



"""
PACS Dataset
4 Domains: Art-painting, Cartoon, Photo, Sketch
7 Classes: Dog, Elephant, Giraffe, Guitar, Jorse, House, Person
"""


ORIGINAL_DATA_DIR = "../data/PACS/pacs_data"
CREATE_DATA_DIR = "./data/database/image"
CREATE_SUB_DATA_DIR = "./data/example"  # For operations insert, retrieve, etc.

NUM_IMG = 30    # per class and per domain
NUM_IMG_SUB = 5 # per class and per domain

if not os.path.exists(CREATE_DATA_DIR):
    os.makedirs(CREATE_DATA_DIR)
if not os.path.exists(CREATE_SUB_DATA_DIR):
    os.makedirs(CREATE_SUB_DATA_DIR)


random.seed(0)

domain_names = sorted(os.listdir(ORIGINAL_DATA_DIR))
class_names = sorted(os.listdir(os.path.join(ORIGINAL_DATA_DIR, domain_names[0])))

for domain in domain_names:
    for class_ in class_names:
        all_data = sorted(os.listdir(os.path.join(ORIGINAL_DATA_DIR, domain, class_)))
        sampled_data = random.sample(all_data, NUM_IMG + NUM_IMG_SUB)
        for i, file_name in enumerate(sampled_data):
            if i < NUM_IMG:
                copyfile(
                    os.path.join(ORIGINAL_DATA_DIR, domain, class_, file_name),
                    os.path.join(CREATE_DATA_DIR, "{}_{}_{:03d}.jpg".format(domain, class_, i)),
                )
            else:
                copyfile(
                    os.path.join(ORIGINAL_DATA_DIR, domain, class_, file_name),
                    os.path.join(CREATE_SUB_DATA_DIR, "{}_{}_{:03d}.jpg".format(domain, class_, i)),
                )
