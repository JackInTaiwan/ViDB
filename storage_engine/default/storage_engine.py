import uuid
import os
import json
'''
Interface data formats
images/thumbnails: string
metadata: json
features: .pt/tensor
----------------------------
Storage Formats
images/thumbnails: string
metadata: .json for hierarchial structure
features: saved as .pt/tensor
'''

CREATE_STORAGE_DIR = "../storage"
id = "63fdbd9a5fd24e95b021bcd8f649c07c"

if not os.path.exists(CREATE_STORAGE_DIR):
    os.makedirs(CREATE_STORAGE_DIR+"/image")
    os.makedirs(CREATE_STORAGE_DIR+"/thumbnail")
    os.makedirs(CREATE_STORAGE_DIR+"/metadata")
    os.makedirs(CREATE_STORAGE_DIR+"/features")
    fd = os.open( CREATE_STORAGE_DIR+"/index.json", os.O_CREAT ) 
    os.close(fd)

def create_one(image, thumbnail, features, metadata):
    if image == None:
        return 'image can\'t be NoneType'

    # generate unique id
    id = generate_id()
    fd = locate_id(id)

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
    # save features

    # save metadata to...
    fp = os.path.join(CREATE_STORAGE_DIR, "metadata", fd)
    with open(fp +".json", "r+") as file:
        json.dump(metadata, file)

    return 'Success, create instance:' + id

def create_many(image, thumbnail, features, metadata):
    for i in range(len(image)):
        create_one(image[i],thumbnail[i],features[i], metadata[1])
    return str(len(image)) + ' instances insert complete'

def read_one(id, mode = 'all'): # mode: TBD
    # locate file directory
    fd = locate_id(id)

    # retrieve image object as string
    fp = os.path.join(CREATE_STORAGE_DIR, "image", fd + ".txt")
    f = os.open(fp, os.O_RDONLY)
    image = str(os.read(f, f))

    # retrieve thumbnail object as string
    fp = os.path.join(CREATE_STORAGE_DIR, "thumbnail", fd + ".txt")
    f = os.open(fp, os.O_RDONLY)
    thumbnail = str(os.read(f, f))

    # retrieve features object as ...
    features = os.path.join(CREATE_STORAGE_DIR, "features", fd + ".pt") # TBD

    # retrieve metadata object as json
    fp = os.path.join(CREATE_STORAGE_DIR, "metadata", fd + ".json")
    metadata = json.load(fp)

    return (image, thumbnail, features, metadata,) # TBD: how to return independently

def read_many(id):
    pass

def delete_one(id):
    path = locate_id(id)
    os.remove(path)
    pass

def delete_many(id:list):
    for i in id:
        path = locate_id(id)
        os.remove(path)
    if len(id) > 100:
        storage_reconstruct()
    pass

def update_metadata(id):
    
    pass

def generate_id():
    id = uuid.uuid4().hex
    return id

def generate_c_at():
    pass

def storage_reconstruct():
    pass

def locate_id(id=None):
    if id == None:
        # generate unique id
        id = generate_id()
    # Opening JSON file
    with open(CREATE_STORAGE_DIR+"/index.json", "r+") as file:
        data = json.load(file)
        rt = -1
        for f in data['folder'].keys():
            if f.values() < 100:
                rt = f 
                break
        if rt == -1:
            
        data.update(str(data['folder'][-1]):id)
        file.seek(0) # relocate the pointer
        json.dump(data, file)
    file_path
    # mode: without hierarchial structure
    file_path = CREATE_STORAGE_DIR + '/'+id

    
    return file_path

'''
'folder': [folder names 0-100],
'0':['index', 'index2'...maybe100]
...
'100':[recent pointer]
index = folder+uuid
'''