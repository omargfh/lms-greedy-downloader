from dataclasses import dataclass
from typing import Dict, Set
import os
import json
from test import it, TestKit
import sys

@dataclass
class CanvasFile:
    name: str
    url: str

    def __str__(self):
        return json.dumps({
            "name": self.name,
            "url": self.url
        }, indent=4)

    def __hash__(self):
        return hash(self.name)

class CanvasFileTree:
    def __init__(self, root=None, name="root"):
        self.root = root if root else self
        self.is_root = lambda: root is None
        self.name = name
        self.files: Dict[CanvasFile] = set()
        self.subfolders: Set[CanvasFileTree] = dict()

    def get_dir(self, path, create=True):
        node = self.root
        while node and path and path != "":
            if node.name == path:
                return node
            else:
                path_fragment = path.split(os.sep)[0]
                tmp_node = node.subfolders.get(path_fragment)
                if not tmp_node and create:
                    tmp_node = CanvasFileTree(root=self.root, name=path_fragment)
                    node.subfolders[path_fragment] = tmp_node
                node = tmp_node
                path = path[len(path_fragment):]
        return node

    def add(self, element: any, cursor: str, dir: bool):
        if not cursor or cursor == "":
            cursor = "root"
        node = self.get_dir(cursor, create=True)
        if not node:
            raise Exception(f"Invalid path: {cursor}")
        if dir:
            node.subfolders[element.name]  = element
        else:
            node.files.add(element)

        print(self)


    def __str__(self):
        return json.dumps({
            "files": [json.loads(str(v)) for v in self.files],
            "subfolders": {k: json.loads(str(v)) for k, v in self.subfolders.items()}
        }, indent=4)

# Test the module
if __name__ == "__main__":
    tk = TestKit()
    fs = None

    @it("Create a file tree", tk)
    def test_create_file_tree():
        global fs
        fs = CanvasFileTree()
        assert fs.is_root()

    @it("Add a file to the root", tk)
    def test_add_file_to_root():
        fs.add(CanvasFile("file1", "url1"), "/", False)
        assert len(fs.files) == 1

    @it("Add a folder to the root", tk)
    def test_add_folder_to_root():
        fs.add(CanvasFileTree("folder1"), "/", True)
        assert len(fs.subfolders) == 1

    @it("Add a file to a folder", tk)
    def test_add_file_to_folder():
        fs.add(CanvasFile("file2", "url2"), "/folder1", False)
        assert len(fs.subfolders["folder1"].files) == 1

    @it("Add a folder to a folder", tk)
    def test_add_folder_to_folder():
        fs.add(CanvasFileTree("folder2"), "/folder1", True)
        assert len(fs.subfolders["folder1"].subfolders) == 1

    @it("Add a file to a folder in a folder", tk)
    def test_add_file_to_folder_in_folder():
        fs.add(CanvasFile("file3", "url3"), "/folder1/folder2", False)
        assert len(fs.subfolders["folder1"].subfolders["folder2"].files) == 1

    test_create_file_tree()
    test_add_file_to_root()
    test_add_folder_to_root()
    test_add_file_to_folder()
    test_add_folder_to_folder()
    test_add_file_to_folder_in_folder()

    tk.done()
