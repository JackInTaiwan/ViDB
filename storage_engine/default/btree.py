from collections import deque 
class Node:
    def __init__(self, value=None, path=None):
        self.value = value
        self.path = path
        self.left_child = None #smaller
        self.right_child = None #greater

class Binary_search_tree:
    def __init__(self, root = None):
        self.root = root

    def insert(self, value, path):
        #判斷tree是否為空
        if self.root == None:
            self.root = Node(value, path)
        else:
            self._insert(value, path, self.root)

    def _insert(self, value, path, cur_node):
        if value < cur_node.value:
            if cur_node.left_child == None:
                cur_node.left_child = Node(value, path)
            else:
                self._insert(value, path, cur_node.left_child)

        elif value > cur_node.value:
            if cur_node.right_child == None:
                cur_node.right_child = Node(value, path)
            else:
                self._insert(value, path, cur_node.right_child)

        # value == cur_node.value
        else:
            print("This value has existed")

    def print_tree(self, path = False):
        lst = []
        if self.root!=None:
        	self._print_tree(self.root, path, lst)
        return lst

    def _print_tree(self,cur_node: Node, path, lst:list):
        if cur_node!=None:
            self._print_tree(cur_node.left_child, path, lst)
            if path:
        	    lst.append([str(cur_node.value), str(cur_node.path)])
            else:
                lst.append(str(cur_node.value))
            self._print_tree(cur_node.right_child, path, lst)

        return lst
    
    def search(self, cur_node:Node, key): # search start from tree root
        # Base Cases: root is null or key is present at root
        if cur_node is None or cur_node.value == key:
            return cur_node
        
        # Key is greater than root's key
        if cur_node.value < key:
            return self.search(cur_node.right_child,key)
    
        # Key is smaller than root's key
        return self.search(cur_node.left_child,key)
        
    def deleteNode(self, cur_node:Node, key):    
        # Base Case
        if cur_node is None:
            return cur_node
    
        # Recursive calls for ancestors of
        # node to be deleted
        if key < cur_node.value:
            cur_node.left_child = self.deleteNode(cur_node.left_child, key)
            return cur_node
    
        elif(key > cur_node.value):
            cur_node.right_child = self.deleteNode(cur_node.right_child, key)
            return cur_node
    
        # We reach here when root is the node
        # to be deleted.
        
        # If root node is a leaf node
        if cur_node.left_child is None and cur_node.right_child is None:
            return None
    
        # If one of the children is empty
        if cur_node.left_child is None:
            temp = cur_node.right_child
            cur_node = None
            return temp
    
        elif cur_node.right_child is None:
            temp = cur_node.left_child
            cur_node = None
            return temp
    
        # If both children exist
        succParent = cur_node
    
        # Find Successor
        succ = cur_node.right_child
    
        while succ.left_child != None:
            succParent = succ
            succ = succ.left_child
    
        # Delete successor.Since successor
        # is always left child of its parent
        # we can safely make successor's right
        # right child as left of its parent.
        # If there is no succ, then assign
        # succ->right to succParent->right
        if succParent != cur_node:
            succParent.left_child = succ.right_child
        else:
            succParent.right_child = succ.right_child
    
        # Copy Successor Data to root
        cur_node.value = succ.value
        cur_node.path = succ.path
    
        return cur_node


def fill_tree(tree, num_elems=10, max_int=50):
    from random import randint
    for _ in range(num_elems): #10個 value
        cur_elem = randint(0, max_int) #隨機0~50(不含50)的值
        cur_path = randint(0, max_int)
        tree.insert(cur_elem, cur_path)
    return tree

def serialize(root: Node) -> str:
    """Encodes a tree to a single string. """
    if not root:
        return '^'
    return str(root.value)+','+str(root.path) + ' ' + serialize(root.left_child) + ' ' + serialize(root.right_child)

def deserialize(data: str) -> Node:
    """Decodes your encoded data to tree. """
    data = deque(data.split(' '))
    return _deserialize(data)

def _deserialize(data):
    v = data.popleft()
    if v == '^':  
        return None
    node = Node(v.split(',')[0], v.split(',')[1]) # id(uuid), path(str)
    node.left_child = _deserialize(data)
    node.right_child = _deserialize(data)
    return node
