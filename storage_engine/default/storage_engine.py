import uuid
import os
import json
import time
import torch
import logging
import btree as btree
from ..base import BaseStorageEngine

logger = logging.getLogger(__name__)

# tree = btree.Binary_search_tree()
# tree = btree.fill_tree(tree)
# tree.print_tree(path=True)
# tree.search(tree.root, 9)
# tree.deleteNode(tree.root, 33)
# data = btree.serialize(tree.root)
# ntree = btree.Binary_search_tree(btree.deserialize(data))
# ntree.print_tree()

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

# index = "63fdbd9a5fd24e95b021bcd8f649c07c" 
# image = b'iVBORw0KGgoAAAANSUhEUgAABoIAAAaCCAYAAAABZu+EAAAqOElEQVR42uzBAQEAAACAkP6v7ggK'
# thumbnail = b'iVBORw0KGgoAAAANSUhEUgAABoIAAAaCCAYAAAABZu+EAAAqOElEQVR42uzBAQEAAACAkP6v7ggK'
# features = []
# metadata = {'tag':None, 'file_type':'.png', 'file_name':'01'}
# st = StorageEngine()
# st.storage_dir = r'C:\Users\Asus\Documents\GitHub\ViDB\storage_engine\storage'
# st.init_storage()
# for i in range(100):
#     st.create_one(image, thumbnail, features, metadata)
# st.read_all_idx()
# st.delete_one("0079112b083242ff9b42d5fad4bc6738")
# st.read_one("08aaec672da9415ea4b1d389800e3c28")

class StorageEngine(BaseStorageEngine):
    def __init__(self):
        self.storage_dir = os.getenv("storage_engine.storage_dir")


    def init_storage(self):
        # Create storage folder
        if not os.path.exists(self.storage_dir):
            os.makedirs(self.storage_dir+"/image")
            os.makedirs(self.storage_dir+"/thumbnail")
            os.makedirs(self.storage_dir+"/metadata")
            os.makedirs(self.storage_dir+"/features")
            fd = os.open( self.storage_dir+"/storage_table.json", os.O_CREAT) 
            os.close(fd)
            fd = os.open( self.storage_dir+"/root.txt", os.O_CREAT) 
            os.close(fd)


    def create_one(self, image:str, thumbnail:str, features, metadata:json):
        if image == None:
            return 'image can\'t be NoneType'

        # generate unique index
        index = self.generate_id()
        fd = self.locate_id(index)

        try:
            # save image to...
            fp = os.path.join(self.storage_dir, "image", fd)
            f = os.open( fp +".txt", os.O_RDWR|os.O_CREAT ) 
            os.write(f, image)
            os.close(f)

            # save thumbnail to...
            fp = os.path.join(self.storage_dir, "thumbnail", fd)
            f = os.open( fp +".txt", os.O_RDWR|os.O_CREAT ) 
            os.write(f, thumbnail)
            os.close(f)

            # save features to...
            fp = os.path.join(self.storage_dir, "features", fd)
            torch.save(features, fp +".pt")

            # save metadata to...
            fp = os.path.join(self.storage_dir, "metadata", fd)
            with open(fp +".json", "x") as file:
                metadata.update({'index': index, 'c_at': self.generate_c_at()}) # update create time # time.time()
                json.dump(metadata, file)
            self.update_storage_table(fd)
        except Exception as e:
            raise e

        return 'Success, create instance:' + index


    def create_many(self, image:list, thumbnail:list, features:list, metadata:list):
        for i in range(len(image)):
            self.create_one(image[i],thumbnail[i],features[i], metadata[1])
        return str(len(image)) + ' instances insert complete'


    def read_one(self, index, mode = 'all'):
        # mode = "image|thumbnail|features|metadata"
        # smode = mode.split("|")

        # locate file directory
        try:
            fd = self.locate_id(index)
            image, thumbnail, features, metadata = None, None, None, None

            # retrieve image object as string
            if ('all' in mode) | ('image' in mode):
                fp = os.path.join(self.storage_dir, "image", fd + ".txt")
                f = os.open(fp, os.O_RDONLY)
                image = str(os.read(f, f))
                os.close(f)
            
            # retrieve thumbnail object as string
            if ('all' in mode) | ('thumbnail' in mode):
                fp = os.path.join(self.storage_dir, "thumbnail", fd + ".txt")
                f = os.open(fp, os.O_RDONLY)
                thumbnail = str(os.read(f, f))
                os.close(f)

            # retrieve features object as ...
            if ('all' in mode) | ('features' in mode):
                fp = os.path.join(self.storage_dir, "features", fd + ".pt") # TBD
                features = torch.load(fp)
                
            # retrieve metadata object as json
            if ('all' in mode) | ('metadata' in mode):
                fp = os.path.join(self.storage_dir, "metadata", fd + ".json")
                with open(fp, "r") as file:
                    metadata = json.load(file)

        except Exception as e:
            raise e

        return image, thumbnail, features, metadata # TBD: how to return independently


    def read_many(self, index:list, mode = 'all'):
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
        file = open(self.storage_dir +"/root.txt", "r")
        text = file.read()
        try:
            tree = btree.Binary_search_tree(btree.deserialize(text))
            idx_list = tree.print_tree()
            return idx_list
        except:
            return None


    def delete_one(self, index): 
        fd = self.locate_id(index)

        try:
            fp = os.path.join(self.storage_dir, "image", fd + ".txt")
            os.remove(fp)
            fp = os.path.join(self.storage_dir, "thumbnail", fd + ".txt")
            os.remove(fp)
            fp = os.path.join(self.storage_dir, "features", fd + ".pt") # TBD
            os.remove(fp)
            fp = os.path.join(self.storage_dir, "metadata", fd + ".json")
            os.remove(fp)

            with open(self.storage_dir+"/root.txt", "r+") as file:
                text = file.read()

                if text == '':
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
        '''
        target_metadata: dict
        '''

        try:
            fd = self.locate_id(index)
            fp = os.path.join(self.storage_dir, "metadata", fd + ".json")

            with open(fp, "r") as f:
                metadata = json.load(f)
                if metadata['index'] != target_metadata['index']:
                    return False # index key is immutable
                if metadata['c_at'] != target_metadata['c_at']:
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
        # f = os.open(self.storage_dir +"/root.txt", os.O_RDWR|os.O_CREAT )
        with open(self.storage_dir+"/root.txt", "r+") as file:
            text = file.read()
            if text != '':
                tree = btree.Binary_search_tree(btree.deserialize(text))
            else: 
                tree = btree.Binary_search_tree()

        # if node exist return file path
        if tree.search(tree.root, index) != None: # node existed
            return tree.search(tree.root, index).path

        '''
        當沒有資料夾，開啟一個新的，並建立table表，新增資料夾名稱為key，value初始值為0，每新增一筆資料增加一
        將資料存入資料夾，將絕對路徑存入btree

        當資料夾滿了，開啟下一個新資料夾
        重複動作

        如何判斷資料夾已滿?
        建立table表，紀錄每個folder目前有多少資料

        btree建立:
        root資料表，存入values, parent, left right child(得路徑)
        '''
        # if new node, create new file path

        # Open JSON file
        with open(self.storage_dir+"/storage_table.json", "r+") as file:
        # with open(r"C:\Users\Asus\Documents\GitHub\ViDB\storage_engine\storage\table.json", "r+") as file:            
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
            file_path = str(fd_path + '/' + index)
            tree.insert(index, file_path)

        # rewrite root file
        with open(self.storage_dir+"/root.txt", "r+") as file:
            file.seek(0)
            file.write(btree.serialize(tree.root))
        

        # mode: without hierarchial structure
        # file_path = index

        return file_path

'''index table

'folder': [folder names 0-100],
'0':['index', 'index2'...maybe100]
...
'100':[recent pointer]
index = folder+uuid
'''
