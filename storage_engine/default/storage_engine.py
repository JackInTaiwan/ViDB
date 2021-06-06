import uuid
import os
import json
import time
import torch
import logging
import glob
import btree as btree

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

# storage_table.json: 紀錄每個資料夾裡有幾個檔案，在create, delete時更新
# root.txt 是序列化的bstree, node之間以" "分隔, 每個Node裡存有(index, path)，以","分隔
# reallocation
    1. 當沒有資料夾，開啟一個新的，並建立storage_table.json, root.txt，新增資料夾名稱為key，value初始值為0，每新增一筆資料增加一
    2. 將資料存入或刪除後，修改storage_table.json, root.txt
    3. 當資料夾滿了(default:100)，開啟下一個新資料夾
        
"""
### Debug區 ###
# index = "63fdbd9a5fd24e95b021bcd8f649c07c" 
# image = b"iVBORw0KGgoAAAANSUhEUgAABoIAAAaCCAYAAAABZu+EAAAqOElEQVR42uzBAQEAAACAkP6v7ggK"
# thumbnail = b"iVBORw0KGgoAAAANSUhEUgAABoIAAAaCCAYAAAABZu+EAAAqOElEQVR42uzBAQEAAACAkP6v7ggK"
# features = []
# metadata = {"tag":None, "file_type":".png", "file_name":"01"}
# st = StorageEngine()
# st.storage_dir = r"C:\Users\Asus\Documents\GitHub\ViDB\storage_engine\storage"
# st.init_storage()
# for i in range(100):
#     st.create_one(image, thumbnail, features, metadata)
# st.read_all_idx()
# st.delete_one("0079112b083242ff9b42d5fad4bc6738")
# st.read_one("08aaec672da9415ea4b1d389800e3c28")



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
            fd = os.open(os.path.join(self.storage_dir, "storage_table.json"), os.O_CREAT) 
            os.close(fd)
            fd = os.open(os.path.join(self.storage_dir, "root.txt"), os.O_CREAT) 
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

            self.update_storage_table(fd)
            
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
        try:
            fd = self.locate_id(index)
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
        with open(self.storage_dir +"/root.txt", "r") as f:
            text = f.read()

        try:
            tree = btree.Binary_search_tree(btree.deserialize(text))
            idx_list = tree.print_tree()
            return idx_list
        except:
            return None


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

            with open(self.storage_dir+"/root.txt", "r+") as file:
                text = file.read()

                if text == "":
                    return False
                
                tree = btree.Binary_search_tree(btree.deserialize(text))
                tree.deleteNode(tree.root, index)
                file.seek(0)
                file.write(btree.serialize(tree.root))

            self.update_storage_table(fd, delete = True)
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
            fd = self.locate_id(index)
            fp = os.path.join(self.storage_dir, self.KW_METADATA, fd + self.SUFFIX_METADATA)

            with open(fp, "r") as f:
                metadata = json.load(f)
                if metadata["index"] != target_metadata["index"]:
                    return False # index key is immutable
                if metadata["c_at"] != target_metadata["c_at"]:
                    return False # c_at key is immutable
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


    def update_storage_table(self, file_path, delete=False):
        fd_path = file_path.split("/")[0]
        with open(self.storage_dir+"/storage_table.json", "r+") as file:
        # with open(r"C:\Users\Asus\Documents\GitHub\ViDB\storage_engine\storage\table.json", "r+") as file:            
            data = json.load(file)

            if delete:
                # updata table file
                data.update({fd_path:data[fd_path]-1})
                file.seek(0) # relocate the pointer
                json.dump(data, file)

            else:
                # updata table file
                            # updata table file
                data.update({fd_path:data[fd_path]+1})
                file.seek(0) # relocate the pointer
                json.dump(data, file)


    def locate_id(self, index=None): 
        if index == None:
            # generate unique index
            index = self.generate_id()
        
        # open root file, reconstruct bstree
        with open(self.storage_dir+"/root.txt", "r+") as file:
            text = file.read()
            if text != "":
                tree = btree.Binary_search_tree(btree.deserialize(text))
            else: 
                tree = btree.Binary_search_tree()


        # if node exist return file path
        if tree.search(tree.root, index) != None: # node existed
            return tree.search(tree.root, index).path


        # if new node, create new file path
        with open(self.storage_dir+"/storage_table.json", "r+") as file:
            fd_path = -1 # 初始值

            try:
                data = json.load(file)
                for k, v in data.items():
                    if v < 100: # 超過一百個開新資料夾
                        fd_path = k # 將要輸入的資料夾
                        break
            
            except: # create new storage_table file
                data = {}
            
            if fd_path == -1: # 代表前面資料夾已滿
                # create new folder
                # fd_path = str(uuid.uuid4().hex)
                fd_path = str(self.generate_id())
                os.makedirs(os.path.join(self.storage_dir, "image", fd_path))
                os.makedirs(os.path.join(self.storage_dir, "thumbnail", fd_path))
                os.makedirs(os.path.join(self.storage_dir, "features", fd_path))
                os.makedirs(os.path.join(self.storage_dir, "metadata", fd_path))
                data.update({fd_path:0})
                file.seek(0) # relocate the pointer
                json.dump(data, file)

        # if new node, insert into bstree
        if tree.search(tree.root, index) == None:
            file_path = str(fd_path + "/" + index)
            tree.insert(index, file_path)

        # rewrite root file
        with open(self.storage_dir+"/root.txt", "r+") as file:
            file.seek(0)
            file.write(btree.serialize(tree.root))
        

        # mode: without hierarchial structure
        # file_path = index

        return file_path


"""index table

"folder": [folder names 0-100],
"0":["index", "index2"...maybe100]
...
"100":[recent pointer]
index = folder+uuid
"""
