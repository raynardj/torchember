# AUTOGENERATED! DO NOT EDIT! File to edit: nbs/01_utils.ipynb (unless otherwise specified).

__all__ = ['check_existance', 'HOME', 'EMBER', 'DATA', 'LOG', 'get_ember_list', 'unpack_meta', 'get_ember_df',
           'get_ember_record', 'emberReader', 'clean_kv', 'io_cleaner']

# Cell
import os
from pathlib import Path
import json
import pandas as pd
import numpy as np

# Cell
HOME = Path(os.environ["HOME"])
EMBER = HOME/".torchember"
DATA = EMBER/"data"
LOG = EMBER/"log"
def check_existance():
    if DATA.exists()==False:
        return False
    if LOG.exists()==False:
        return False
    else:
        return True


# Cell
def get_ember_list():
    if check_existance()== False:
        return None
    else:
        return  list(i for i in os.listdir(DATA) if i[:5]=="base_")

# Cell
def unpack_meta(fname):
    f = open(DATA/fname,"r")
    dict_ = json.loads(f.read())
    f.close()
    dict_["name"] = fname[5:-5]
    return dict_

def get_ember_df(ember_list):
    """
    list out the latest 5 tracking record metadata
    """
    if ember_list ==None: return None
    df = pd.DataFrame(list(unpack_meta(i) for i in ember_list))
    df = df.sort_values(by = "start",ascending = False)
    return df.reset_index().drop("index",axis=1)

def get_ember_record():
    ember_list = get_ember_list()
    if ember_list==None:  return {}
    ember_df = get_ember_df(ember_list)

    ember_df["latest"] = list(range(len(ember_df)))
    return ember_df.to_dict(orient="record")

# Cell
from .helper import emberTracker

class emberReader(object):
    def __init__(self, name,verbose = False):
        self.verbose = verbose
        self.name = name
        self.t = emberTracker(name)
        self.structure = self.t[f"structure_{self.name}"]
        self.base = self.t[f"base_{self.name}"]
        if self.verbose:print(self.t.log_files)

    @property
    def latest(self):
        return self.t.latest_df.to_dict(orient = "record")

    def read_file(self,filename):
        return open(self.t.log_path/filename,"r").read()

    def read_log(self,log_name):
        return "["+str(self.read_file(log_name)[1:])+"]"

    def json_df(self,log_name):
        return pd.DataFrame(json.loads(self.read_log(log_name)))

# Cell
from torch import is_tensor
def clean_kv(k,v):
    if is_tensor(v):
        return {k:v}
    else:
        rt = dict()
        if type(v)==dict:
            for vk,vv in v.items():
                rt.update(clean_kv(f"{k}.{vk}",vv))
            return rt
        elif type(v) in [list,tuple,set]:
            for i in range(len(v)):
                vv = v[i]
                rt.update(clean_kv(f"{k}.tsr{i}",vv))
            return rt
        else:
            return {}

def io_cleaner(**kwargs):
    """
    Cleaning up the tensor input/output
    to a uniformed format of k,v
    * k is the tensor name
    * v is a tensor
    The inherent idea is to break down list,tuple,set, dictionary
    ,at any level
    return dictionary
    """
    dict_clean = dict()
    for k,v in kwargs.items():
        dict_clean.update(clean_kv(k,v))
    return dict_clean
