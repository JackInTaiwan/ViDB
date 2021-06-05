
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
        tree.insert(cur_elem)
    return tree

# tree = Binary_search_tree()
# tree = fill_tree(tree)

# tree.print_tree()