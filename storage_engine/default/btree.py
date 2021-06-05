
class Node:
    def __init__(self, value=None, path=None):
        self.value = value
        self.path = path
        self.left_child = None #smaller
        self.right_child = None #greater

class Binary_search_tree:
    def __init__(self):
        self.root = None

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

    def print_tree(self):
        if self.root!=None:
        	self._print_tree(self.root)

    def _print_tree(self,cur_node):
    	if cur_node!=None:
        	self._print_tree(cur_node.left_child)
        	print(str(cur_node.value), str(cur_node.path))
        	self._print_tree(cur_node.right_child)


def fill_tree(tree, num_elems=10, max_int=50):
    from random import randint
    for _ in range(num_elems): #10個 value
        cur_elem = randint(0, max_int) #隨機0~50(不含50)的值
        cur_path = randint(0, max_int)
        tree.insert(cur_elem, cur_path)
    return tree

def serialize(self, root: TreeNode) -> str:
    """Encodes a tree to a single string. """
    if not root:
        return '^'
    return str(root.val) + ' ' + self.serialize(root.left) + ' ' + self.serialize(root.right)

def deserialize(self, data: str) -> TreeNode:
    """Decodes your encoded data to tree. """
    data = deque(data.split(' '))
    def build(data):
        v = data.popleft()
        if v == '^':  
            return None
        node = TreeNode(int(v))
        node.left = build(data)
        node.right = build(data)
        return node
    return build(data)

def serialize(self, root):
    res =[]
    queue = [root]
    while queue:
        while True and queue:
        current = queue[0]
        res.append(current)
        queue.pop(0)
        if current:
            break
        if not current:
        break
        if current.left:
        queue.append(current.left)
        else:
        queue.append(None)
        if current.right:
        queue.append(current.right)
        else:
        queue.append(None)
    s=""
    for i in range(len(res)):
        if res[i]:
        s+=str(res[i].data)
        else:
        s+="N"
        if i == len(res)-1:
        break
        s+="."
    return s
def deserialize(self, data):
    data = data.split(".")
    stack = []
    if data[0]=='N':
        return None
    root = TreeNode(int(data[0]))
    stack.append(root)
    i = 1
    current = 0
    while i <len(data):
        left= False
        if data[i] !='N':
        temp = TreeNode(int(data[i]))
        stack[current].left = temp
        stack.append(temp)
        else:
        stack[current].left = None
        i+=1
        if data[i] !='N':
        temp = TreeNode(int(data[i]))
        stack[current].right = temp
        stack.append(temp)
        else:
        stack[current].right = None
        current+=1
        i+=1
        return root
# tree = Binary_search_tree()
# tree = fill_tree(tree)

# tree.print_tree()