#!/usr/bin/env python
import os.path as path
import sys
root=path.abspath(path.dirname(__file__))
sys.path.append(root)
sys.path.insert(0,path.join(root,'mongo-async-python-driver'))
sys.path.insert(0,path.join(root,'tornado'))
