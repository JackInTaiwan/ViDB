import uuid
import os
import json
import time
import torch
import logging
import glob

from ..base import BaseStorageEngine

logger = logging.getLogger(__name__)



"""
Interface data formats
images/thumbnails: string
metadata: .json/dict # TBD
features: .pt/tensor
----------------------------
Storage Formats
images/thumbnails: string as .txt
metadata: .json for hierarchial structure
features: saved as .pt/tensor
"""

# index = "63fdbd9a5fd24e95b021bcd8f649c07c" 
# image = "iVBORw0KGgoAAAANSUhEUgAABoIAAAaCCAYAAAABZu+EAAAqOElEQVR42uzBAQEAAACAkP6v7ggK"
# thumbnail = "iVBORw0KGgoAAAANSUhEUgAABoIAAAaCCAYAAAABZu+EAAAqOElEQVR42uzBAQEAAACAkP6v7ggK"
# features = []
# metadata = {"tag":None, "file_type":".png", "file_name":"01"}



class StorageEngine(BaseStorageEngine):
    KW_IMAGE = "image"
    KW_THUMBNAIL = "thumbnail"
    KW_METADATA = "metadata"
    KW_FEATURE = "features"

    SUFFIX_IMAGE = ".txt"
    SUFFIX_THUMBNAIL = ".txt"
    SUFFIX_METADATA = ".json"
    SUFFIX_FEATURE = ".pt"

    def __init__(self):
        self.storage_dir = os.getenv("storage_engine.storage_dir")


    def init_storage(self):
        # Create storage folder
        if not os.path.exists(self.storage_dir):
            os.makedirs(os.path.join(self.storage_dir, self.KW_IMAGE))
            os.makedirs(os.path.join(self.storage_dir, self.KW_THUMBNAIL))
            os.makedirs(os.path.join(self.storage_dir, self.KW_METADATA))
            os.makedirs(os.path.join(self.storage_dir, self.KW_FEATURE))
            fd = os.open(os.path.join(self.storage_dir, "index.json"), os.O_CREAT) 
            os.close(fd)


    def clean_storage(self):
        folders = [self.KW_IMAGE, self.KW_THUMBNAIL, self.KW_METADATA, self.KW_FEATURE]
        for f in folders:
            folder_path = os.path.join(self.storage_dir,f,"*")
            files = glob.glob(folder_path)
            for f in files:
                os.remove(f)
        os.remove(os.path.join(self.storage_dir, "index.json"))
        fd = os.open(os.path.join(self.storage_dir, "index.json"), os.O_CREAT) 
        os.close(fd)
        
        logger.info("Successfully clean all data.")

        return True


    def create_one(self, image:str, thumbnail:str, features, metadata:json):
        if image == None:
            logger.error("Image cannot be NoneType")
            raise ValueError("Image cannot be NoneType")

        # generate unique index
        index = self.generate_id()
        fd = self.locate_id(index)

        try:
            # save image to...
            fp = os.path.join(self.storage_dir, self.KW_IMAGE, fd)
            f = os.open(fp+self.SUFFIX_IMAGE, os.O_RDWR|os.O_CREAT) 
            os.write(f, image)
            os.close(f)

            # save thumbnail to...
            fp = os.path.join(self.storage_dir, self.KW_THUMBNAIL, fd)
            f = os.open(fp+self.SUFFIX_THUMBNAIL, os.O_RDWR|os.O_CREAT) 
            os.write(f, thumbnail)
            os.close(f)

            # save features to...
            fp = os.path.join(self.storage_dir, self.KW_FEATURE, fd)
            torch.save(features, fp+self.SUFFIX_FEATURE)

            # save metadata to...
            fp = os.path.join(self.storage_dir, self.KW_METADATA, fd)
            with open(fp+self.SUFFIX_METADATA, "x") as file:
                metadata.update({"index": index, "c_at": self.generate_c_at()}) # update create time # time.time()
                json.dump(metadata, file)
            
            logger.info("Successfully create an instance with id={}.".format(index))

            return True
                
        except Exception as e:
            raise e


    def create_many(self, image:list, thumbnail:list, features:list, metadata:list):
        for i in range(len(image)):
            self.create_one(image[i],thumbnail[i],features[i], metadata[1])
        
        logger.info("Successfully insert {} instances.".format(len(image)))

        return True


    def read_one(self, index, mode = "all"):
        # mode = "image|thumbnail|features|metadata"
        # smode = mode.split("|")

        # locate file directory
        fd = self.locate_id(index)
        try:
            image, thumbnail, features, metadata = None, None, None, None

            # retrieve image object as string
            if ("all" in mode) | ("image" in mode):
                fp = os.path.join(self.storage_dir, self.KW_IMAGE, fd + self.SUFFIX_IMAGE)
                
                with open(fp, "rb") as myfile:
                    image=myfile.read()
                """
                f = os.open(fp, os.O_RDONLY)
                image = str(os.read(f, f))
                os.close(f)
                """
                
            
            # retrieve thumbnail object as string
            if ("all" in mode) | ("thumbnail" in mode):
                fp = os.path.join(self.storage_dir, self.KW_THUMBNAIL, fd + self.SUFFIX_THUMBNAIL)
                
                with open(fp, "rb") as myfile:
                    thumbnail=myfile.read()
                """
                f = os.open(fp, os.O_RDONLY)
                thumbnail = str(os.read(f, f))
                os.close(f)
                """
                

            # retrieve features object as ...
            if ("all" in mode) | ("features" in mode):
                fp = os.path.join(self.storage_dir, self.KW_FEATURE, fd + self.SUFFIX_FEATURE) # TBD
                features = torch.load(fp)
                
            # retrieve metadata object as json
            if ("all" in mode) | ("metadata" in mode):
                fp = os.path.join(self.storage_dir, self.KW_METADATA, fd + self.SUFFIX_METADATA)
                with open(fp, "r") as file:
                    metadata = json.load(file)

        except Exception as e:
            raise e

        return image, thumbnail, features, metadata # TBD: how to return independently


    def read_many(self, index:list, mode = "all"):
        image = []
        thumbnail = []
        features = []
        metadata = []
        for i in index:
            img, thmbnl, ftrs, mtdt = self.read_one(i, mode)
            image.append(img)
            thumbnail.append(thmbnl)
            features.append(ftrs)
            metadata.append(mtdt)
        return (image, thumbnail, features, metadata,)


    def read_all_idx(self):
        image_files = sorted(os.listdir(os.path.join(self.storage_dir, self.KW_IMAGE)))
        idx_list = [file[:-4] for file in image_files]
        return idx_list


    def delete_one(self, index): 
        fd = self.locate_id(index)

        try:
            fp = os.path.join(self.storage_dir, self.KW_IMAGE, fd + self.SUFFIX_IMAGE)
            os.remove(fp)
            fp = os.path.join(self.storage_dir, self.KW_THUMBNAIL, fd + self.SUFFIX_THUMBNAIL)
            os.remove(fp)
            fp = os.path.join(self.storage_dir, self.KW_FEATURE, fd + self.SUFFIX_FEATURE) # TBD
            os.remove(fp)
            fp = os.path.join(self.storage_dir, self.KW_METADATA, fd + self.SUFFIX_METADATA)
            os.remove(fp)

            return True

        except Exception as e:
            logger.error(e)
            return False


    def delete_many(self, index:list): # TBD: how to relocate files
        try:
            for i in index:
                result = self.delete_one(i)
                if not result:
                    # abort the transation
                    return False

            if len(index) > 100:
                self.storage_reconstruct()

            return True

        except Exception as e:
            logger.error(e)
            return False
    

    def update_one(self, index, metadata):
        result = self.update_metadata(index, metadata)
        return result
    

    def update_many(self, index:list, metadata:list):
        if (len(index) != len(metadata)):
            return False
        try:
            for index_, metadata_ in zip(index, metadata):
                result = self.update_metadata(index_, metadata_)
                if not result:
                    # abort the transation
                    return False
            return True

        except Exception as e:
            logger.error(e)
            return False


    def update_metadata(self, index:str, target_metadata:dict):
        """
        target_metadata: dict
        """
        try:
            # rewrite files? TBD
            fd = self.locate_id(index)
            fp = os.path.join(self.storage_dir, self.KW_METADATA, fd + self.SUFFIX_METADATA)

            with open(fp, "r") as f:
                metadata = json.load(f)
                metadata.update(target_metadata)

            with open(fp, "w") as f:
                json.dump(metadata, f)
        
            return True

        except Exception as e:
            logger.error(e)
            return False


    def generate_id(self):
        index = uuid.uuid4().hex
        return index


    def generate_c_at(self): # create time
        return time.time()


    def storage_reconstruct(self): # TBD: how to relocate files
        pass


    def locate_id(self, index=None): # TBD: how to relocate files
        if index == None:
            # generate unique index
            index = self.generate_id()

        # # Opening JSON file
        # with open(self.storage_dir+"/index.json", "r+") as file:
        #     data = json.load(file)
        #     rt = -1
        #     for f in data["folder"].keys():
        #         if f.values() < 100:
        #             rt = f 
        #             break
        #     if rt == -1:
        #         # create new folder
        #         pass
        #     data.update(str(data["folder"][-1]):index)
        #     file.seek(0) # relocate the pointer
        #     json.dump(data, file)
        
        # mode: without hierarchial structure
        file_path = index

        return file_path


"""index table

"folder": [folder names 0-100],
"0":["index", "index2"...maybe100]
...
"100":[recent pointer]
index = folder+uuid
"""
