#! /usr/bin/python3

class box(dict):
    def __init__(self):
        super().__init__()
        self.observers = []

    def __setitem__(self,key,val):
        super().__setitem__(key,val)
        for f in self.observers:
            f(key)
            
    def watch(self,watcher):
        self.observers.append(watcher)

    def watch_key(self,key,watcher):
        self.watch(lambda k: k == key and watcher())

# TODO: observe the addition and deletion of keys
# have a better system for attaching observers to individual keys
# allow for observers to unregister
# TODO: test
# TODO: comment/document
