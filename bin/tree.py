import os
from pprint import pprint

# to do
# dirs cannot have the same name


def get_level(root_node, base_level=0):
    root_node = os.path.normpath(root_node)
    root_node_list = root_node.split(os.sep)

    level = len(root_node_list) - base_level

    return level


def clean(string, operation):
    '''rstrip operation replaces all slash characters from the string
    the get_root_node operation returns the end node from path'''
    if operation == 'rstrip':
        string = string.rstrip('/')
        string = string.rstrip('\\')

    elif operation == 'get_root_node':
        string = os.path.normpath(string)
        root_node_list = string.split(os.sep)
        string = root_node_list[-1]

    return string


class Node:
    def __init__(self):
        self.name = None

        # specifies whether its a file or a dir
        self.type = None

        self.level = None
        self.position = None

        self.parent_position = None

        self.path = None


class Tree:
    def __init__(self, root_node_path):
        #Call root_node_path cleaning functions outside of tree
        self.root_node_path = os.path.abspath(root_node_path)
        self.root_node_name = clean(root_node_path, operation='get_root_node')
        self.root_node_name = clean(self.root_node_name, operation='rstrip')

        self.tree_dict = {}

        self.init_parent_node()
        self.init_node()

    def init_parent_node(self):
        # Creates the parent node
        self.tree_dict["level_0"] = [Node()]
        self.tree_dict["level_0"][0].name = self.root_node_name
        self.tree_dict["level_0"][0].type = "dir"
        self.tree_dict["level_0"][0].level = 0
        self.tree_dict["level_0"][0].position = 0
        self.tree_dict["level_0"][0].path = self.root_node_path

    def init_node(self):
        # Creates the tree structure automatically
        tree_data = os.walk(self.root_node_path)
        # pprint(list(tree_data))

        parent_node = True
        for root, dirs, files in tree_data:
            if parent_node is True:
                # get_level here returns the number of slashes
                base_level = get_level(root)
                # once the root node has been set, parent_node is set to false
                parent_node = False

            # starts from level 1
            level_count = get_level(root, base_level) + 1
            current_level = f"level_{level_count}"

            # Initiate level if it doesn't already exist
            if current_level not in self.tree_dict.keys():
                self.tree_dict[current_level] = []

            # Get parent node's position in parent's level
            if level_count > 1:
                root_node = clean(root, operation='get_root_node')
                parent_node_level = f"level_{level_count - 1}"
                # Iterating over parents in parent_node_level
                for position in range(0, len(self.tree_dict[parent_node_level])):
                    # Check if current root node matches parent node
                    if self.tree_dict[parent_node_level][position].name == root_node:
                        parent_position = position

            # Level 0 has only one node
            elif level_count == 1:
                parent_position = 0

            position = len(self.tree_dict[current_level])
            for dir_ in dirs:
                self.tree_dict[current_level].append(Node())
                self.tree_dict[current_level][position].name = dir_
                self.tree_dict[current_level][position].type = "dir"
                self.tree_dict[current_level][position].level = level_count
                self.tree_dict[current_level][position].position = position
                self.tree_dict[current_level][position].parent_position = parent_position
                self.tree_dict[current_level][position].path = os.path.join(self.tree_dict[f'level_{level_count - 1}'][parent_position].path, self.tree_dict[current_level][position].name)
                position += 1

            for file_ in files:
                self.tree_dict[current_level].append(Node())
                self.tree_dict[current_level][position].name = file_
                self.tree_dict[current_level][position].type = "file"
                self.tree_dict[current_level][position].level = level_count
                self.tree_dict[current_level][position].position = position
                self.tree_dict[current_level][position].parent_position = parent_position
                self.tree_dict[current_level][position].path = os.path.join(self.tree_dict[f'level_{level_count - 1}'][parent_position].path, self.tree_dict[current_level][position].name)
                position += 1

    def get_node(self, by='name', node_name=None, node_level=None, node_position=None):
        if by == 'name':
            for level, node_list in self.tree_dict.items():
                for node_ in node_list:
                    if node_name.lower() in node_.name.lower():
                        return node_

        elif by == 'location':
            # Get node by its level and position
            node_ = self.tree_dict[f"level_{node_level}"][node_position]
            return node_

    def get_node_path(self, node):
        parent_node = node
        node_path = os.path.abspath(self.tree_dict["level_0"][0].name)
        print(f"initial {node_path}")
        temp_path = ""

        for i in range(node.level, 0, -1):
            parent_node = self.tree_dict[f"level_{i}"][parent_node.parent_position]
            temp_path = parent_node.name + "/" + temp_path
            # print(f"appending {parent_node.name}, appended: {node_path}, levle {i}")

        node_path = os.path.join(node_path, os.path.normpath(temp_path))

        print(f"final {node_path}")

        return node_path

    # Convenience function to view tree
    def __str__(self):
        str_ = str()
        for level, node_list in self.tree_dict.items():
            str_ += f"Level: {level}\n"
            for node_ in node_list:
                str_ += f"\t{node_.name}\n"

        return str_

    # Convenience function to probe specific node data
    def get_node_data(self, node_name):
        for level, node_list in self.tree_dict.items():
            for node_ in node_list:
                if node_name.lower() in node_.name.lower():
                    str_ = f"Current level: {level}\n \
                            Node name: {node_.name}\n \
                            Node type: {node_.type}\n \
                            Node level: {node_.level}\n \
                            Node level position: {node_.position}\n \
                            Node parent position: {node_.parent_position}\n"
                    return str_

def main():
    import time
    import os

    start = time.perf_counter()

    # tree = Tree('Tests')
    os.walk('Tests')

    print("time_taken", time.perf_counter() - start)

    # print(tree)

# Tests
if __name__ == '__main__':
    main()
    # cat_node = tree.get_node(by='name', node_name='cat_window.png')
    # print(tree.get_node_path(cat_node))
    # print(fh.get_node_data('orange'))
