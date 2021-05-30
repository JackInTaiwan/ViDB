import uuid
import os
import json
import time
import torch
'''
Interface data formats
images/thumbnails: string
metadata: .json/dict # TBD
features: .pt/tensor
----------------------------
Storage Formats
images/thumbnails: string as .txt
metadata: .json for hierarchial structure
features: saved as .pt/tensor
'''

CREATE_STORAGE_DIR = "../storage"
# index = "63fdbd9a5fd24e95b021bcd8f649c07c" 
# image = 'iVBORw0KGgoAAAANSUhEUgAABoIAAAaCCAYAAAABZu+EAAAqOElEQVR42uzBAQEAAACAkP6v7ggK'
# thumbnail = 'iVBORw0KGgoAAAANSUhEUgAABoIAAAaCCAYAAAABZu+EAAAqOElEQVR42uzBAQEAAACAkP6v7ggK'
# features = []
# metadata = {'tag':None, 'file_type':'.png', 'file_name':'01'}

# Create storage folder
if not os.path.exists(CREATE_STORAGE_DIR):
    os.makedirs(CREATE_STORAGE_DIR+"/image")
    os.makedirs(CREATE_STORAGE_DIR+"/thumbnail")
    os.makedirs(CREATE_STORAGE_DIR+"/metadata")
    os.makedirs(CREATE_STORAGE_DIR+"/features")
    fd = os.open( CREATE_STORAGE_DIR+"/index.json", os.O_CREAT ) 
    os.close(fd)

def create_one(image:str, thumbnail:str, features, metadata:json):
    if image == None:
        return 'image can\'t be NoneType'

    # generate unique index
    index = generate_id()
    fd = locate_id(index)

    try:
        # save image to...
        fp = os.path.join(CREATE_STORAGE_DIR, "image", fd)
        f = os.open( fp +".txt", os.O_RDWR|os.O_CREAT ) 
        os.write(f, image.encode())
        os.close(f)

        # save thumbnail to...
        fp = os.path.join(CREATE_STORAGE_DIR, "thumbnail", fd)
        f = os.open( fp +".txt", os.O_RDWR|os.O_CREAT ) 
        os.write(f, thumbnail.encode())
        os.close(f)

        # save features to...
        fp = os.path.join(CREATE_STORAGE_DIR, "features", fd)
        torch.save(features, fp +".pt")

        # save metadata to...
        fp = os.path.join(CREATE_STORAGE_DIR, "metadata", fd)
        with open(fp +".json", "x") as file:
            metadata.update({'index':index,'c_at':generate_c_at()}) # update create time # time.time()
            json.dump(metadata, file)
    except:
        raise

    return 'Success, create instance:' + index

def create_many(image:list, thumbnail:list, features:list, metadata:list):
    for i in range(len(image)):
        create_one(image[i],thumbnail[i],features[i], metadata[1])
    return str(len(image)) + ' instances insert complete'

def read_one(index, mode = 'all'):
    # mode = "image|thumbnail|features|metadata"
    # smode = mode.split("|")

    # locate file directory
    fd = locate_id(index)
    try:
        # retrieve image object as string
        if ('all' in mode) | ('image' in mode):
            fp = os.path.join(CREATE_STORAGE_DIR, "image", fd + ".txt")
            f = os.open(fp, os.O_RDONLY)
            image = str(os.read(f, f))
            os.close(f)
        
        # retrieve thumbnail object as string
        if ('all' in mode) | ('thumbnail' in mode):
            fp = os.path.join(CREATE_STORAGE_DIR, "thumbnail", fd + ".txt")
            f = os.open(fp, os.O_RDONLY)
            thumbnail = str(os.read(f, f))
            os.close(f)

        # retrieve features object as ...
        if ('all' in mode) | ('features' in mode):
            fp = os.path.join(CREATE_STORAGE_DIR, "features", fd + ".pt") # TBD
            features = torch.load(fp)
            
        # retrieve metadata object as json
        if ('all' in mode) | ('metadata' in mode):
            fp = os.path.join(CREATE_STORAGE_DIR, "metadata", fd + ".json")
            with open(fp, "r") as file:
                metadata = json.load(file)
    except:
        raise

    return image, thumbnail, features, metadata # TBD: how to return independently

def read_many(index:list, mode = 'all'):
    image = []
    thumbnail = []
    features = []
    metadata = []
    for i in index:
        img, thmbnl, ftrs, mtdt = read_one(i, mode)
        image.append(img)
        thumbnail.append(thmbnl)
        features.append(ftrs)
        metadata.append(mtdt)
    return (image, thumbnail, features, metadata,)

def delete_one(index): 
    fd = locate_id(index)
    try:
        fp = os.path.join(CREATE_STORAGE_DIR, "image", fd + ".txt")
        os.remove(fp)
        fp = os.path.join(CREATE_STORAGE_DIR, "thumbnail", fd + ".txt")
        os.remove(fp)
        fp = os.path.join(CREATE_STORAGE_DIR, "features", fd + ".pt") # TBD
        os.remove(fp)
        fp = os.path.join(CREATE_STORAGE_DIR, "metadata", fd + ".json")
        os.remove(fp)
    except:
        raise

    return 'Success, delete instance '+ index

def delete_many(index:list): # TBD: how to relocate files
    for i in index:
        delete_one(i)
    if len(index) > 100:
        storage_reconstruct()
    pass

def update_metadata(index, metadata):
    '''
    metadata: dict
    '''
    # rewrite files? TBD
    fd = locate_id(index)
    fp = os.path.join(CREATE_STORAGE_DIR, "metadata", fd + ".json")
    with open(fp, "+") as file:
        metadata = json.load(file)
        metadata.update(metadata)
        json.dump(metadata, fp)
    pass

def generate_id():
    index = uuid.uuid4().hex
    return index

def generate_c_at(): # create time
    return time.time()

def storage_reconstruct(): # TBD: how to relocate files
    pass

def locate_id(index=None): # TBD: how to relocate files
    if index == None:
        # generate unique index
        index = generate_id()

    # # Opening JSON file
    # with open(CREATE_STORAGE_DIR+"/index.json", "r+") as file:
    #     data = json.load(file)
    #     rt = -1
    #     for f in data['folder'].keys():
    #         if f.values() < 100:
    #             rt = f 
    #             break
    #     if rt == -1:
    #         # create new folder
    #         pass
    #     data.update(str(data['folder'][-1]):index)
    #     file.seek(0) # relocate the pointer
    #     json.dump(data, file)
    
    # mode: without hierarchial structure
    file_path = index

    return file_path

'''index table

'folder': [folder names 0-100],
'0':['index', 'index2'...maybe100]
...
'100':[recent pointer]
index = folder+uuid
'''
